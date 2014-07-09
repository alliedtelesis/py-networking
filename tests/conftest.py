import pytest
import sys
import re
import os
import shutil
from hashlib import md5
from pprint import pprint
from multiprocessing import Process, Value, Array, Manager
from ctypes import c_char_p, c_int
from time import sleep
from twisted.conch import avatar, recvline
from twisted.conch.interfaces import IConchUser, ISession
from twisted.conch.ssh import factory, keys, session
from twisted.conch.insults import insults
from twisted.cred import portal, checkers
from twisted.internet import reactor, protocol
from twisted.internet.error import ProcessTerminated,ProcessDone
from zope.interface import implements
from twisted.python import failure, log, logfile
from os.path import join

class Emulator(recvline.HistoricRecvLine):
    def __init__(self, user, parent, cmd=None):
        self.user = user
        self._hostname = "awplus"
        self.parent = parent
        self._cmd = cmd
        self._prompt = self.parent.prompt

    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.nextLine()
        self.terminal.nextLine()
        self.terminal.write(self.parent.motd)
        self.terminal.nextLine()
        self.terminal.nextLine()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write(self._hostname+self._prompt)

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        log.msg("new line "+line)
        if line == '' or re.match('\s+', line):
            self.showPrompt()
        line = line.strip()
        if line:
            log.msg('Executing shell command "{0}"'.format(line))
            cmdAndArgs = line.split()
            cmd = cmdAndArgs[0]
            args = cmdAndArgs[1:]
            func = self.getCommandFunc(cmd)
            if func:
                try:
                    func(*args)
                except Exception, e:
                    self.terminal.write("Error: %s" % e)
                    self.terminal.nextLine()
            else:
                ret = None
                for action in sorted(self.parent.cmds.values(), key=lambda k: (k['seq'],k['state'])):
                    if re.match(action['cmd'], line) and (action['state'] == -1 or action['state'] == self.parent.state):
                        if action['action'] == 'PRINT':
                            ret = action['args'][0]
                            log.msg("Printing {0}".format(ret))
                        elif action['action'] == 'SET_STATE':
                            self.parent.state = int(action['args'][0])
                            log.msg("Switching to state {0}".format(self.parent.state))
                        elif action['action'] == 'SET_PROMPT':
                            self._prompt = action['args'][0]
                            log.msg("Set prompt {0}".format(self._prompt))

                if ret:
                    log.msg("Command response")
                    log.msg(ret)
                    for l in ret.split('\n'):
                        self.terminal.write(l)
                        self.terminal.nextLine()
                self.terminal.nextLine()
                self.showPrompt()

    def do_help(self):
        for cmd in sorted(self.parent.cmds.values(), key=lambda k:(k['seq'],k['state'])):
            self.terminal.write("{0} {2} {3} {1}".format(cmd['seq'], cmd['cmd'],cmd['state'],cmd['action']))
            self.terminal.nextLine()
        self.showPrompt()

    def keystrokeReceived(self, keyID, modifier):
        if keyID == '\x1a':
            self.do_enable()
            log.msg("Received control-z")
            return
        recvline.RecvLine.keystrokeReceived(self, keyID, modifier)

    def do_enable(self):
        self._prompt = "#"
        self.terminal.nextLine()
        self.showPrompt()

    def do_conf(self,t='t'):
        if t != 't':
            return
        self._prompt = "(config)#"
        self.terminal.nextLine()
        self.showPrompt()

    def do_logout(self):
        self.terminal.nextLine()
        self.terminal.loseConnection()

    def do_state(self):
        self.terminal.write("State is {0}".format(self.parent.state))
        self.terminal.nextLine()

    def do_copy(self, src, dst):
        if (src.find('tftp://') == 0) or (dst.find('tftp://') == 0):
            tftp_dir = 'tftpdir'
            if (src.find('tftp://') == 0):
                src_path = tftp_dir + '/' + src.split('/')[-1]
                dst_path = dst
            else:
                src_path = src
                dst_path = tftp_dir + '/' + dst.split('/')[-1]
            shutil.copy2(src_path,dst_path)

        if (src.find('http://') == 0) or (src.find('tftp://') == 0):
            for action in sorted(self.parent.cmds.values(), key=lambda k: (k['seq'], k['state'])):
                if (action['cmd'].find('http://') > 0 or action['cmd'].find('tftp://') > 0) and (action['state'] == self.parent.state):
                    if action['action'] == 'SET_STATE':
                        self.parent.state = int(action['args'][0])
                    break

        self._prompt = "#"
        self.terminal.nextLine()
        self.showPrompt()


