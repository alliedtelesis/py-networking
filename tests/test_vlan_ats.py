# -*- coding: utf-8 -*-
import pytest
from pynetworking import Device
from time import sleep
from jinja2 import Template


def setup_dut(dut):
    dut.reset()
    dut.prompt = '#'
    dut.add_cmd({'cmd':'show version', 'state':-1, 'action':'PRINT','args':["""

        Unit             SW version         Boot version         HW version      
------------------- ------------------- ------------------- ------------------- 
         1               3.0.0.44            1.0.1.07            00.01.00       

    """]})
    dut.add_cmd({'cmd':'show system', 'state':-1, 'action':'PRINT','args':["""

Unit        Type         
---- ------------------- 
 1     AT-8000S/24       


Unit     Up time     
---- --------------- 
 1     00,00:14:51   

Unit Number:   1
Serial number:  
    """]})


def test_get_vlan(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show interfaces status', 'state':0, 'action':'PRINT','args':["""

                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
1/e1     100M-Copper  Full    100   Enabled  Off  Up          Disabled On     
1/e2     100M-Copper    --      --     --     --  Down           --     --    
1/e3     100M-Copper    --      --     --     --  Down           --     --    
1/e4     100M-Copper    --      --     --     --  Down           --     --    
1/e5     100M-Copper    --      --     --     --  Down           --     --    
1/e6     100M-Copper    --      --     --     --  Down           --     --    
1/e7     100M-Copper    --      --     --     --  Down           --     --    
1/e8     100M-Copper    --      --     --     --  Down           --     --    
1/e9     100M-Copper    --      --     --     --  Down           --     --    
1/e10    100M-Copper    --      --     --     --  Down           --     --    
1/e11    100M-Copper    --      --     --     --  Down           --     --    
1/e12    100M-Copper    --      --     --     --  Down           --     --    
1/e13    100M-Copper    --      --     --     --  Down           --     --    
1/e14    100M-Copper    --      --     --     --  Down           --     --    
1/e15    100M-Copper    --      --     --     --  Down           --     --    
1/e16    100M-Copper    --      --     --     --  Down           --     --    
1/e17    100M-Copper    --      --     --     --  Down           --     --    
1/e18    100M-Copper    --      --     --     --  Down           --     --    
1/e19    100M-Copper    --      --     --     --  Down           --     --    
1/e20    100M-Copper    --      --     --     --  Down           --     --    
1/e21    100M-Copper    --      --     --     --  Down           --     --    
1/e22    100M-Copper    --      --     --     --  Down           --     --    
1/e23    100M-Copper    --      --     --     --  Down           --     --    
1/e24    100M-Copper    --      --     --     --  Down           --     --    
1/e25         --        --      --     --     --  Not Present    --     --    
1/e26         --        --      --     --     --  Not Present    --     --    
1/e27         --        --      --     --     --  Not Present    --     --    
1/e28         --        --      --     --     --  Not Present    --     --    
1/e29         --        --      --     --     --  Not Present    --     --    
1/e30         --        --      --     --     --  Not Present    --     --    
1/e31         --        --      --     --     --  Not Present    --     --    
1/e32         --        --      --     --     --  Not Present    --     --    
1/e33         --        --      --     --     --  Not Present    --     --    
1/g1     1G-Combo-C     --      --     --     --  Down           --     --    
1/g2     1G-Combo-C     --      --     --     --  Down           --     --    
1/g3          --        --      --     --     --  Not Present    --     --    
1/g4          --        --      --     --     --  Not Present    --     --    
2/e1          --        --      --     --     --  Not Present    --     --    
2/e2          --        --      --     --     --  Not Present    --     --    
2/e3          --        --      --     --     --  Not Present    --     --    
    """]})

    dut.add_cmd({'cmd':'show interfaces configuration', 'state':0, 'action':'PRINT','args':["""
                                               Flow    Admin     Back   Mdix
Port     Type         Duplex  Speed  Neg      control  State   Pressure Mode
-------- ------------ ------  -----  -------- -------  -----   -------- ----
1/e1     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e2     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e3     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e4     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e5     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e6     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e7     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e8     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e9     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e10    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e11    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e12    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e13    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e14    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e15    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e16    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e17    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e18    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e19    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e20    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e21    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e22    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e23    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e24    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e25         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e26         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e27         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e28         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e29         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e30         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e31         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e32         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e33         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e34         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e35         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e36         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e37         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e38         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e39         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e40         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e41         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e42         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e43         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e44         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e45         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e46         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e47         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e48         --      Full      --   Enabled  Off      Up      Disabled Auto
1/g1     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g2     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g3          --      Full      --   Enabled  Off      Up      Disabled Auto
1/g4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e1          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e2          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e3          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e5          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e6          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e7          --      Full      --   Enabled  Off      Up      Disabled Auto
    """]})

    dut.add_cmd({'cmd':'show interfaces description', 'state':0, 'action':'PRINT','args':["""
Port      Description
-------   -----------
1/e1
1/e2
1/e3
1/e4      singleworddescription
1/e5
1/e6
1/e7
1/e8
1/e9
1/e10
1/e11
1/e12     some_description
1/e13
1/e14
1/e15
1/e16
1/e17
1/e18
1/e19
1/e20     some description
1/e21
1/e22
1/e23
1/e24
1/e25
1/e26
1/e27
1/e28
1/e29
1/e30
1/e31
1/e32
1/e33
1/e34
1/e35
1/e36
1/e37
1/e38
1/e39
1/e40
1/e41
1/e42
1/e43
1/e44
1/e45
1/e46
1/e47
1/e48
1/g1
1/g2
1/g3
1/g4
2/e1
2/e2
2/e3
    """]})

    dut.add_cmd({'cmd':'show vlan', 'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-12,14-48),1/g(1-4),      other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
 2           2                                      permanent     Required
 10         10                                      permanent     Required
100  0123456789                   1/e13             permanent     Required
     123456789
1000       1000                                     permanent     Required
2000       2000                                     permanent     Required
3000       3000                                     permanent     Required
4000       4000                                     permanent     Required
4045       4045                                     permanent     Required
4093       4093                                     permanent     Required

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,30,100,1000,2000,3000,4000,4045,4093
exit
interface vlan 10
name "long vlan name"
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    if dut.mode == 'emulated':
        assert dict(d.vlan) == {"4045": {"untagged": [], "tagged": [], "type": "permanent", "name": "4045"},
                 "1": {"untagged": ["1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8", "1.0.9",
                                    "1.0.10", "1.0.11", "1.0.12", "1.0.14", "1.0.15", "1.0.16", "1.0.17", "1.0.18",
                                    "1.0.19", "1.0.20", "1.0.21", "1.0.22", "1.0.23", "1.0.24", "1.0.25", "1.0.26"],
                       "tagged": [], "type": "other", "name": "default_vlan"},
                 "1000": {"untagged": [], "tagged": [], "type": "permanent", "name": "1000"},
                 "2": {"untagged": [], "tagged": [], "type": "permanent", "name": "2"},
                 "2000": {"untagged": [], "tagged": [], "type": "permanent", "name": "2000"},
                 "4093": {"untagged": [], "tagged": [], "type": "permanent", "name": "4093"},
                 "3000": {"untagged": [], "tagged": [], "type": "permanent", "name": "3000"},
                 "100": {"untagged": ["1.0.13"], "tagged": [], "type": "permanent", "name": "100"},
                 "4000": {"untagged": [], "tagged": [], "type": "permanent", "name": "4000"},
                 "10": {"untagged": [], "tagged": [], "type": "permanent", "name": "long vlan name"}}
        str(d.vlan)
    else:
        assert '1' in d.vlan
        assert 'tagged' in d.vlan[1]
        assert 'untagged' in d.vlan[1]
        assert d.vlan[1]['name'] == '1'
        str(d.vlan)
    d.close()


def test_create1(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show vlan',                  'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 10',                       'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                     'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           10                                     permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',             'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'interface vlan 10',             'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface vlan 10',             'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'name "new vlan"',               'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show vlan',                     'state':4, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':4, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface vlan 10
name "new vlan"
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.create(10, name='new vlan')
    assert '10' in d.vlan
    assert d.vlan[10]['name'] == 'new vlan'
    d.close()


def test_create2(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show vlan',                  'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 10',                       'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                     'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           10                                     permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',             'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'interface vlan 10',             'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface vlan 10',             'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'name new_vlan',                 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show vlan',                     'state':4, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new_vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':4, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface vlan 10
name new_vlan
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.create(10, name='new_vlan')
    assert '10' in d.vlan
    assert d.vlan[10]['name'] == 'new_vlan'
    with pytest.raises(KeyError) as excinfo:
        d.vlan.update(30,name='does not exists')
        assert '30 vlans do not exist' in excinfo.value
    d.close()


def test_get_interface_config(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e10
switchport mode trunk
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
switchport trunk allowed vlan add 10
switchport trunk allowed vlan add 11
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface ethernet 1/e10
switchport trunk allowed vlan add 10
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.vlan._interface_config['1.0.10']['switchport mode'] == 'trunk'
    assert d.vlan._interface_config['1.0.10']['switchport trunk allowed'] == '10'
    assert d.vlan._interface_config['1.0.25']['switchport mode'] == 'trunk'
    assert d.vlan._interface_config['1.0.12']['switchport mode'] == 'trunk'
    assert d.vlan._interface_config['1.0.12']['switchport trunk allowed'] == ['10','11']
    assert d.vlan._interface_config['1.0.18']['switchport mode'] == 'trunk'
    assert d.vlan._interface_config['1.0.19']['switchport mode'] == 'trunk'
    d.close()


def test_add_interface1(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e10
switchport mode trunk
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',  'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',  'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport access vlan 10', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                 'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),      other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                          permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport access vlan 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.add_interface(10,'1.0.20')
    assert '1.0.20' in d.vlan[10]['untagged']
    assert '1.0.20' not in d.vlan[1]['untagged']
    with pytest.raises(ValueError) as excinfo:
        d.vlan.add_interface(11,'1.0.20')
        assert '{0} is not a valid vlan id' in excinfo.value
    d.close()


def test_delete_interface1(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport access vlan 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),    other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                         permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no switchport access vlan',            'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                            'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10,11,26
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert '1.0.20' in d.vlan[10]['untagged']
    assert '1.0.20' not in d.vlan[1]['untagged']
    d.vlan.delete_interface(10,'1.0.20')
    assert '1.0.20' not in d.vlan[10]['untagged']
    assert '1.0.20' in d.vlan[1]['untagged']
    with pytest.raises(ValueError) as excinfo:
        d.vlan.delete_interface(11,'1.0.20')
        assert '11 is not a valid vlan id' in excinfo.value
    with pytest.raises(ValueError) as excinfo:
        d.vlan.delete_interface(10,'1.0.19')
        assert 'interface 1.0.19 does not belong to vlan 10' in excinfo.value
    d.close()


def test_add_interface2(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e10
switchport mode trunk
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport mode trunk',                'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'switchport trunk allowed vlan add 10', 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show vlan',                            'state':3, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),      other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                          permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':3, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
switchport trunk allowed vlan add 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.add_interface(10,'1.0.20',tagged=True)
    assert '1.0.20' in d.vlan[10]['tagged']
    d.close()


def test_delete_interface2(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
switchport trunk allowed vlan add 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),    other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                         permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',               'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',               'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport trunk allowed vlan remove 10','state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                              'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),           other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10,11,26
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert '1.0.20' in d.vlan[10]['tagged']
    assert '1.0.20' in d.vlan[1]['untagged']
    d.vlan.delete_interface(10,'1.0.20')
    assert '1.0.20' not in d.vlan[10]['tagged']
    assert '1.0.20' in d.vlan[1]['untagged']
    d.close()


def test_add_interface3(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport trunk native vlan 10',      'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                            'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),      other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                          permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
switchport trunk native vlan 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.add_interface(10,'1.0.20')
    assert '1.0.20' in d.vlan[10]['untagged']
    d.close()


def test_delete_interface3(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
switchport trunk native vlan 10
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),    other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                         permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no switchport trunk native vlan',      'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                            'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10,11,26
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert '1.0.20' in d.vlan[10]['untagged']
    assert '1.0.20' not in d.vlan[1]['untagged']
    d.vlan.delete_interface(10,'1.0.20')
    assert '1.0.20' not in d.vlan[10]['untagged']
    assert '1.0.20' in d.vlan[1]['untagged']
    d.close()


def test_add_interface4(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface ethernet 1/e20
switchport mode trunk
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'show vlan',      'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e20',             'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'switchport trunk allowed vlan add 10', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                            'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-19,21-48),1/g(1-4),      other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan  1/e20                          permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config',                    'state':2, 'action':'PRINT','args':["""
vlan database
vlan 10,11,26
exit
interface ethernet 1/e20
switchport mode trunk
switchport trunk allowed vlan add 10
switchport trunk allowed vlan add 11
switchport trunk allowed vlan add 26
exit
interface range ethernet 1/e(11-12)
switchport mode trunk
exit
interface range ethernet 1/e(18-19),1/g1
switchport mode trunk
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.vlan.add_interface(10,'1.0.20',tagged=True)
    assert '1.0.20' in d.vlan[10]['tagged']
    d.close()


def test_delete(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show vlan',                     'state':0, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           new vlan                                permanent   Required

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
vlan database
vlan 10
exit
interface vlan 10
name "new vlan"
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database',                 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no vlan 10',                    'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show vlan',                     'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)
10           10                                     permanent   Required

    """]})
    dut.add_cmd({'cmd':'show vlan',                  'state':2, 'action':'PRINT','args':["""

Vlan       Name                   Ports                Type     Authorization
---- ----------------- --------------------------- ------------ -------------
 1           1         1/e(1-48),1/g(1-4),          other       Required
                       2/e(1-48),2/g(1-4),
                       3/e(1-48),3/g(1-4),
                       4/e(1-48),4/g(1-4),
                       5/e(1-48),5/g(1-4),
                       6/e(1-48),6/g(1-4),ch(1-8)

    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':2, 'action':'PRINT','args':["""
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert '10' in d.vlan
    d.vlan.delete(10)
    assert '10' not in d.vlan
    d.close()


def test_get_vlan_ids(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.vlan._get_vlan_ids('10,20,30,40,50') == [10,20,30,40,50]
    assert d.vlan._get_vlan_ids('10-15') == [10,11,12,13,14,15]
    assert d.vlan._get_vlan_ids('10-11,60,1000-1001') == [10,11,60,1000,1001]
    with pytest.raises(ValueError) as excinfo:
        d.vlan._get_vlan_ids('not_valid_range')
        assert 'not_valid_range is not a valid vlan id, range or list' in excinfo.value


