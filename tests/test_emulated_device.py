import pytest
from pynetworking import Device
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

def test_device_open_close(dut):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    d.close()

def test_device_ping(dut):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    assert d.ping()
    d.close()

def test_device_facts(dut):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    assert d.facts['build_date'] == 'Wed Sep 25 12:57:26 NZST 2013'
    assert d.facts['build_name'] == 'x600-5.4.2-3.14.rel'
    assert d.facts['build_type'] == 'RELEASE'
    assert d.facts['version'] == '5.4.2'
    d.close()

def test_device_config(dut):
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
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol)
    d.open()
    assert d.config == config
    d.close()
