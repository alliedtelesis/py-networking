import pytest
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey

def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd':'show version',        'state':-1, 'action': 'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':-1, 'action': 'PRINT','args':["""
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
vlan database
 vlan 10 name "marketing vlan"
 vlan 10 state enable
 vlan 7 name admin state enable
 vlan 8-100 mtu 1200
 vlan 6,7 mtu 1000
!
end
    """]})
    dut.add_cmd({'cmd': 'show vlan all',                        'state':-1, 'action':'PRINT','args':["""
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
                                         port1.0.31(u) 
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
                         STATIC  ACTIVE  port1.0.42(u) port1.0.43(t) 
10      VLAN0030         STATIC  ACTIVE  port1.0.28(t) port1.0.29(u)
                                         port1.0.19(t) port1.0.30(t)
    """]})

def test_create(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd': 'vlan database'              , 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'              , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 20 name admin mtu 1300', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config',         'state':2, 'action':'PRINT'    ,'args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.create(20, name='admin', mtu=1300)
    assert d.vlan[20]['state'] == 'enable'
    assert d.vlan[20]['name'] == 'admin'
    assert d.vlan[20]['mtu'] == 1300
    d.close()

def test_exist(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.vlan[7]['state'] == 'enable'
    assert d.vlan[7]['name'] == 'admin'
    assert d.vlan[10]['name'] == 'marketing vlan'
    d.close()

def test_update(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd': 'vlan database'                  , 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'                  , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 20 name vlan_name mtu 1400', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config',             'state':2, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name vlan_name state enable mtu 1400
! 
    """]})
    dut.add_cmd({'cmd': 'vlan database'                    , 'state':2, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'                    , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'vlan 20 name "vlan name" mtu 1400', 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show running-config',               'state':4, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name "vlan name" state enable mtu 1400
! 
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.update(20, mtu=1400, name='vlan_name')
    assert d.vlan[20]['mtu'] == 1400
    assert d.vlan[20]['name'] == 'vlan_name'
    d.vlan.update(20, mtu=1400, name='vlan name')
    assert d.vlan[20]['mtu'] == 1400
    assert d.vlan[20]['name'] == 'vlan name'
    d.close()

def test_delete(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd': 'vlan database'                  , 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'                  , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no vlan 10',                      'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config',             'state':2, 'action':'PRINT','args':["""
!
vlan database
 vlan 20 name admin state enable mtu 1300
! 
    """]})
    dut.add_cmd({'cmd':'show vlan all',         'state':2, 'action':'PRINT','args':["""
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
"""]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.vlan[10]['state'] == 'enable'
    d.vlan.delete(10)
    with pytest.raises(KeyError):
        d.vlan[10]
    d.close()


def test_add_interface(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd': 'interface port1.0.30',      'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface port1.0.30',      'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport access vlan 10', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan all',             'state':2, 'action':'PRINT','args':["""
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
                                         port1.0.31(u) 
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
                                         port1.0.19(t) port1.0.30(u)
"""]})
    dut.add_cmd({'cmd': 'interface port1.0.30',                 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface port1.0.30',                 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'switchport mode trunk',                'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'switchport trunk allowed vlan add 10', 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show vlan all',                        'state':5, 'action':'PRINT','args':["""
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
                                         port1.0.31(u) 
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
                                         port1.0.19(t) port1.0.30(t)
"""]})
    dut.add_cmd({'cmd':'show running-config', 'state':5, 'action': 'PRINT','args':["""
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface port1.0.30
 switchport
 switchport mode trunk
!
vlan database
 vlan 10 name "marketing vlan"
 vlan 10 state enable
 vlan 7 name admin state enable
 vlan 8-100 mtu 1200
 vlan 6,7 mtu 1000
!
end
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.add_interface(10,'port1.0.30')
    assert 'port1.0.30' in d.vlan[10]['untagged']
    d.vlan.add_interface(10,'port1.0.30',tagged=True)
    assert 'port1.0.30' in d.vlan[10]['tagged']
    d.close()

def test_delete_interface(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd': 'interface port1.0.42',                 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface port1.0.42',                 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no switchport access vlan 20',         'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan all',                        'state':2, 'action':'PRINT','args':["""
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
                                         port1.0.31(u) 
                                         port1.0.32(u) port1.0.33(u) 
                                         port1.0.34(u) port1.0.35(u) 
                                         port1.0.36(u) port1.0.37(u) 
                                         port1.0.38(u) port1.0.39(u) 
                                         port1.0.40(u) port1.0.41(u) 
                                         port1.0.44(u) port1.0.45(u) 
                                         port1.0.46(u) port1.0.47(u) 
                                         port1.0.48(u) port1.0.49(u) 
                                         port1.0.50(u) port1.0.42(u)
7       VLAN0007         STATIC  ACTIVE  port1.0.28(t) port1.0.29(u)
20      "this is a long vlan name"
                         STATIC  ACTIVE  port1.0.43(t) 
10      VLAN0030         STATIC  ACTIVE  port1.0.28(t) port1.0.29(u)
                                         port1.0.19(t) port1.0.30(t)
    """]})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'port1.0.42'in d.vlan[20]['untagged']
    d.vlan.delete_interface(20,'port1.0.42')
    assert 'port1.0.42'in d.vlan[1]['untagged']
    d.close()
