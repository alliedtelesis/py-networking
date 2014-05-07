# -*- coding: utf-8 -*-
import pytest
from pynetworking import Device
from time import sleep
from jinja2 import Template


show_interface_template = Template("""
Interface {{ interface }}
  Scope: both
  Link is {{ link }}, administrative state is {{ state }}
  Thrash-limiting
    Status Not Detected, Action learn-disable, Timeout 1(s)
  Hardware is {{ hardware }}, address is 0015.77ea.17e5
  index 5001 metric 1 mru 1500
  {% if hardware == 'Ethernet' -%}
  {% if link == 'UP' -%}
  current duplex full, current speed 1000, current polarity mdix
  {% endif -%}
  configured duplex auto, configured speed auto, configured polarity auto
  {% endif -%}
  <UP,BROADCAST,RUNNING,MULTICAST>
  SNMP link-status traps: Disabled
    input packets 3082, bytes 327520, dropped 0, multicast packets 466
    output packets 656, bytes 176318, multicast packets 252 broadcast packets 4
  Time since last state change: 0 days 00:08:18
""")

def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd':'show version', 'state':-1, 'action':'PRINT','args':["""

AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})
    dut.add_cmd({'cmd':'show running-config', 'state':0, 'action':'PRINT','args':["""
!
interface port0.0.1-0.0.10
 description test1
 switchport mode access
!
interface port0.0.11-0.0.50
 description "this is a test description"
 switchport mode trunk
 this is an unknown command
!
interface vlan1
 description testvlan
!
interface vlan10
 description testvlan
!
vlan database
 vlan 10 name marketing
 vlan 10 state enable
 vlan 7 name admin state enable
 vlan 8-100 mtu 1200
 vlan 6,7 mtu 1000
!
end
    """]})

def test_config(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    show_interface = ''
    for interface in range(1,51):
        env = { 
                'interface': 'port0.0.{0}'.format(interface),
                'link' : 'UP',
                'state': 'DOWN',
                'hardware' : 'Ethernet',
              } 
        show_interface += show_interface_template.render(env).encode('ascii','ignore')
    env = { 
                'interface': 'lo',
                'link' : 'UP',
                'state': 'UP',
                'hardware' : 'Loopback',
          } 
    show_interface += show_interface_template.render(env).encode('ascii','ignore')
    for vlan in [1,8, 10,7]:
        env = { 
                'interface': 'vlan{0}'.format(vlan),
                'link' : 'UP',
                'state': 'UP',
                'hardware' : 'VLAN',
               } 
        show_interface += show_interface_template.render(env).encode('ascii','ignore')
    dut.add_cmd({'cmd':'show interface', 'state':0, 'action':'PRINT','args':[show_interface]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.facts['os'] == 'awp'
    assert d.interface['0.0.10']['description'] == 'test1'
    assert d.interface['0.0.11']['description'] == 'this is a test description'
    assert d.interface['vlan10']['description'] == 'testvlan'
    d.close()

def test_enable(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    show_interface = ''
    for interface in range(1,51):
        env = { 
                'interface': 'port0.0.{0}'.format(interface),
                'link' : 'UP',
                'state': 'DOWN',
                'hardware' : 'Ethernet',
              } 
        show_interface += show_interface_template.render(env).encode('ascii','ignore')
    dut.add_cmd({'cmd': 'show interface',       'state':0, 'action':'PRINT','args':[show_interface]})
    dut.add_cmd({'cmd': 'interface port0.0.10', 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface port0.0.10', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'no shutdown',          'state':1, 'action':'SET_STATE','args':[2]})
    show_interface = ''
    for interface in range(1,51):
        env = { 
                'interface': 'port0.0.{0}'.format(interface),
                'link' : 'UP',
                'state': 'UP',
                'hardware' : 'Ethernet',
              } 
        show_interface += show_interface_template.render(env).encode('ascii','ignore')
    dut.add_cmd({'cmd': 'show interface',       'state':2, 'action':'PRINT','args':[show_interface]})
    dut.add_cmd({'cmd': 'interface port0.0.10', 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface port0.0.10', 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'shutdown',             'state':3, 'action':'SET_STATE','args':[4]})
    show_interface = ''
    for interface in range(1,51):
        env = { 
                'interface': 'port0.0.{0}'.format(interface),
                'link' : 'UP',
                'state': 'DOWN',
                'hardware' : 'Ethernet',
              } 
        show_interface += show_interface_template.render(env).encode('ascii','ignore')
    dut.add_cmd({'cmd': 'show interface',       'state':4, 'action':'PRINT','args':[show_interface]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.interface['0.0.10']['enable'] == False
    d.interface.update('0.0.10',enable=True)
    assert d.interface['0.0.10']['enable'] == True
    d.interface.update('0.0.10',enable=True)
    assert d.interface['0.0.10']['enable'] == True
    d.interface.update('0.0.10',enable=False)
    assert d.interface['0.0.10']['enable'] == False
    d.close()

def test_description(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)

