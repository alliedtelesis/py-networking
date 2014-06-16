import pytest
import os
import socket
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey


def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd':'show version',        'state':-1, 'action': 'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})


def test_copy_file_from_device_to_host(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    setup_dut(dut)
    copy_cmd = 'copy default.cfg http://' + socket.gethostbyname(socket.getfqdn()) + os.getcwd() + '/default.cfg'
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'default.cfg' in d.file.keys()
    d.file.download("default.cfg")
    # assert 'default.cfg' in os.listdir(os.getcwd())
    d.close()


def test_copy_file_from_host_to_device_1(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    dir_1 = ["""
      588 -rw- Jun 10 2014 12:38:10  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    video_2_cfg_content = """
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
access-list 67 permit any
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
snmp-server community public
!
aaa authentication enable default local
aaa authentication login default local
!
ip domain-lookup
!
no service dhcp-server
spanning-tree mode rstp
!
interface port1.0.1-1.0.24
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
line con 0
line vty 0 4
!
end
"""
    setup_dut(dut)
    myfile = open('video-2.cfg', 'w')
    myfile.write(video_2_cfg_content)
    myfile.close()
    host_path = os.getcwd() + '/' + 'video-2.cfg'
    copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'   , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'video-2.cfg' not in d.file.keys()
    d.file.upload(host_path)
    assert 'video-2.cfg' in d.file.keys()
    d.close()


def test_copy_file_from_host_to_device_2(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    dir_1 = ["""
      588 -rw- Jun 10 2014 12:39:44  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    video_2_cfg_content = """
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
access-list 67 permit any
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
snmp-server community public
!
aaa authentication enable default local
aaa authentication login default local
!
ip domain-lookup
!
no service dhcp-server
spanning-tree mode rstp
!
interface port1.0.1-1.0.24
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
line con 0
line vty 0 4
!
end
"""
    setup_dut(dut)
    myfile = open('video-2.cfg', 'w')
    myfile.write(video_2_cfg_content)
    myfile.close()
    host_path = os.getcwd() + '/' + 'video-2.cfg'
    copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'   , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'video-2.cfg' in d.file.keys()
    old_date = d.file['video-2.cfg']['mtime']
    d.file.upload(host_path, overwrite=True)
    assert old_date != d.file['video-2.cfg']['mtime']
    d.close()


def test_copy_file_from_host_to_device_3(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    video_2_cfg_content = """
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
access-list 67 permit any
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
snmp-server community public
!
aaa authentication enable default local
aaa authentication login default local
!
ip domain-lookup
!
no service dhcp-server
spanning-tree mode rstp
!
interface port1.0.1-1.0.24
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
line con 0
line vty 0 4
!
end
"""
    setup_dut(dut)
    myfile = open('video-2.cfg', 'w')
    myfile.write(video_2_cfg_content)
    myfile.close()
    host_path = os.getcwd() + '/' + 'video-2.cfg'
    copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'video-2.cfg' in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.file.upload(host_path)
    assert 'file video-2.cfg cannot be overwritten' in excinfo.value
    d.close()


def test_remove_file(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  video-2.cfg
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
"""]
    dir_1 = ["""
      588 -rw- Jun 10 2014 12:38:10  video.cfg
      633 -rw- May 29 2014 12:34:00  voice.cfg
      588 -rw- Apr 10 2014 08:10:02  default.cfg
 16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
     4647 -rw- Nov 18 2013 11:14:46  x210.cfg
 16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
  3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
      735 -rw- Aug 23 2013 08:48:35  exception.log
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
