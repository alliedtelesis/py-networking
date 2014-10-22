import pytest
import os
import socket
import tftpy
import threading
import getpass
from pynetworking.Device import Device


def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd': 'show system', 'state': 0, 'action': 'PRINT', 'args': ["""
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
    dut.add_cmd({'cmd': 'show version', 'state': 0, 'action': 'PRINT', 'args': ["""
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


def tftp_server_for_ever(port, tftp_server_dir):
    ip_address = socket.gethostbyname(socket.getfqdn())
    server = tftpy.TftpServer(tftp_server_dir)
    server.listen(ip_address, port)


def setup_test_certificate(dut, cert_file, label, key, mac='', tftp_server=False):
    if (os.path.exists(cert_file) is False):
        myfile = open(cert_file, 'w')
        myfile.write('# certificate file for tests\n')
        if (mac == ''):
            license_entry = '*,{0},{1}\n'.format(label, key)
            myfile.write('# feature licenses\n')
            myfile.write(license_entry)
        else:
            release_entry = '{0},{1},{2}\n'.format(mac, label, key)
            myfile.write('# release licenses\n')
            myfile.write(release_entry)
        myfile.close()

    if (tftp_server is True):
        if (dut.mode != 'emulated'):
            assert 'root' == getpass.getuser()
        dut.tftp_port = 69
        if (getpass.getuser() != 'root'):
            dut.tftp_port = 20069

        client_dir = './tftp_client_dir'
        server_dir = './tftp_server_dir'
        if (os.path.exists(client_dir) is False):
            os.mkdir(client_dir)
        if (os.path.exists(server_dir) is False):
            os.mkdir(server_dir)
        if not hasattr(dut, 'tftp_server_thread'):
            dut.tftp_server_thread = threading.Thread(target=tftp_server_for_ever, args=(dut.tftp_port, server_dir,))
            dut.tftp_server_thread.daemon = True
            dut.tftp_server_thread.start()

        tftp_client = tftpy.TftpClient(socket.gethostbyname(socket.getfqdn()), dut.tftp_port)
        tftp_client.upload(cert_file.split('/')[-1], cert_file)


def clean_test_environment(dut, cert_file):
    if (os.path.exists(cert_file) is True):
        os.remove(cert_file)
    tftp_client_dir = './tftp_client_dir'
    if (os.path.exists(tftp_client_dir) is True):
        os.rmdir(tftp_client_dir)
    tftp_server_dir = './tftp_server_dir'
    tftp_server_file = tftp_server_dir + '/' + cert_file
    if (os.path.exists(tftp_server_file) is True):
        os.remove(tftp_server_file)
    if (os.path.exists(tftp_server_dir) is True):
        os.rmdir(tftp_server_dir)


def test_feature_license_label_key(dut, log_level, use_mock):
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

    label = 'AT-FL-x610-01'
    key = 'jkRaT0PvfUf/M7VhxAzdAZLB/RcX95VNU3xIOwW0aKi9FSOFtJ5otefLbZur0aAQ7xr2JT88N7U='

    setup_dut(dut)

    set_cmd = 'license {0} {1}'.format(label, key)
    delete_cmd = 'no license {0}'.format(label)

    dut.add_cmd({'cmd': 'show license', 'state': 0, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': set_cmd, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state': 1, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show license', 'state': 2, 'action': 'PRINT', 'args': output_0})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(label='', key=key)
    assert 'either label and key or certificate must be given' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(label=label, key='')
    assert 'either label and key or certificate must be given' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.license['Bbase']
    assert 'license Bbase does not exist' in excinfo.value
    assert label not in d.license.keys()
    d.license.set_license(label=label, key=key)
    assert label in d.license.keys()
    assert d.license[label]['features'] == 'BGP-5K, OSPF-FULL, PIM, PIM-100, VlanDT, VRF-LITE, VRF-LITE-63'
    assert d.license[label]['releases'] == ''
    assert (label, {'customer': d.license[label]['customer'], 'quantity': d.license[label]['quantity'], 'type': d.license[label]['type'],
                    'issue_date': d.license[label]['issue_date'], 'expire_date': d.license[label]['expire_date'],
                    'features': d.license[label]['features'], 'releases': ''}) in d.license.items()
    with pytest.raises(KeyError) as excinfo:
        d.license.delete(label='Bbase')
    assert 'label Bbase does not exist' in excinfo.value
    d.license.delete(label=label)
    assert label not in d.license.keys()
    d.close()


def test_feature_license_path(dut, log_level, use_mock):
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

    cert_file = 'demo.csv'
    cert_path = os.path.dirname(os.path.abspath(__file__)) + '/../examples/'
    cert_name = cert_path + cert_file
    false_cert_file = 'demo1.csv'
    label = 'AT-FL-x610-01'
    key = 'jkRaT0PvfUf/M7VhxAzdAZLB/RcX95VNU3xIOwW0aKi9FSOFtJ5otefLbZur0aAQ7xr2JT88N7U='

    setup_dut(dut)

    setup_test_certificate(dut, cert_name, label, key)
    set_cmd = 'license certificate {0}'.format(cert_file)
    delete_cmd = 'no license {0}'.format(label)

    dut.add_cmd({'cmd': 'show license', 'state': 0, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': set_cmd, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state': 1, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show license', 'state': 2, 'action': 'PRINT', 'args': output_0})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_file)
    assert 'certificate file {0} does not exist'.format(false_cert_file) in excinfo.value
    assert label not in d.license.keys()
    d.license.set_license(certificate=cert_name)
    assert label in d.license.keys()
    assert d.license[label]['features'] == 'BGP-5K, OSPF-FULL, PIM, PIM-100, VlanDT, VRF-LITE, VRF-LITE-63'
    assert d.license[label]['releases'] == ''
    d.license.delete(label=label)
    assert label not in d.license.keys()
    if cert_file in d.file.keys():
        d.file.delete(cert_file)
    d.close()

    clean_test_environment(dut, cert_name)


def test_feature_license_tftp(dut, log_level, use_mock):
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

    cert_file = 'demo.csv'
    cert_url = 'tftp://{0}/{1}'.format(socket.gethostbyname(socket.getfqdn()), cert_file)
    false_cert_url = 'http://{0}/{1}'.format(socket.gethostbyname(socket.getfqdn()), cert_file)
    label = 'AT-FL-x610-01'
    key = 'jkRaT0PvfUf/M7VhxAzdAZLB/RcX95VNU3xIOwW0aKi9FSOFtJ5otefLbZur0aAQ7xr2JT88N7U='

    setup_dut(dut)

    setup_test_certificate(dut, cert_file, label, key, tftp_server=True)
    set_cmd = 'license certificate {0}'.format(cert_url)
    delete_cmd = 'no license {0}'.format(label)

    dut.add_cmd({'cmd': 'show license', 'state': 0, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': set_cmd, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state': 1, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show license', 'state': 2, 'action': 'PRINT', 'args': output_0})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.license.set_license(certificate=false_cert_url)
    assert 'protocol http not supported' in excinfo.value
    assert label not in d.license.keys()
    assert cert_file not in d.file.keys()
    d.license.set_license(certificate=cert_url)
    assert label in d.license.keys()
    assert d.license[label]['features'] == 'BGP-5K, OSPF-FULL, PIM, PIM-100, VlanDT, VRF-LITE, VRF-LITE-63'
    assert d.license[label]['releases'] == ''
    d.license.delete(label=label)
    assert label not in d.license.keys()
    d.close()

    clean_test_environment(dut, cert_file)


def test_release_license(dut, log_level, use_mock):
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
License name                  : rel-544
Customer name                 : Allied Telesis Int. - EMEA Service LAB - Milan
Quantity of licenses          : -
Type of license               : Full
License issue date            : 01-Oct-2013
License expiry date           : N/A
Release                       : 5.4.4
"""]

    cert_file = 'demo.csv'
    cert_url = 'tftp://{0}/{1}'.format(socket.gethostbyname(socket.getfqdn()), cert_file)
    label = 'rel-544'
    key = 'iRVj3gJbwguCAW4ueUYE6izn1OhPYxtcMnLXMd3BTw81OFKBQvwio4/aL09QheRGdHV2oglgTb+NGb19aNfQeKSvYceLeDTP'
    mac_address = 'eccd-6d8d-16a9'

    # Output of key tool:
    # Certificate created on 2014-09-02 for Allied Telesis Int. - EMEA Service LAB - Milan
    # eccd-6d8d-16a9, rel-544, iRVj3gJbwguCAW4ueUYE6izn1OhPYxtcMnLXMd3BTw81OFKBQvwio4/aL09QheRGdHV2oglgTb+NGb19aNfQeKSvYceLeDTP

    setup_dut(dut)

    setup_test_certificate(dut, cert_file, label, key, mac=mac_address, tftp_server=True)
    set_cmd = 'license certificate {0}'.format(cert_url)
    delete_cmd = 'no license {0}'.format(label)

    dut.add_cmd({'cmd': 'show license', 'state': 0, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': set_cmd, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show license', 'state': 1, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show license', 'state': 2, 'action': 'PRINT', 'args': output_0})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    assert label not in d.license.keys()
    assert cert_file not in d.file.keys()
    d.license.set_license(certificate=cert_url)
    assert label in d.license.keys()
    assert d.license[label]['features'] == ''
    assert d.license[label]['releases'] == '5.4.4'
    d.license.delete(label=label)
    assert label not in d.license.keys()
    d.close()

    clean_test_environment(dut, cert_file)
