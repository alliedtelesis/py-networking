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


def setup_test_release_license(dut, cert_file):
    if (os.path.exists(cert_file) == False):
        myfile = open(cert_file, 'w')
        myfile.write('1')
        myfile.close()


def test_feature_license(dut, log_level):
    output_0 = ["""
OEM Territory : ATI USA
Software Licenses
------------------------------------------------------------------------
Index                         : 1
License name                  : 5.4.4-rl
Customer name                 : ABC
Quantity of licenses          : -
Type of license               : Full
License issue date            : 01-Oct-2013
License expiry date           : N/A
Release                       : 5.4.4
"""]
    output_1 = ["""
OEM Territory : ATI USA
Software Licenses
------------------------------------------------------------------------
Index                         : 1
License name                  : Base
Customer name                 : ABC
Quantity of licenses          : 1
Type of license               : Full
License issue date            : 10-Dec-2013
License expiry date           : N/A
Features included             : EPSR-MASTER, IPv6Basic, MLDSnoop, OSPF-64,
                                RADIUS-100, RIP, VRRP

Index                         : 2
License name                  : 5.4.4-rl
Customer name                 : ABC
Quantity of licenses          : -
Type of license               : Full
License issue date            : 01-Oct-2013
License expiry date           : N/A
Release                       : 5.4.4
"""]

    setup_dut(dut)
    label = 'Base'
    key = '1234567890'
    set_cmd = 'license {0} {1}'.format(label, key)
    delete_cmd = 'no license {0}'.format(label)

    dut.add_cmd({'cmd': 'show license', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': set_cmd       , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state':1, 'action':'PRINT','args': output_1})
    dut.add_cmd({'cmd': delete_cmd    , 'state':1, 'action':'SET_STATE','args': [2]})
    dut.add_cmd({'cmd': 'show license', 'state':2, 'action':'PRINT','args': output_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(label='', key=key)
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(label=label, key='')
    with pytest.raises(KeyError) as excinfo:
        d.license['Bbase']
    assert label not in d.license.keys()
    d.license.set_license(label=label, key=key)
    assert label in d.license.keys()
    assert d.license[label]['features'] == True
    assert (label, {'customer': d.license[label]['customer'], 'quantity': d.license[label]['quantity'], 'type': d.license[label]['type'], 'issue_date': d.license[label]['issue_date'], 'expire_date': d.license[label]['expire_date'], 'features' : True, 'releases' : False}) in d.license.items()
    with pytest.raises(KeyError) as excinfo:
        d.license.delete(label='Bbase')
    d.license.delete(label=label)
    assert label not in d.license.keys()
    d.close()


def test_release_license(dut, log_level):
    output_0 = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x210-5.4.3-2.6.rel
Current boot image : flash:/x210-5.4.3-2.6.rel
Backup  boot image : flash:/x210-5.4.3-2.6.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]
    output_1 = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x210-5.4.3-2.6.rel
Current boot image : flash:/x210-5.4.3-2.7.rel
Backup  boot image : flash:/x210-5.4.3-2.6.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]

    cert_file = 'demo.csv'
    cert_path = os.path.dirname(os.path.abspath(__file__)) + '/../examples/'
    cert_name = cert_path + cert_file
    false_cert_file = 'demo1.csv'
    false_cert_url = 'http://10.17.90.17/demo1.csv'

    setup_dut(dut)
    setup_test_release_license(dut, cert_name)

    set_cmd = 'license certificate {0}'.format(cert_name)
    dut.add_cmd({'cmd': 'show license', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': set_cmd       , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_file)
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_url)
    d.license.set_license(certificate=cert_name)
    d.close()

    os.remove(cert_name)