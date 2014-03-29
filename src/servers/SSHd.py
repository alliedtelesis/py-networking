# Copyright (C) 2007-2010 Samuel Abels.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
An SSH2 server.
"""
import os
import base64
import socket
import threading
import Crypto
import paramiko
from paramiko                import ServerInterface
from pynetworking.servers.Server import Server

class _ParamikoServer(ServerInterface):
    # 'data' is the output of base64.encodestring(str(key))
    data = 'AAAAB3NzaC1yc2EAAAABIwAAAIEAyO4it3fHlmGZWJaGrfeHOVY7RWO3P9M7hp' + \
           'fAu7jJ2d7eothvfeuoRFtJwhUmZDluRdFyhFY/hFAh76PJKGAusIqIQKlkJxMC' + \
           'KDqIexkgHAfID/6mqvmnSJf0b5W8v5h2pI/stOSwTQ+pxVhwJ9ctYDhRSlF0iT' + \
           'UWT10hcuO4Ks8='
    good_pub_key = paramiko.RSAKey(data = base64.decodestring(data))

    def __init__(self):
        self.event = threading.Event()
        self.command = None
        self.requested_action = None

        # Since each server is created in it's own thread, we must
        # re-initialize the random number generator to make sure that
        # child threads have no way of guessing the numbers of the parent.
        # If we don't, PyCrypto generates an error message for security
        # reasons.
        try:
            Crypto.Random.atfork()
        except AttributeError:
            # pycrypto versions that have no "Random" module also do not
            # detect the missing atfork() call, so they do not raise.
            pass

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL # TODO: paramiko.AUTH_FAILED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password,publickey'

    def check_channel_shell_request(self, channel):
        self.requested_action = 'shell'
        self.event.set()
        return True

    def check_channel_pty_request(self,
                                  channel,
                                  term,
                                  width,
                                  height,
                                  pixelwidth,
                                  pixelheight,
                                  modes):
        return True

    def check_channel_exec_request(self, channel, command):
        self.requested_action = 'exec'
        self.command = command
        self.event.set()
        return True

class SSHd(Server):
    """
    A SSH2 server. Usage::

        device = VirtualDevice('myhost')
        daemon = SSHd('localhost', 1234, device)
        device.add_command('ls', 'ok', prompt = True)
        device.add_command('exit', daemon.exit_command)
        daemon.start() # Start the server.
        daemon.exit()  # Stop the server.
        daemon.join()  # Wait until it terminates.

    @keyword key: An Exscript.PrivateKey object.
    """

    def __init__(self, host, port, device, key = None):
        Server.__init__(self, host, port, device)
        if key:
            keyfile = key.get_filename()
        else:
            keyfile = os.path.expanduser('~/.ssh/id_rsa')
        self.host_key = paramiko.RSAKey(filename = keyfile)
        self.channel  = None
        self.device.echo = False

    def _shutdown_notify(self, conn):
        if self.channel:
            self.channel.send('Server is shutting down.\n')

    def _handle_connection(self, conn):
        t = paramiko.Transport(conn)
        try:
            t.load_server_moduli()
        except:
            self._dbg(1, 'Failed to load moduli, gex will be unsupported.')
            raise
        t.add_server_key(self.host_key)
        server = _ParamikoServer()
        t.start_server(server = server)

        while self.running:
            self.channel = t.accept(1)
            if self.channel is None:
                self._dbg(1, 'Client disappeared before requesting channel.')
                t.close()
                return
            self.channel.settimeout(self.timeout)
            server.event.wait(1)
            if server.event.isSet():
                if server.requested_action == 'exec':
                    response = self.device.do(server.command)
                    if response:
                        self.channel.send(response.replace('\n', '\r\n'))
                    self.channel.close()
                    server.event.clear()
                elif server.requested_action == 'shell':
                    self.channel.send(self.device.init().replace('\n', '\r\n'))
                    command = ''
                    while True:
                        self._poll_child_process()
                        if not self.running:
                            break
                        try:
                            data = None
                            data = self.channel.recv(1024)
                            if data:
                                self.channel.send(data)
                        except socket.timeout:
                            continue
                        except socket.error:
                            self.channel.close()
                            break
                        command += data.replace('\r\n', '\n').replace('\r', '\n')
                        if '\n' in command:
                            command = command.split('\n')[0]
                            if command == 'logout':
                                self.channel.close()
                                break
                            response = self.device.do(command)
                            command = ''
                            if response:
                                self.channel.send(response.replace('\n', '\r\n'))
            self._poll_child_process()
        self.channel.close()
        t.close()
