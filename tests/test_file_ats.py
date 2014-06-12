import pytest
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


def test_copy_file_from_device_to_device(dut, log_level):
    setup_dut(dut)
    # dut.add_cmd({'cmd': 'dir'               , 'state':0, 'action':'PRINT','args': dir_0})
    # dut.add_cmd({'cmd': 'delete video-2.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    # dut.add_cmd({'cmd': 'dir'               , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.close()


def test_copy_file_from_device_to_host(dut, log_level):
    setup_dut(dut)
    # dut.add_cmd({'cmd': 'dir'               , 'state':0, 'action':'PRINT','args': dir_0})
    # dut.add_cmd({'cmd': 'delete video-2.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    # dut.add_cmd({'cmd': 'dir'               , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.close()


def test_copy_file_from_host_to_device(dut, log_level):
    setup_dut(dut)
    # dut.add_cmd({'cmd': 'dir'               , 'state':0, 'action':'PRINT','args': dir_0})
    # dut.add_cmd({'cmd': 'delete video-2.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    # dut.add_cmd({'cmd': 'dir'               , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.close()


def test_remove_file(dut, log_level):
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
directry.prv            --       262144      --      01-Jan-2000 01:02:12
startup-config          rw       524288      437     01-Oct-2006 02:07:34

Total size of flash: 15990784 bytes
Free size of flash: 3276800 bytes

"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'               , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': 'delete video-2.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'               , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'video-2.cfg' in d.file.keys()
    d.file.delete("video-2.cfg")
    assert 'video-2.cfg' not in d.file.keys()
    d.close()
