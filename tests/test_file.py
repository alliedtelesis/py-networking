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


def test_create_file_with_failures(dut, log_level):
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
    host_content = """
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
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'default.cfg' in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='default.cfg', text=host_content)
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='test_file.cfg', filename='unexisting.cfg')
    with pytest.raises(KeyError) as excinfo:
        d.file.create(name='test_file.cfg', text=host_content, filename='default.cfg')
    d.close()


def test_create_empty_file(dut, log_level):
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
        0 -rw- Jun 16 2014 15:15:15  test_file_0.cfg
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
    host_file_name = 'test_file_0.cfg'
    create_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + '/' + host_file_name + ' ' + host_file_name
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert host_file_name not in d.file.keys()
    d.file.create(name=host_file_name)
    assert host_file_name in d.file.keys()
    assert d.file[host_file_name]['size'] == '0'
    d.close()


def test_create_file_from_another_file(dut, log_level):
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
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
    dut.add_cmd({'cmd': 'dir'                             , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': 'copy default.cfg test_file_1.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'                             , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'default.cfg' in d.file.keys()
    assert 'test_file_1.cfg' not in d.file.keys()
    d.file.create(name='test_file_1.cfg', filename='default.cfg')
    assert 'default.cfg' in d.file.keys()
    assert 'test_file_1.cfg' in d.file.keys()
    assert d.file['default.cfg']['size'] == d.file['test_file_1.cfg']['size']
    d.close()


def test_create_file_from_string(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
      287 -rw- Jun 16 2014 15:23:44  test_file_2.cfg
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
    host_content = """
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
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""
    setup_dut(dut)
    host_file_name = 'test_file_2.cfg'
    create_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + '/' + host_file_name + ' ' + host_file_name
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert host_file_name not in d.file.keys()
    d.file.create(name=host_file_name, text=host_content)
    assert host_file_name in d.file.keys()
    d.close()


