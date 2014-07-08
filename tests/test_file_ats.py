import pytest
import os
import socket
import tftpy
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey


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


def test_create_file_with_failures(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
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
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'startup-config' in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='startup-config', text=host_text)
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='test_file.cfg', text=host_text, filename='startup-config')
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='test_file.cfg', text=host_text, server='10.17.90.1')
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='test_file.cfg', server='10.17.90.1')
    with pytest.raises(KeyError) as excinfo:
        d.file['video-3.cfg']
    d.close()


def test_create_empty_file(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
test_file_0.cfg         rw       524288       1      20-Jun-2014 11:35:01

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    setup_dut(dut)
    host_file_name = 'test_file_0.cfg'
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    create_cmd = 'copy tftp://{0}/test_file_0.cfg test_file_0.cfg'.format(local_tftp_server)
    delete_cmd = 'delete test_file_0.cfg'
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    dut.add_cmd({'cmd': delete_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert host_file_name not in d.file.keys()
    d.file.create(name=host_file_name)
    assert host_file_name in d.file.keys()
    assert (host_file_name, {'size': '1', 'mdate': d.file[host_file_name]['mdate'], 'permission': 'rw', 'mtime': d.file[host_file_name]['mtime']}) in d.file.items()
    d.file.delete(host_file_name)
    assert host_file_name not in d.file.keys()
    d.close()


def test_create_file_through_another_file(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
test_file_1.cfg         rw       131072      284     20-Jun-2014 11:49:22

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
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
    setup_dut(dut)
    host_file_name = 'local.cfg'
    device_file_name = 'test_file_1.cfg'
    myfile = open(host_file_name, 'w')
    myfile.write(host_text)
    myfile.close()
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    create_cmd = 'copy tftp://{0}/local.cfg test_file_1.cfg'.format(local_tftp_server)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' not in d.file.keys()
    d.file.create(name='test_file_1.cfg', filename='local.cfg')
    assert 'test_file_1.cfg' in d.file.keys()
    assert d.file['test_file_1.cfg']['size'] == '{0}'.format(len(host_text))
    d.close()
    os.remove(host_file_name)


def test_create_file_through_text(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
test_file_1.cfg         rw       131072      284     20-Jun-2014 11:49:22

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
test_file_1.cfg         rw       131072      284     20-Jun-2014 11:49:22
test_file_2.cfg         rw       131072      321     20-Jun-2014 11:54:01

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,30,100,1000,2000,3000,4000,4045,4093
exit
interface vlan 10
name "long vlan name"
exit
interface vlan 2000
name video1
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    setup_dut(dut)
    host_file_name = 'test_file_2.cfg'
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    create_cmd = 'copy tftp://{0}/test_file_2.cfg test_file_2.cfg'.format(local_tftp_server)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_2.cfg' not in d.file.keys()
    d.file.create(name='test_file_2.cfg', text=host_text)
    assert 'test_file_2.cfg' in d.file.keys()
    assert d.file['test_file_2.cfg']['size'] == '{0}'.format(len(host_text))
    d.close()


def test_read_file(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59
test_file_r.cfg         rw       131072      284     01-Jul-2014 11:37:01

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 555
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    setup_dut(dut)
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    create_cmd = 'copy tftp://{0}/test_file_r.cfg test_file_r.cfg'.format(local_tftp_server)
    dut.add_cmd({'cmd': 'dir'                      , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd                 , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'                      , 'state':1, 'action':'PRINT','args': dir_1})
    dut.add_cmd({'cmd': 'show file test_file_r.cfg', 'state':1, 'action':'PRINT','args': [host_text]})
    dut.add_cmd({'cmd': 'delete test_file_r.cfg'   , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'dir'                      , 'state':2, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_r.cfg' not in d.file.keys()
    d.file.create(name='test_file_r.cfg', text=host_text)
    assert 'test_file_r.cfg' in d.file.keys()
    # assert d.file['test_file_r.cfg']['content'] == host_text
    d.file.delete("test_file_r.cfg")
    assert 'test_file_r.cfg' not in d.file.keys()
    d.close()


def test_update_file_with_failures(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
test_file_1.cfg         rw       131072      284     20-Jun-2014 11:49:22

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'startup-config' in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_3.cfg', text=host_text)
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', text=host_text, new_name='startup-config')
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg')
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', filename='host_temp.cfg', text=host_text)
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', text=host_text, server='10.17.90.1')
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', server='10.17.90.1')
    d.close()


def test_update_file_through_text(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59
test_file_1.cfg         rw       131072      284     20-Jun-2014 11:49:22

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      202     20-Jun-2014 12:03:36

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    update_cmd = 'copy tftp://{0}/test_file_1.cfg test_file_1.cfg'.format(local_tftp_server)
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    old_mtime = d.file['test_file_1.cfg']['mtime']
    d.file.update(name='test_file_1.cfg', text=host_text)
    assert old_mtime != d.file['test_file_1.cfg']['mtime']
    assert d.file['test_file_1.cfg']['size'] == '{0}'.format(len(host_text))
    d.close()


def test_update_file_through_another_file(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59
test_file_1.cfg         rw       131072      202     20-Jun-2014 12:03:36

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,2000
exit
interface vlan 2000
name video1
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    myfile = open('temp.cfg', 'w')
    myfile.write(host_text)
    myfile.close()
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    update_cmd = 'copy tftp://{0}/temp.cfg test_file_1.cfg'.format(local_tftp_server)
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    old_mtime = d.file['test_file_1.cfg']['mtime']
    d.file.update(name='test_file_1.cfg', filename='temp.cfg')
    assert old_mtime != d.file['test_file_1.cfg']['mtime']
    assert d.file['test_file_1.cfg']['size'] == '{0}'.format(len(host_text))
    d.close()
    os.remove('temp.cfg')


def test_update_file_and_rename(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_2 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,2000,2001
exit
interface vlan 2000
name video1
exit
interface vlan 2001
name voice1
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    update_cmd = 'copy tftp://{0}/test_file_1.cfg test_file_3.cfg'.format(local_tftp_server)
    delete_cmd = 'delete test_file_1.cfg'
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    dut.add_cmd({'cmd': delete_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_2})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    assert 'test_file_3.cfg' not in d.file.keys()
    d.file.update(name='test_file_1.cfg', text=host_text, new_name='test_file_3.cfg')
    assert 'test_file_1.cfg' not in d.file.keys()
    assert 'test_file_3.cfg' in d.file.keys()
    assert d.file['test_file_3.cfg']['size'] == '{0}'.format(len(host_text))
    d.close()


def test_remote_tftp_server(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      192     20-Jun-2014 11:48:59
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27
test_file_5.cfg         rw       131072      247     07-Jul-2014 12:04:51

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_2 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27
test_file_5.cfg         rw       131072      247     07-Jul-2014 12:09:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_3 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_1.cfg         rw       131072      244     20-Jun-2014 12:08:41
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:09:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    host_text_1 = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,3000
exit
interface vlan 3000
name video3000
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    host_text_2 = """
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
vlan database
vlan 2,10,3001
exit
interface vlan 3001
name voice3001
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
"""
    remote_tftp_server = socket.gethostbyname(socket.getfqdn())

    myfile = open('test_file_A.cfg', 'w')
    myfile.write(host_text_1)
    myfile.close()

    myfile = open('test_file_B.cfg', 'w')
    myfile.write(host_text_2)
    myfile.close()

    create_cmd = 'copy tftp://{0}/test_file_A.cfg test_file_5.cfg'.format(remote_tftp_server)
    update_cmd = 'copy tftp://{0}/test_file_B.cfg test_file_5.cfg'.format(remote_tftp_server)
    delete_cmd = 'delete test_file_5.cfg'
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    dut.add_cmd({'cmd': update_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_2})
    dut.add_cmd({'cmd': delete_cmd, 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'dir'     , 'state':3, 'action':'PRINT','args': dir_3})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert 'test_file_5.cfg' not in d.file.keys()
    d.file.create(name='test_file_5.cfg', server = remote_tftp_server, filename='test_file_A.cfg')
    assert 'test_file_5.cfg' in d.file.keys()
    assert d.file['test_file_5.cfg']['size'] == '{0}'.format(len(host_text_1))
    d.file.update(name='test_file_5.cfg', server = remote_tftp_server, filename='test_file_B.cfg')
    assert 'test_file_5.cfg' in d.file.keys()
    assert d.file['test_file_5.cfg']['size'] == '{0}'.format(len(host_text_2))
    d.file.delete("test_file_5.cfg")
    assert 'test_file_5.cfg' not in d.file.keys()
    d.close()

    os.remove('test_file_A.cfg')
    os.remove('test_file_B.cfg')


def test_remove_files(dut, log_level):
    dir_0 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
test_file_2.cfg         rw       131072      244     20-Jun-2014 12:14:41
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:15:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_1 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22
test_file_3.cfg         rw       131072      286     20-Jun-2014 12:15:27

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    dir_2 = ["""
Directory of flash:

     File Name      Permission Flash Size Data Size        Modified
------------------- ---------- ---------- --------- -----------------------
starts                  rw       524288      982     01-Oct-2006 01:12:44
image-1                 rw      5242880    4325376   01-Jan-2000 01:07:08
image-2                 rw      5242880    4325376   01-Oct-2006 01:28:04
dhcpsn.prv              --       131072      --      01-Jan-2000 01:02:12
sshkeys.prv             --       262144      --      01-Oct-2006 01:01:16
syslog1.sys             r-       262144      --      01-Oct-2006 01:03:28
syslog2.sys             r-       262144      --      01-Oct-2006 01:03:28
video-2.cfg             rw       524288      154     01-Oct-2006 01:02:36
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34
default.cfg             rw       131072      284     20-Jun-2014 11:49:22

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'                   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': 'delete test_file_2.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'                   , 'state':1, 'action':'PRINT','args': dir_1})
    dut.add_cmd({'cmd': 'delete test_file_3.cfg', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'dir'                   , 'state':2, 'action':'PRINT','args': dir_2})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_2.cfg' in d.file.keys()
    assert 'test_file_3.cfg' in d.file.keys()
    assert 'test_file_x.cfg' not in d.file.keys()
    d.file.delete("test_file_2.cfg")
    assert 'test_file_2.cfg' not in d.file.keys()
    assert 'test_file_3.cfg' in d.file.keys()
    d.file.delete("test_file_3.cfg")
    with pytest.raises(KeyError) as excinfo:
        d.file.delete("test_file_x.cfg")
    assert 'test_file_2.cfg' not in d.file.keys()
    assert 'test_file_3.cfg' not in d.file.keys()
    d.close()
