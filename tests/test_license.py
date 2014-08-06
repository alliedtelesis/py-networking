import pytest
import logging
import os
import socket
import tftpy
import threading
import getpass
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


def setup_test_release_license(dut, cert_file, tftp_server=False):
    if (dut.mode == 'emulated'):
        if (os.path.exists(cert_file) == False):
            myfile = open(cert_file, 'w')
            myfile.write('# certificate file facsimile\n')
            myfile.write('# feature licenses\n')
            myfile.write('000C-25A4-00F0,license_for_IPv6,1234567890abcdefghijklmnopqrstuvwxyz\n')
            myfile.write('*,license_for_IPv6_bis,123+/=456+/=abcdefghijkl+/=mnopqrstuv+/=Qwxyz\n')
            myfile.write('# release licenses\n')
            myfile.write('000C-25A4-00F0,upgrade_to_544rl,ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890\n')
            myfile.write('*,upgrade_to_544rl_bis,ABCDEFGHIJKLMNOPQRSTUVWXYZ=/+=/+=/+1234567890\n')
            myfile.close()

    if (tftp_server == True):
        if (dut.mode != 'emulated'):
            assert 'root' == getpass.getuser()
        dut.tftp_port = 69
        if (getpass.getuser() != 'root'):
            dut.tftp_port = 20069

        client_dir = './tftp_client_dir'
        server_dir = './tftp_server_dir'
        tftp_make_dir(client_dir, server_dir)
        if not hasattr(dut, 'tftp_server_thread'):
            dut.tftp_server_thread = threading.Thread(target=tftp_server_for_ever, args=(dut.tftp_port, server_dir,))
            dut.tftp_server_thread.daemon = True
            dut.tftp_server_thread.start()

        tftp_client = tftpy.TftpClient(socket.gethostbyname(socket.getfqdn()), dut.tftp_port)
        tftp_client.upload(cert_file.split('/')[-1], cert_file)


def tftp_make_dir(tftp_client_dir, tftp_server_dir):
    if (os.path.exists(tftp_client_dir) == False):
        os.mkdir(tftp_client_dir)
    if (os.path.exists(tftp_server_dir) == False):
        os.mkdir(tftp_server_dir)


def tftp_server_for_ever(port, tftp_server_dir):
    ip_address = socket.gethostbyname(socket.getfqdn())
    server = tftpy.TftpServer(tftp_server_dir)
    server.listen(ip_address, port)


def clean_test_release_license(dut, cert_file):
    if (dut.mode == 'emulated'):
        if (os.path.exists(cert_file) == True):
            os.remove(cert_file)
    tftp_client_dir = './tftp_client_dir'
    if (os.path.exists(tftp_client_dir) == True):
        os.rmdir(tftp_client_dir)
    tftp_server_dir = './tftp_server_dir'
    tftp_server_file = tftp_server_dir + '/' + cert_file
    if (os.path.exists(tftp_server_file) == True):
        os.remove(tftp_server_file)
    if (os.path.exists(tftp_server_dir) == True):
        os.rmdir(tftp_server_dir)


def test_feature_license(dut, log_level):
    output_0 = ["""
OEM Territory : Global
Software Licenses
------------------------------------------------------------------------
Index                         : 1
License name                  : Base License
Customer name                 : Base License
Quantity of licenses          : 1
Type of license               : Full
License issue date            : 06-Aug-2014
License expiry date           : N/A
Features included             : EPSR-MASTER, IPv6Basic, LAG-FULL, MLDSnoop,
                                No-License-Lock, OSPF-64, RADIUS-100, RIP,
                                VRRP
"""]
    output_1 = ["""
OEM Territory : Global
Software Licenses
------------------------------------------------------------------------
Index                         : 1
License name                  : Base License
Customer name                 : Base License
Quantity of licenses          : 1
Type of license               : Full
License issue date            : 06-Aug-2014
License expiry date           : N/A
Features included             : EPSR-MASTER, IPv6Basic, LAG-FULL, MLDSnoop,
                                No-License-Lock, OSPF-64, RADIUS-100, RIP,
                                VRRP

Index                         : 2
License name                  : AT-FL-x610-01
Customer name                 : C.A.R.T. Elettronica srl
Quantity of licenses          : 2
Type of license               : Full
License issue date            : 29-Jan-2014
License expiry date           : N/A
Features included             : BGP-5K, OSPF-FULL, PIM, PIM-100, VlanDT,
                                VRF-LITE, VRF-LITE-63
"""]

    setup_dut(dut)
    label = 'AT-FL-x610-01'
    key = 'jkRaT0PvfUf/M7VhxAzdAZLB/RcX95VNU3xIOwW0aKi9FSOFtJ5otefLbZur0aAQ7xr2JT88N7U='
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
    assert d.license[label]['features'] != ''
    assert d.license[label]['releases'] == ''
    assert (label, {'customer': d.license[label]['customer'], 'quantity': d.license[label]['quantity'], 'type': d.license[label]['type'], 'issue_date': d.license[label]['issue_date'], 'expire_date': d.license[label]['expire_date'], 'features' : d.license[label]['features'], 'releases' : ''}) in d.license.items()
    with pytest.raises(KeyError) as excinfo:
        d.license.delete(label='Bbase')
    d.license.delete(label=label)
    assert label not in d.license.keys()
    d.close()


def test_release_license_path(dut, log_level):
    output_0 = ["""
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

    cert_file = 'demo.csv'
    cert_path = os.path.dirname(os.path.abspath(__file__)) + '/../examples/'
    cert_name = cert_path + cert_file
    false_cert_file = 'demo1.csv'
    name = '5.4.4-rl'

    setup_dut(dut)
    setup_test_release_license(dut, cert_name)

    set_cmd = 'license certificate {0}'.format(cert_file)
    dut.add_cmd({'cmd': 'show license', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': set_cmd       , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_file)
    assert name not in d.license.keys()
    d.license.set_license(certificate=cert_name)
    assert name in d.license.keys()
    assert d.license[name]['features'] == ''
    assert d.license[name]['releases'] != ''
    d.close()

    clean_test_release_license(dut, cert_name)


def test_release_license_tftp(dut, log_level):
    output_0 = ["""
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

    cert_file = 'demo.csv'
    cert_url = 'tftp://{0}/{1}'.format(socket.gethostbyname(socket.getfqdn()), cert_file)
    false_cert_url = 'http://{0}/demo1.csv'.format(socket.gethostbyname(socket.getfqdn()))
    name = '5.4.4-rl'

    setup_dut(dut)
    setup_test_release_license(dut, cert_file, tftp_server=True)

    set_cmd = 'license certificate {0}'.format(cert_url)
    dut.add_cmd({'cmd': 'show license', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': set_cmd       , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_url)
    assert name not in d.license.keys()
    d.license.set_license(certificate=cert_url)
    assert name in d.license.keys()
    assert d.license[name]['features'] == ''
    assert d.license[name]['releases'] != ''
    d.close()

    clean_test_release_license(dut, cert_file)
