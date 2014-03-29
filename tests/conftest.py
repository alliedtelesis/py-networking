import pytest
import sys
import re
from multiprocessing import Process, Value, Array, Manager
from ctypes import c_char_p
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
import os

class SSHProtocol(recvline.HistoricRecvLine):
    def __init__(self, user, parent, cmd=None):
        self.user = user
        self._hostname = "awplus"
        self._prompt = ">"
        self._parent = parent
        self._cmd = cmd


    def connectionMade(self):
        recvline.HistoricRecvLine.connectionMade(self)
        self.terminal.nextLine()
        self.terminal.nextLine()
        self.terminal.write(self._parent.motd)
        self.terminal.nextLine()
        self.terminal.nextLine()
        self.showPrompt()

    def showPrompt(self):
        self.terminal.write(self._hostname+self._prompt)

    def getCommandFunc(self, cmd):
        return getattr(self, 'do_' + cmd, None)

    def lineReceived(self, line):
        line = line.strip()
        if line:
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
                for cmd,action in self._parent.cmds.items():
                    if re.search(cmd,line):
                        if action['action'] == 'PRINT':
                            for l in action['args'][0].split('\n'):
                                self.terminal.write(l)
                                self.terminal.nextLine()
                        break
                self.terminal.nextLine()
                self.showPrompt()

    def do_help(self):
        for cmd in self._parent.cmds.keys():
            self.terminal.write(cmd)
        self.showPrompt()

    def do_enable(self):
        self._prompt = "#"
        self.terminal.nextLine()
        self.showPrompt()

    def do_logout(self):
        self.terminal.nextLine()
        self.terminal.loseConnection()

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
        for cmd,action in self.parent.cmds.items():
            if re.search(cmd,line):
                if action['action'] == 'PRINT':
                    protocol.session.write(action['args'][0])
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
        self._motd = manager.Value(c_char_p,"AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26")
        self.cmds = manager.dict()

        users = {'manager': 'friend'}
        self._sshFactory.portal.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**users))

        with open(join(os.getcwd(),'tests/id_rsa')) as privateBlobFile:
            privateBlob = privateBlobFile.read()
            self._sshFactory.privateKeys = {'ssh-rsa': keys.Key.fromString(data=privateBlob)}
        with open(join(os.getcwd(),'tests/id_rsa.pub')) as publicBlobFile:
            publicBlob = publicBlobFile.read()
            self._sshFactory.publicKeys = {'ssh-rsa': keys.Key.fromString(data=publicBlob)}

        self._listeningport = reactor.listenTCP(self._port, self._sshFactory,interface='127.0.0.1')
    
    @property
    def motd(self):
        return self._motd.value

    @motd.setter
    def motd(self, value):
        self._motd.value = value

    @property
    def port(self):
        if self._listeningport:
            return self._listeningport.getHost().port
        return None

    def exit(self):
        reactor.stop()

    def _run(self):
        f = logfile.LogFile("SSHd.log", "/tmp", rotateLength=100)
        log.startLogging(f)
        log.msg("Listening on port {0}".format(self.port))
        reactor.run()        

@pytest.fixture(scope="module")
def ssh_server(request):
    daemon = SSHd()
    def fin():
        daemon.terminate()
        daemon.join()
    request.addfinalizer(fin)
    daemon.start()
    return daemon