def test_update_file_with_failures(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
    host_text = """
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
interface port1.0.1-1.0.50
switchport
switchport mode access
!
interface vlan1
ip address 10.17.39.253/24
!
end
"""
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'default.cfg' in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_3.cfg', text=host_text)
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', text=host_text, new_name='default.cfg')
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg')
    with pytest.raises(KeyError) as excinfo:
        d.file.update(name='test_file_1.cfg', filename='host_temp.cfg', text=host_text)
    d.close()


def test_update_file_with_text(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
      588 -rw- Jun 16 2014 15:15:33  test_file_1.cfg
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
    host_text = """
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
interface port1.0.1-1.0.50
switchport
switchport mode access
!
interface vlan1
ip address 10.17.39.253/24
!
end
"""
    update_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + '/test_file_1.cfg test_file_1.cfg'
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    old_date = d.file['test_file_1.cfg']['mtime']
    d.file.update(name='test_file_1.cfg', text=host_text)
    assert old_date != d.file['test_file_1.cfg']['mtime']
    d.close()


def test_update_file_with_another_file(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
      588 -rw- Jun 16 2014 15:15:33  test_file_1.cfg
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
    host_text = """
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
interface port1.0.1-1.0.50
switchport
switchport mode access
!
interface vlan1
ip address 10.17.39.253/24
!
end
"""
    myfile = open('temp.cfg', 'w')
    myfile.write(host_text)
    myfile.close()
    update_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + '/temp.cfg test_file_1.cfg'
    setup_dut(dut)
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    old_date = d.file['test_file_1.cfg']['mtime']
    d.file.update(name='test_file_1.cfg', filename='temp.cfg')
    assert old_date != d.file['test_file_1.cfg']['mtime']
    d.close()
    os.remove('temp.cfg')


def test_update_file_and_rename(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 16 2014 15:15:15  test_file_1.cfg
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
      588 -rw- Jun 16 2014 15:15:16  test_file_1.cfg
      588 -rw- Jun 16 2014 15:15:33  test_file_4.cfg
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
    dir_2 = ["""
      588 -rw- Jun 16 2014 15:15:33  test_file_4.cfg
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
    host_text = """
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
interface port1.0.1-1.0.50
switchport
switchport mode access
!
interface vlan1
ip address 10.17.39.253/24
!
end
"""
    update_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + '/test_file_1.cfg test_file_4.cfg'
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
    assert 'test_file_4.cfg' not in d.file.keys()
    d.file.update(name='test_file_1.cfg', text=host_text, new_name='test_file_4.cfg')
    assert 'test_file_1.cfg' not in d.file.keys()
    assert 'test_file_4.cfg' in d.file.keys()
    d.close()


# def test_copy_file_from_host_to_device_1(dut, log_level):
#     dir_0 = ["""
#       588 -rw- Jun 10 2014 12:38:10  video.cfg
#       633 -rw- May 29 2014 12:34:00  voice.cfg
#       588 -rw- Apr 10 2014 08:10:02  default.cfg
#  16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
#      4647 -rw- Nov 18 2013 11:14:46  x210.cfg
#  16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
#   3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
#       735 -rw- Aug 23 2013 08:48:35  exception.log
# """]
#     dir_1 = ["""
#       588 -rw- Jun 10 2014 12:38:10  video-2.cfg
#       588 -rw- Jun 10 2014 12:38:10  video.cfg
#       633 -rw- May 29 2014 12:34:00  voice.cfg
#       588 -rw- Apr 10 2014 08:10:02  default.cfg
#  16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
#      4647 -rw- Nov 18 2013 11:14:46  x210.cfg
#  16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
#   3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
#       735 -rw- Aug 23 2013 08:48:35  exception.log
# """]
#     video_2_cfg_content = """
# !
# service password-encryption
# !
# no banner motd
# !
# username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
# !
# access-list 67 permit any
# !
# ssh server allow-users manager
# service ssh
# !
# service telnet
# !
# service http
# !
# no clock timezone
# !
# snmp-server
# snmp-server community public
# !
# aaa authentication enable default local
# aaa authentication login default local
# !
# ip domain-lookup
# !
# no service dhcp-server
# spanning-tree mode rstp
# !
# interface port1.0.1-1.0.24
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip address 10.17.39.253/24
# !
# line con 0
# line vty 0 4
# !
# end
# """
#     setup_dut(dut)
#     myfile = open('video-2.cfg', 'w')
#     myfile.write(video_2_cfg_content)
#     myfile.close()
#     host_path = os.getcwd() + '/' + 'video-2.cfg'
#     copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
#     dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
#     dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
#     dut.add_cmd({'cmd': 'dir'   , 'state':1, 'action':'PRINT','args': dir_1})
#     d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
#     d.open()
#     assert 'video-2.cfg' not in d.file.keys()
#     d.file.upload(host_path)
#     assert 'video-2.cfg' in d.file.keys()
#     d.close()
#
#
# def test_copy_file_from_host_to_device_2(dut, log_level):
#     dir_0 = ["""
#       588 -rw- Jun 10 2014 12:38:10  video-2.cfg
#       588 -rw- Jun 10 2014 12:38:10  video.cfg
#       633 -rw- May 29 2014 12:34:00  voice.cfg
#       588 -rw- Apr 10 2014 08:10:02  default.cfg
#  16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
#      4647 -rw- Nov 18 2013 11:14:46  x210.cfg
#  16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
#   3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
#       735 -rw- Aug 23 2013 08:48:35  exception.log
# """]
#     dir_1 = ["""
#       588 -rw- Jun 10 2014 12:39:44  video-2.cfg
#       588 -rw- Jun 10 2014 12:38:10  video.cfg
#       633 -rw- May 29 2014 12:34:00  voice.cfg
#       588 -rw- Apr 10 2014 08:10:02  default.cfg
#  16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
#      4647 -rw- Nov 18 2013 11:14:46  x210.cfg
#  16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
#   3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
#       735 -rw- Aug 23 2013 08:48:35  exception.log
# """]
#     video_2_cfg_content = """
# !
# service password-encryption
# !
# no banner motd
# !
# username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
# !
# access-list 67 permit any
# !
# ssh server allow-users manager
# service ssh
# !
# service telnet
# !
# service http
# !
# no clock timezone
# !
# snmp-server
# snmp-server community public
# !
# aaa authentication enable default local
# aaa authentication login default local
# !
# ip domain-lookup
# !
# no service dhcp-server
# spanning-tree mode rstp
# !
# interface port1.0.1-1.0.24
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip address 10.17.39.253/24
# !
# line con 0
# line vty 0 4
# !
# end
# """
#     setup_dut(dut)
#     myfile = open('video-2.cfg', 'w')
#     myfile.write(video_2_cfg_content)
#     myfile.close()
#     host_path = os.getcwd() + '/' + 'video-2.cfg'
#     copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
#     dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
#     dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
#     dut.add_cmd({'cmd': 'dir'   , 'state':1, 'action':'PRINT','args': dir_1})
#     d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
#     d.open()
#     assert 'video-2.cfg' in d.file.keys()
#     old_date = d.file['video-2.cfg']['mtime']
#     d.file.upload(host_path, overwrite=True)
#     assert old_date != d.file['video-2.cfg']['mtime']
#     d.close()
#
#
# def test_copy_file_from_host_to_device_3(dut, log_level):
#     dir_0 = ["""
#       588 -rw- Jun 10 2014 12:38:10  video-2.cfg
#       588 -rw- Jun 10 2014 12:38:10  video.cfg
#       633 -rw- May 29 2014 12:34:00  voice.cfg
#       588 -rw- Apr 10 2014 08:10:02  default.cfg
#  16654715 -rw- Jan 20 2014 15:28:41  x210-5.4.3-3.9.rel
#      4647 -rw- Nov 18 2013 11:14:46  x210.cfg
#  16629994 -rw- Oct  3 2013 09:56:13  x210-5.4.3-2.6.rel
#   3936572 -rw- Oct  3 2013 09:48:43  x210-gui_543_04.jar
#       735 -rw- Aug 23 2013 08:48:35  exception.log
# """]
#     video_2_cfg_content = """
# !
# service password-encryption
# !
# no banner motd
# !
# username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
# !
# access-list 67 permit any
# !
# ssh server allow-users manager
# service ssh
# !
# service telnet
# !
# service http
# !
# no clock timezone
# !
# snmp-server
# snmp-server community public
# !
# aaa authentication enable default local
# aaa authentication login default local
# !
# ip domain-lookup
# !
# no service dhcp-server
# spanning-tree mode rstp
# !
# interface port1.0.1-1.0.24
#  switchport
#  switchport mode access
# !
# interface vlan1
#  ip address 10.17.39.253/24
# !
# line con 0
# line vty 0 4
# !
# end
# """
#     setup_dut(dut)
#     myfile = open('video-2.cfg', 'w')
#     myfile.write(video_2_cfg_content)
#     myfile.close()
#     host_path = os.getcwd() + '/' + 'video-2.cfg'
#     copy_cmd = 'copy http://' + socket.gethostbyname(socket.getfqdn()) + host_path + ' video-2.cfg'
#     dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
#     dut.add_cmd({'cmd': copy_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
#     d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
#     d.open()
#     assert 'video-2.cfg' in d.file.keys()
#     with pytest.raises(KeyError) as excinfo:
#         d.file.upload(host_path)
#     assert 'file video-2.cfg cannot be overwritten' in excinfo.value
#     d.close()


def test_remove_file(dut, log_level):
    dir_0 = ["""
      588 -rw- Jun 10 2014 12:38:10  test_file_1.cfg
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
    dut.add_cmd({'cmd': 'dir'                   , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': 'delete test_file_1.cfg', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'                   , 'state':1, 'action':'PRINT','args': dir_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'test_file_1.cfg' in d.file.keys()
    d.file.delete("test_file_1.cfg")
    assert 'test_file_1.cfg' not in d.file.keys()
    d.close()
