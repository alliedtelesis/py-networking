import pytest
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

def test_setup_emulated_device(dut):
    dut.cmds['show_version_0'] = {'cmd':'show version', 'state':0, 'action':'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]}
    dut.cmds['show_running-config'] = {'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
!
interface port0.1.1
 no shutdown
 switchmode mode access
!
vlan database
 vlan 10 name "marketing vlan"
 vlan 10 state enable
 vlan 7 name admin state enable
 vlan 8-100 mtu 1200
 vlan 6,7 mtu 1000
!
end
    """]}


    dut.cmds['show_vlan_all_0'] = {'cmd':'show vlan all', 'state':0, 'action':'PRINT','args':["""
VLAN ID  Name            Type    State   Member ports                   
                                         (u)-Untagged, (t)-Tagged
======= ================ ======= ======= ====================================
1       default          STATIC  ACTIVE  port1.0.1(u) port1.0.2(u) port1.0.3(u) 
                                         port1.0.4(u) port1.0.5(u) port1.0.6(u) 
                                         port1.0.7(u) port1.0.8(u) port1.0.9(u) 
                                         port1.0.10(u) port1.0.11(u) 
                                         port1.0.12(t) port1.0.13(u) 
                                         port1.0.14(u) port1.0.15(u) 
                                         port1.0.16(u) port1.0.17(u) 
                                         port1.0.18(u) port1.0.19(u) 
                                         port1.0.20(t) port1.0.21(u) 
                                         port1.0.22(u) port1.0.23(u) 
                                         port1.0.24(u) port1.0.25(u) 
                                         port1.0.26(u) port1.0.27(u) 
                                         port1.0.28(u) port1.0.29(u) 
                                         port1.0.30(u) port1.0.31(u) 
                                         port1.0.32(u) port1.0.33(u) 
                                         port1.0.34(u) port1.0.35(u) 
                                         port1.0.36(u) port1.0.37(u) 
                                         port1.0.38(u) port1.0.39(u) 
                                         port1.0.40(u) port1.0.41(u) 
                                         port1.0.44(u) port1.0.45(u) 
                                         port1.0.46(u) port1.0.47(u) 
                                         port1.0.48(u) port1.0.49(u) 
                                         port1.0.50(u) 
7       VLAN0007         STATIC  ACTIVE  port1.0.28(t) port1.0.29(u)
20      "this is a long vlan name"
                         STATIC  ACTIVE  port1.0.42(t) port1.0.43(t) 
10      VLAN0030         STATIC  ACTIVE  port1.0.28(t) port1.0.29(u)
                                         port1.0.19(t)
"""]}
def test_device_vlan_create(dut):
    dut.state = 0
    dut.cmds['create_vlan_20'] = {'cmd': 'vlan 20 name admin mtu 1300', 'state':0, 'action':'SET_STATE','args':[1]}
    dut.cmds['show_running-config_create_vlan_20'] = {'cmd':'show running-config', 'state':1, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]}
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    d.vlan.create(20, name='admin', mtu=1300)
    assert d.vlan[20]['state'] == 'enable'
    assert d.vlan[20]['name'] == 'admin'
    assert d.vlan[20]['mtu'] == 1300
    d.close()

def test_device_vlan_exist(dut):
    dut.state = 0
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    assert d.vlan[7]['state'] == 'enable'
    assert d.vlan[7]['name'] == 'admin'
    d.close()

def test_device_vlan_update(dut):
    dut.state = 0
    dut.cmds['update_vlan_20'] = {'cmd': 'vlan 20 mtu 1400', 'state':0, 'action':'SET_STATE','args':[3]}
    dut.cmds['show_running-config_update_20'] = {'cmd':'show running-config', 'state':3, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1400
! 
    """]}
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    d.vlan.update(20, mtu=1400)
    assert d.vlan[20]['mtu'] == 1400
    d.close()

def test_device_vlan_delete(dut):
    dut.state = 0
    dut.cmds['delete_vlan_10'] = {'cmd': 'no vlan 10', 'state':0, 'action':'SET_STATE','args':[2]}
    dut.cmds['show_running-config_delete_vlan_10'] = {'cmd':'show running-config', 'state':2, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]}
    dut.cmds['show_vlan_all_2'] = {'cmd':'show vlan all', 'state':2, 'action':'PRINT','args':["""
VLAN ID  Name            Type    State   Member ports                   
                                         (u)-Untagged, (t)-Tagged
======= ================ ======= ======= ====================================
1       default          STATIC  ACTIVE  port1.0.1(u) port1.0.2(u) port1.0.3(u) 
                                         port1.0.4(u) port1.0.5(u) port1.0.6(u) 
                                         port1.0.7(u) port1.0.8(u) port1.0.9(u) 
                                         port1.0.10(u) port1.0.11(u) 
                                         port1.0.12(t) port1.0.13(u) 
                                         port1.0.14(u) port1.0.15(u) 
                                         port1.0.16(u) port1.0.17(u) 
                                         port1.0.18(u) port1.0.19(u) 
                                         port1.0.20(t) port1.0.21(u) 
                                         port1.0.22(u) port1.0.23(u) 
                                         port1.0.24(u) port1.0.25(u) 
                                         port1.0.26(u) port1.0.27(u) 
                                         port1.0.28(u) port1.0.29(u) 
                                         port1.0.30(u) port1.0.31(u) 
                                         port1.0.32(u) port1.0.33(u) 
                                         port1.0.34(u) port1.0.35(u) 
                                         port1.0.36(u) port1.0.37(u) 
                                         port1.0.38(u) port1.0.39(u) 
                                         port1.0.40(u) port1.0.41(u) 
                                         port1.0.44(u) port1.0.45(u) 
                                         port1.0.46(u) port1.0.47(u) 
                                         port1.0.48(u) port1.0.49(u) 
                                         port1.0.50(u) 
20      "this is a long vlan name"
                         STATIC  ACTIVE  port1.0.42(t) port1.0.43(t) 
"""]}
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    assert d.vlan[10]['state'] == 'enable'
    d.vlan.delete(10)
    with pytest.raises(KeyError):
        d.vlan[10]
    d.close()