class Forwarder(recvline.HistoricRecvLine):
    def __init__(self, user, parent, cmd=None):
        self.user = user
        self.parent = parent

    def connectionMade(self):
        pass

    def lineReceived(self, line):
        pass


class SSHAvatar(avatar.ConchUser):
    implements(ISession)
    def __init__(self, username, parent):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})
        self.parent = parent

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(Emulator, self, self.parent)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, line):
        protocol.session.write("not supported")

    def closed(self):
        pass
    
    def eofReceived(self):
        pass

class SSHRealm(object):
    implements(portal.IRealm)
    def __init__(self, parent):
        self.parent = parent
    def requestAvatar(self, avatarId, mind, *interfaces):
        if IConchUser in interfaces:
            return interfaces[0], SSHAvatar(avatarId,self.parent), lambda: None
        else:
            raise NotImplementedError("No supported interfaces found.")

class DUTd(Process):
    def __init__(self,port=0, host='127.0.0.1'):
        Process.__init__(self, target = self._run)
        self._port = port
        self._sshFactory = factory.SSHFactory()
        self._sshFactory.portal = portal.Portal(SSHRealm(self))
        manager = Manager()
        self._motd = manager.Value(c_char_p, "AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26")
        self._prompt = manager.Value(c_char_p, ">")
        self._state = manager.Value(c_int, 0)
        self.cmds = manager.dict()
        self.protocol = 'ssh'
        self.host = host

        users = {'manager': 'friend'}
        if self.host == '127.0.0.1':
            self.mode = 'emulated'
            self._sshFactory.portal.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

            with open(join(os.getcwd(),'tests/id_rsa')) as privateBlobFile:
                privateBlob = privateBlobFile.read()
                self._sshFactory.privateKeys = {'ssh-rsa': keys.Key.fromString(data=privateBlob)}
            with open(join(os.getcwd(),'tests/id_rsa.pub')) as publicBlobFile:
                publicBlob = publicBlobFile.read()
                self._sshFactory.publicKeys = {'ssh-rsa': keys.Key.fromString(data=publicBlob)}

            self._listeningport = reactor.listenTCP(self._port, self._sshFactory,interface=self.host)
        else:
            self.mode = 'passthrou'
    
    @property
    def motd(self):
        return self._motd.value

    @motd.setter
    def motd(self, value):
        self._motd.value = value

    @property
    def prompt(self):
        return self._prompt.value

    @prompt.setter
    def prompt(self, value):
        self._prompt.value = value

    @property
    def state(self):
        return self._state.value

    @state.setter
    def state(self, value):
        self._state.value = int(value)

    @property
    def port(self):
        if self.host == '127.0.0.1' and self._listeningport:
            return self._listeningport.getHost().port
        return 22
    
    def reset(self):
        manager = Manager()
        self._motd.value = "AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26"
        self._state.value = 0
        for cmdid in self.cmds.keys():
            del self.cmds[cmdid]
     
    def add_cmd(self, cmd):
        cmd['seq'] = len(self.cmds)
        self.cmds[md5(str(cmd)).hexdigest()]=cmd

    def exit(self):
        if reactor.running:
            reactor.stop()

    def _run(self):
        if self.host == '127.0.0.1':
            f = logfile.LogFile("dut.log", "/tmp", rotateLength=100000,maxRotatedFiles=10)
            log.startLogging(f)
            log.msg("Listening on port {0}".format(self.port))
            reactor.run()
        else:
            while True:
                sleep(1)

    def stop(self):
        self.exit()
        self.terminate()
        sleep(0.1)


@pytest.fixture(scope="module")
def dut(request):
    host = request.config.getoption("--dut-host")
    daemon = DUTd(host=host)
    def fin():
        daemon.terminate()
        daemon.join()
    request.addfinalizer(fin)
    daemon.start()
    return daemon

def pytest_addoption(parser):
    parser.addoption("--log", default='notset', action="store", help="show log messages")
    parser.addoption("--dut-host", default='127.0.0.1', action="store", help="dut hostname or address")

@pytest.fixture(scope="module")
def log_level(request):
    log_level = request.config.getoption("--log")
    return log_level



