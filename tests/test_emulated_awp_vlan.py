import pytest
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

dut = '127.0.0.1'

def test_setup_emulated_device(ssh_server):
    ssh_server.cmds['show_version_0'] = {'cmd':'show version', 'state':0, 'action':'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]}
    ssh_server.cmds['show_running-config_0'] = {'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
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
    """]}

def test_device_vlan_create(ssh_server):
    ssh_server.cmds['create_vlan_20'] = {'cmd': 'vlan 20 name admin mtu 1300', 'state':0, 'action':'SET_STATE','args':[1]}
    ssh_server.cmds['show_running-config_1'] = {'cmd':'show running-config', 'state':1, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]}
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    d.vlan.create(20, name='admin', mtu=1300)
    assert d.vlan[20]['state'] == 'enable'
    assert d.vlan[20]['name'] == 'admin'
    assert d.vlan[20]['mtu'] == 1300
    d.close()

def test_device_vlan_exist(ssh_server):
    ssh_server.state = 0
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    assert d.vlan[7]['state'] == 'enable'
    assert d.vlan[7]['name'] == 'admin'
    d.close()

def test_device_vlan_update(ssh_server):
    ssh_server.state = 0
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    #d.vlan.update(20, name='admin', mtu=1300)
    d.vlan.create(20, name='admin', mtu=1300)
    d.close()

def test_device_vlan_delete(ssh_server):
    ssh_server.state = 0
    ssh_server.cmds['delete_vlan_10'] = {'cmd': 'no vlan 10', 'state':0, 'action':'SET_STATE','args':[2]}
    ssh_server.cmds['show_running-config_1'] = {'cmd':'show running-config', 'state':2, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]}
    d=Device(host=dut,port=ssh_server.port)
    d.open()
    assert d.vlan[10]['state'] == 'enable'
    d.vlan.delete(10)
    with pytest.raises(KeyError):
        d.vlan[10]
    d.close()

