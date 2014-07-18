import pytest
import logging
import os
import socket
from pynetworking import Device, DeviceException
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd':'show system',         'state':0, 'action':'PRINT','args':["""
Switch System Status                                   Fri Mar 21 15:45:13 2014

Board       ID  Bay   Board Name                         Rev   Serial number
--------------------------------------------------------------------------------
Base       294        x600-48Ts/XP                       B-0   G1Q79C001
Expansion  306  Bay1  AT-StackXG                         A-0   N/A
--------------------------------------------------------------------------------
RAM:  Total: 512932 kB Free: 413340 kB
Flash: 63.0MB Used: 23.7MB Available: 39.3MB
--------------------------------------------------------------------------------
Environment Status : Normal
Uptime             : 0 days 00:07:29
Bootloader version : 1.1.0


Current software   : x600-5.4.2-3.14.rel
Software version   : 5.4.2-3.14
Build date         : Wed Sep 25 12:57:26 NZST 2013

Current boot config: flash:/default.cfg (file not found)
User Configured Territory: europe

System Name
  awplus
System Contact

System Location

    """]})
    dut.add_cmd({'cmd':'show version',        'state':0, 'action':'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
 NET-SNMP SNMP agent software
 (c) 1996, 1998-2000 The Regents of the University of California.
     All rights reserved;
 (c) 2001-2003, Networks Associates Technology, Inc. All rights reserved;
 (c) 2001-2003, Cambridge Broadband Ltd. All rights reserved;
 """]})


def setup_http_server(dut, image_name):
    if (dut.mode == 'emulated'):
        myfile = open(image_name, 'w')
        myfile.write('1')
        myfile.close()


def test_open_close1(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    d.close()


def test_open_close2(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level, connection_timeout=3)
    d.open()
    sleep(4)
    d.close()


def test_open_close3(dut, log_level):
    dut.reset()
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    with pytest.raises(DeviceException) as excinfo:
        d.open()
    assert str(excinfo.value).startswith("device not supported")


def test_open_close4(dut, log_level):
    dut.reset()
    # d=Device(host='www.google.com',port=80,protocol=dut.protocol,log_level=log_level)
    # with pytest.raises(DeviceException) as excinfo:
    #     d.open()
    # assert str(excinfo.value).startswith("cannot open a ssh transport to") == True

    d=Device(host=dut.host,port=2323 ,protocol=dut.protocol,log_level=log_level)
    with pytest.raises(DeviceException) as excinfo:
        d.open()
    assert str(excinfo.value).startswith("cannot connect to") == True

    d=Device(host=dut.host,port=dut.port ,username='wronguser', protocol=dut.protocol,log_level=log_level)
    with pytest.raises(DeviceException) as excinfo:
        d.open()
    assert str(excinfo.value).startswith("authentication failed") == True


def test_ping1(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.ping()
    d.close()


def test_facts(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.facts['build_date'] == 'Wed Sep 25 12:57:26 NZST 2013'
    assert d.facts['build_name'] == 'x600-5.4.2-3.14.rel'
    assert d.facts['build_type'] == 'RELEASE'
    assert d.facts['version'] == '5.4.2'
    d.close()


def test_config(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    config = """
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
service telnet
!
service http
!
no clock timezone
!
snmp-server
!
aaa authentication enable default local
aaa authentication login default local 
!
!
stack virtual-chassis-id 1726
!
ip domain-lookup
!
no service dhcp-server
!
no ip multicast-routing
!
spanning-tree mode rstp
!
switch 1 provision x600-48
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.254/24
!
!
line con 0
line vty 0 4
!
end
"""
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':[config]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.config == config
    d.close()


def test_system(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    cmds = d.system.shell_init()
    assert cmds[0]['cmd'] == 'terminal length 0'
    d.close()


def test_save_config(dut, log_level):
    setup_dut(dut)
    config_no_vlan = """
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
service telnet
!
service http
!
no clock timezone
!
snmp-server
!
aaa authentication enable default local
aaa authentication login default local
!
stack virtual-chassis-id 1726
!
ip domain-lookup
!
no service dhcp-server
!
no ip multicast-routing
!
spanning-tree mode rstp
!
switch 1 provision x600-48
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.254/24
!
line con 0
line vty 0 4
!
end
"""
    config_with_vlan="""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
service telnet
!
service http
!
no clock timezone
!
snmp-server
!
aaa authentication enable default local
aaa authentication login default local
!
stack virtual-chassis-id 1726
!
ip domain-lookup
!
no service dhcp-server
!
no ip multicast-routing
!
spanning-tree mode rstp
!
switch 1 provision x600-48
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.254/24
!
vlan database
 vlan 3999 state enable
!
line con 0
line vty 0 4
!
end
"""
    dut.add_cmd({'cmd': 'show running-config', 'state':0, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':0, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 3999'          , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config', 'state':2, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':2, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'write'              , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config', 'state':3, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':3, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':3, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'no vlan 3999'       , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show running-config', 'state':5, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':5, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'write'              , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show running-config', 'state':6, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':6, 'action':'PRINT','args':[config_no_vlan]})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.config == d.system.get_startup_config()
    d.vlan.create(3999)
    assert d.config != d.system.get_startup_config()
    d.system.save_config()
    assert d.config == d.system.get_startup_config()
    d.vlan.delete(3999)
    assert d.config != d.system.get_startup_config()
    d.system.save_config()
    assert d.config == d.system.get_startup_config()
    d.close()


def test_ping2(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    dut.stop()
    assert not d.ping()
    d.close()


def test_software_upgrade(dut, log_level):
    dir_0 = ["""
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    dir_1 = ["""
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16664399 -rw- Jan 21 2014 09:33:19  x210-5.4.3-3.10.rel
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    image_name = 'x210-5.4.3-3.10.rel'
    false_image_name = 'x211-5.4.3-3.10.rel'
    setup_dut(dut)
    setup_http_server(dut, image_name)
    local_http_server = socket.gethostbyname(socket.getfqdn())
    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{1}'.format(socket.gethostbyname(socket.getfqdn()), image_name)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert (os.path.exists(image_name) == True)
    assert (os.path.exists(false_image_name) == False)
    with pytest.raises(KeyError) as excinfo:
        d.system.update(name=false_image_name, filename=false_image_name)
    d.system.update(name=image_name, filename=image_name)
    d.close()

    if (dut.mode == 'emulated'):
        os.remove(image_name)
