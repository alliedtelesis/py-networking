import pytest
from pynetworking.servers import Telnetd,SSHd
from pynetworking.emulators import VirtualDevice
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

@pytest.fixture(scope="module")
def telnet_server(request):
    device = VirtualDevice('myhost')
    daemon = Telnetd('localhost', port, device)
#    daemon.start()
    def fin():
        daemon.exit()
        daemon.join()
    request.addfinalizer(fin)
    return port

@pytest.fixture(scope="module")
def ssh_server(request):
    device = VirtualDevice('awp',strict=False,login_type=VirtualDevice.LOGIN_TYPE_NONE)
    daemon = SSHd('127.0.0.1', 0, device)
    device.add_command('enable', '', prompt = True)
    device.add_command('configure terminal', '', prompt = True)
    device.add_command('exit', daemon.exit_command)
    def fin():
        daemon.exit()
        daemon.join()
    request.addfinalizer(fin)
    return daemon



