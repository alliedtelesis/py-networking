import pytest
import sys
import re
import os
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

class SSHProtocol(recvline.HistoricRecvLine):
    def __init__(self, user, parent, cmd=None):
        self.user = user
        self._hostname = "awplus"
        self._prompt = ">"
        self.parent = parent
        self._cmd = cmd

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
                    if action['cmd']== line and (action['state'] == -1 or action['state'] == self.parent.state):
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

    def do_enable(self):
        self._prompt = "#"
        self.terminal.nextLine()
        self.showPrompt()

    def do_conf(self,t):
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


class SSHAvatar(avatar.ConchUser):
    implements(ISession)
    def __init__(self, username, parent):
        avatar.ConchUser.__init__(self)
        self.username = username
        self.channelLookup.update({'session': session.SSHSession})
        self.parent = parent

    def openShell(self, protocol):
        serverProtocol = insults.ServerProtocol(SSHProtocol, self, self.parent)
        serverProtocol.makeConnection(protocol)
        protocol.makeConnection(session.wrapProtocol(serverProtocol))

    def getPty(self, terminal, windowSize, attrs):
        return None

    def execCommand(self, protocol, line):
        ret = None
        state = 0
        for action in self.parent.cmds:
            if re.search(action['cmd'],line):
                if action['action'] == 'PRINT':
                    if action['state'] == 0 and state == 0:
                        ret = action['args'][0]
                    elif action['state'] > 0 and action['state'] == self.parent.state:
                        ret = action['args'][0]
                        state = action['state']
                if action['action'] == 'SET_STATE':
                    self.parent.state = action['args'][0]
                    log.msg("Switching to state {0}".format(self.parent.state))

        if ret:
            log.msg("Command response")
            log.msg(ret)
            protocol.session.write(ret)
        reactor.spawnProcess(protocol,'echo')

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

class SSHd(Process):
    def __init__(self,port=0):
        Process.__init__(self, target = self._run)
        self._port = port
        self._sshFactory = factory.SSHFactory()
        self._sshFactory.portal = portal.Portal(SSHRealm(self))
        manager = Manager()
        self._motd = manager.Value(c_char_p, "AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26")
        self._state = manager.Value(c_int, 0)
        self.cmds = manager.dict()
        self.protocol = 'ssh'
        self.host = '127.0.0.1'

        users = {'manager': 'friend'}
        self._sshFactory.portal.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

        with open(join(os.getcwd(),'tests/id_rsa')) as privateBlobFile:
            privateBlob = privateBlobFile.read()
            self._sshFactory.privateKeys = {'ssh-rsa': keys.Key.fromString(data=privateBlob)}
        with open(join(os.getcwd(),'tests/id_rsa.pub')) as publicBlobFile:
            publicBlob = publicBlobFile.read()
            self._sshFactory.publicKeys = {'ssh-rsa': keys.Key.fromString(data=publicBlob)}

        self._listeningport = reactor.listenTCP(self._port, self._sshFactory,interface=self.host)
    
    @property
    def motd(self):
        return self._motd.value

    @motd.setter
    def motd(self, value):
        self._motd.value = value

    @property
    def state(self):
        return self._state.value

    @state.setter
    def state(self, value):
        self._state.value = int(value)

    @property
    def port(self):
        if self._listeningport:
            return self._listeningport.getHost().port
        return None
    
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
        reactor.stop()

    def _run(self):
        f = logfile.LogFile("dut.log", "/tmp", rotateLength=100000,maxRotatedFiles=10)
        log.startLogging(f)
        log.msg("Listening on port {0}".format(self.port))
        reactor.run()        

@pytest.fixture(scope="module")
def dut(request):
    daemon = SSHd()
    def fin():
        daemon.terminate()
        daemon.join()
    request.addfinalizer(fin)
    daemon.start()
    return daemon

def pytest_addoption(parser):
    parser.addoption("--log", default='notset', action="store", help="show log messages")

@pytest.fixture(scope="module")
def log_level(request):
    log_level = request.config.getoption("--log")
    return log_level

