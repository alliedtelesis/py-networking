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


def setup_test_firmware_upgrade(dut, release_file):
    if (dut.mode == 'emulated'):
        if (os.path.exists(release_file) == False):
            myfile = open(release_file, 'w')
            myfile.write('1')
            myfile.close()


def clean_test_firmware_upgrade(dut, release_file):
    if (dut.mode == 'emulated'):
        os.remove(release_file)


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


def test_firmware_upgrade_543(dut, log_level):
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
    release_file = 'x210-5.4.3-2.7.rel'
    false_release_file = 'x211-5.4.3-2.7.rel'
    bad_name_release_file = 'x210-5.4.3-2.7.rol'

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, release_file)
    assert (os.path.exists(release_file) == True)
    assert (os.path.exists(false_release_file) == False)

    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{1}'.format(socket.gethostbyname(socket.getfqdn()), release_file)
    dut.add_cmd({'cmd': 'show boot', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': update_cmd , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show boot', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware(false_release_file)
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware(bad_name_release_file)
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware('x210-5.4.3-2.6.rel')
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware('x210-5.4.3-2.7.rel', protocol='tftp')
    d.system.update_firmware(release_file)
    d.close()

    clean_test_firmware_upgrade(dut, release_file)


def test_firmware_upgrade_full_path(dut, log_level):
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
    image_file = 'x210-5.4.3-2.7.rel'
    image_path = os.path.dirname(os.path.abspath(__file__)) + '/../examples/'
    image_name = image_path + image_file

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, image_name)
    assert (os.path.exists(image_name) == True)

    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{1}'.format(socket.gethostbyname(socket.getfqdn()), image_file)
    dut.add_cmd({'cmd': 'show boot', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': update_cmd , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show boot', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    d.system.update_firmware(image_name)
    d.close()

    clean_test_firmware_upgrade(dut, image_name)


def test_firmware_upgrade_544(dut, log_level):
    output_show_boot = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x210-5.4.4-1.4.rel
Current boot image : flash:/x210-5.4.4-1.4.rel
Backup  boot image : flash:/x210-5.4.4-1.4.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]
    output_show_version= ["""
AlliedWare Plus (TM) 5.4.4 07/25/14 17:51:44

Build name : x210-5.4.4-1.4.rel
Build date : Fri Jul 25 17:51:4 NZST 2014
Build type : RELEASE
 NET-SNMP SNMP agent software
 (c) 1996, 1998-2000 The Regents of the University of California.
     All rights reserved;
 (c) 2001-2003, Networks Associates Technology, Inc. All rights reserved;
 (c) 2001-2003, Cambridge Broadband Ltd. All rights reserved;
"""]

    release_file = 'x210-5.4.4-1.5.rel'

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, release_file)
    assert (os.path.exists(release_file) == True)

    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{2}'.format(socket.gethostbyname(socket.getfqdn()), release_file, release_file)
    dut.add_cmd({'cmd': 'show boot'                 , 'state':0, 'action':'PRINT','args': output_show_boot})
    dut.add_cmd({'cmd': 'show version'              , 'state':0, 'action':'PRINT','args': output_show_version})
    dut.add_cmd({'cmd': update_cmd                  , 'state':0, 'action':'SET_STATE','args': [1]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    d.system.update_firmware(release_file)
    d.close()

    clean_test_firmware_upgrade(dut, release_file)


def test_firmware_upgrade_544_unlicensed(dut, log_level):
    output_show_boot = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x908-5.4.4-1.4.rel
Current boot image : flash:/x908-5.4.4-1.4.rel
Backup  boot image : flash:/x908-5.4.4-1.4.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]
    output_show_license= ["""
OEM Territory : ATI USA
Software Release Licenses
---------------------------------------------------------------------
Index License name    Quantity     Customer name
      Type            Version      Period
---------------------------------------------------------------------
"""]
    output_show_version= ["""
AlliedWare Plus (TM) 5.4.4 07/25/14 17:51:44

Build name : x908-5.4.4-1.4.rel
Build date : Fri Jul 25 17:51:4 NZST 2014
Build type : RELEASE
 NET-SNMP SNMP agent software
 (c) 1996, 1998-2000 The Regents of the University of California.
     All rights reserved;
 (c) 2001-2003, Networks Associates Technology, Inc. All rights reserved;
 (c) 2001-2003, Cambridge Broadband Ltd. All rights reserved;
"""]

    release_file = 'x908-5.4.4-1.5.rel'

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, release_file)
    assert (os.path.exists(release_file) == True)

    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{2}'.format(socket.gethostbyname(socket.getfqdn()), release_file, release_file)
    dut.add_cmd({'cmd': 'show boot'                 , 'state':0, 'action':'PRINT','args': output_show_boot})
    dut.add_cmd({'cmd': 'show license release brief', 'state':0, 'action':'PRINT','args': output_show_license})
    dut.add_cmd({'cmd': 'show version'              , 'state':0, 'action':'PRINT','args': output_show_version})
    dut.add_cmd({'cmd': update_cmd                  , 'state':0, 'action':'SET_STATE','args': [1]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware(release_file)
    d.close()

    clean_test_firmware_upgrade(dut, release_file)


def test_firmware_upgrade_544_licensed(dut, log_level):
    output_show_boot_0 = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x908-5.4.4-1.4.rel
Current boot image : flash:/x908-5.4.4-1.4.rel
Backup  boot image : flash:/x908-5.4.4-1.4.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]
    output_show_boot_1 = ["""
Boot configuration
----------------------------------------------------------------
Current software   : x908-5.4.4-1.5.rel
Current boot image : flash:/x908-5.4.5-1.0.rel
Backup  boot image : flash:/x908-5.4.4-1.4.rel
Default boot config: flash:/default.cfg
Current boot config: flash:/my.cfg (file exists)
Backup  boot config: flash:/backup.cfg (file not found)
"""]
    output_show_license= ["""
OEM Territory : ATI USA
Software Release Licenses
---------------------------------------------------------------------
Index License name    Quantity     Customer name
      Type            Version      Period
---------------------------------------------------------------------
1     544             -            ABC Consulting
      Trial           5.4.4        N/A
"""]
    output_show_version= ["""
AlliedWare Plus (TM) 5.4.4 07/25/14 17:51:44

Build name : x908-5.4.4-1.5.rel
Build date : Fri Jul 25 17:51:4 NZST 2014
Build type : RELEASE
 NET-SNMP SNMP agent software
 (c) 1996, 1998-2000 The Regents of the University of California.
     All rights reserved;
 (c) 2001-2003, Networks Associates Technology, Inc. All rights reserved;
 (c) 2001-2003, Cambridge Broadband Ltd. All rights reserved;
"""]

    release_file = 'x908-5.4.4-1.5.rel'

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, release_file)
    assert (os.path.exists(release_file) == True)

    update_cmd = 'copy\s+http://{0}:\d+/{1}\s+{2}'.format(socket.gethostbyname(socket.getfqdn()), release_file, release_file)
    dut.add_cmd({'cmd': 'show boot'                 , 'state':0, 'action':'PRINT','args': output_show_boot_0})
    dut.add_cmd({'cmd': 'show license release brief', 'state':0, 'action':'PRINT','args': output_show_license})
    dut.add_cmd({'cmd': 'show version'              , 'state':0, 'action':'PRINT','args': output_show_version})
    dut.add_cmd({'cmd': update_cmd                  , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show boot'                 , 'state':1, 'action':'PRINT','args': output_show_boot_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    d.system.update_firmware(release_file)
    d.close()

    clean_test_firmware_upgrade(dut, release_file)


def test_ping2(dut, log_level):
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    dut.stop()
    assert not d.ping()
    d.close()
