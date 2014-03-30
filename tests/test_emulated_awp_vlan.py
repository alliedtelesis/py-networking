import pytest
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

dut = '127.0.0.1'

show_version_output = """
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """
show_running_config_output = """
!
interface port0.1.1
 no shutdown
 switchmode mode access
!
vlan database
 vlan 10 name marketing
 vlan 10 state enable
 vlan 7 name admin state enable
 vlan 8-100 mtu 1200
 vlan 6,7 mtu 1000
!
end
"""

@pytest.mark.current
def test_setup_emulated_device(ssh_server):
    ssh_server.cmds['show version'] = {'action':'PRINT','args':[show_version_output]}
    ssh_server.cmds['show running-config'] = {'action':'PRINT','args':[show_running_config_output]}

@pytest.mark.current
def test_device_vlan_create(ssh_server):
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    d.vlan.create(20, name='admin', mtu=1300)
    d.close()

@pytest.mark.current
def test_device_vlan_exist(ssh_server):
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    assert d.vlan[7]['state'] == 'enable'
    d.close()

@pytest.mark.current
def test_device_vlan_update(ssh_server):
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    #d.vlan.update(20, name='admin', mtu=1300)
    d.vlan.create(20, name='admin', mtu=1300)
    d.close()

@pytest.mark.current
def test_device_vlan_delete(ssh_server):
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    d.vlan.delete(10)
    d.close()

