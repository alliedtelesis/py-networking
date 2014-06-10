import pytest
import logging
from pynetworking import Device, DeviceException
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

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


def test_save_config(dut, log_level):
    setup_dut(dut)
    config_no_vlan = """
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
"""
    config_with_vlan="""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,30,100,1000,2000,3000,3999,4000,4045,4093
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
"""
    dut.add_cmd({'cmd': 'show running-config', 'state':0, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':0, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':0, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'vlan 3999'          , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config', 'state':2, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':2, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'copy r s'           , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config', 'state':3, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':3, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':3, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'no vlan 3999'       , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show running-config', 'state':5, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':5, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'copy r s'           , 'state':5, 'action':'SET_STATE','args':[6]})
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


def test_ping1(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.ping()
    d.close()
