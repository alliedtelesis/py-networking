import pytest
import os
import socket
import tftpy
import threading
import getpass

from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey


# def http_server_for_ever(port):
#     http_client_dir = './http_client_dir'
#     if (os.path.exists(http_client_dir) == False):
#         os.mkdir(http_client_dir)
#     http_server_dir = './http_server_dir'
#     if (os.path.exists(http_server_dir) == False):
#         os.mkdir(http_server_dir)
#         ip_address = socket.gethostbyname(socket.getfqdn())
#         server = httpy.httpServer(http_server_dir)
#         server.listen(ip_address, port)
#
#
def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd':'show version',        'state':-1, 'action': 'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})


def test_download_image(dut, log_level):
    if (dut.mode == 'emulated'):
        if (os.path.exists('x210-5.4.3-99.99.rel') == True):
            os.remove('x210-5.4.3-99.99.rel')
        myfile = open('x210-5.4.3-3.9.rel','w')
        myfile.write('1')
        myfile.close()
        pytest.skip("only on real device")

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
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()

    assert 'x210-5.4.3-3.9.rel' in d.file.keys()
    m = d.file['x210-5.4.3-3.9.rel']['content']

    assert m != ''
    myfile = open('x210-5.4.3-3.9.rel','w')
    myfile.write(m)
    myfile.close()

    d.close()


def test_create_image_with_failures(dut, log_level):
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
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert (os.path.exists('x210-5.4.3-3.9.rel') == True)
    assert (os.path.exists('x210-5.4.3-99.99.rel') == False)
    assert 'x210-5.4.3-3.9.rel' in d.file.keys()
    assert 'x210-5.4.3-99.99.rel' not in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.sw_upgrade.create(name='x210-5.4.3-99.99.rel')
    with pytest.raises(KeyError) as excinfo:
        d.sw_upgrade.create(name='x210-5.4.3-3.9.rel')
    d.close()


def test_update_image_with_failures(dut, log_level):
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
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    os.rename('x210-5.4.3-3.9.rel', 'x210-5.4.3-99.99.rel')
    assert (os.path.exists('x210-5.4.3-3.9.rel') == False)
    assert (os.path.exists('x210-5.4.3-99.99.rel') == True)
    assert 'x210-5.4.3-3.9.rel' in d.file.keys()
    assert 'x210-5.4.3-99.99.rel' not in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.sw_upgrade.update(name='x210-5.4.3-3.9.rel')
    with pytest.raises(KeyError) as excinfo:
        d.sw_upgrade.update(name='x210-5.4.3-99.99.rel')
    os.rename('x210-5.4.3-99.99.rel', 'x210-5.4.3-3.9.rel')
    d.close()


def test_delete_image_with_failures(dut, log_level):
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
    dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'x210-5.4.3-99.99.rel' not in d.file.keys()
    with pytest.raises(KeyError) as excinfo:
        d.sw_upgrade.delete("x210-5.4.3-99.99.rel")
    d.close()


def test_create_image(dut, log_level):
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

    # myfile = open('temp_1.cfg', 'w')
    # myfile.write(host_text_1)
    # myfile.close()
    # myfile = open('temp_2.cfg', 'w')
    # myfile.write(host_text_2)
    # myfile.close()

    # remote_http_server = '10.17.39.119'
    # create_cmd = 'copy http://{0}/temp_1.cfg test_file_1.cfg'.format(remote_http_server)
    # update_cmd = 'copy http://{0}/temp_2.cfg test_file_1.cfg'.format(remote_http_server)
    local_http_server = socket.gethostbyname(socket.getfqdn())
    create_cmd = 'copy http://{0}/temp_1.cfg test_file_1.cfg'.format(local_http_server)
    # update_cmd = 'copy http://{0}/temp_2.cfg test_file_1.cfg'.format(local_http_server)
    # delete_cmd = 'delete test_file_1.cfg'
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': create_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    # dut.add_cmd({'cmd': update_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_2})
    # dut.add_cmd({'cmd': delete_cmd, 'state':2, 'action':'SET_STATE','args':[3]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':3, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    # assert 'test_file_1.cfg' not in d.file.keys()
    # d.file.create(name='test_file_1.cfg', port=dut.http_port, filename='temp_1.cfg')
    # # d.file.create(name='test_file_1.cfg', filename='temp_1.cfg',server=remote_http_server)
    # assert 'test_file_1.cfg' in d.file.keys()
    # assert d.file['test_file_1.cfg']['content'] == host_text_1
    # d.file.update(name='test_file_1.cfg', port=dut.http_port, filename='temp_2.cfg')
    # # d.file.update(name='test_file_1.cfg', filename='temp_2.cfg',server=remote_http_server)
    # assert 'test_file_1.cfg' in d.file.keys()
    # assert d.file['test_file_1.cfg']['content'] == host_text_2
    # d.file.delete('test_file_1.cfg')
    # assert 'test_file_1.cfg' not in d.file.keys()
    d.close()

    # os.remove('temp_1.cfg')
    # os.remove('temp_2.cfg')


def test_update_image(dut, log_level):
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
    local_http_server = socket.gethostbyname(socket.getfqdn())
    # create_cmd = 'copy http://{0}/test_file_2.cfg test_file_2.cfg'.format(local_http_server)
    update_cmd = 'copy http://{0}/test_file_2.cfg test_file_2.cfg'.format(local_http_server)
    # delete_cmd = 'delete test_file_2.cfg'
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': update_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    # dut.add_cmd({'cmd': update_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_2})
    # dut.add_cmd({'cmd': delete_cmd, 'state':2, 'action':'SET_STATE','args':[3]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':3, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    # assert 'test_file_2.cfg' not in d.file.keys()
    # d.file.create(name='test_file_2.cfg', port=dut.http_port, text=host_text_1)
    # assert 'test_file_2.cfg' in d.file.keys()
    # assert d.file['test_file_2.cfg']['content'] == host_text_1
    # d.file.update(name='test_file_2.cfg', port=dut.http_port, text=host_text_2)
    # assert 'test_file_2.cfg' in d.file.keys()
    # assert d.file['test_file_2.cfg']['content'] == host_text_2
    # d.file.delete('test_file_2.cfg')
    # assert 'test_file_2.cfg' not in d.file.keys()
    d.close()


def test_delete_image(dut, log_level):
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
    # local_http_server = socket.gethostbyname(socket.getfqdn())
    # create_cmd = 'copy http://{0}/test_file_3.cfg test_file_3.cfg'.format(local_http_server)
    # update_cmd = 'copy http://{0}/test_file_4.cfg test_file_4.cfg'.format(local_http_server)
    delete_cmd = 'delete test_file_4.cfg'
    dut.add_cmd({'cmd': 'dir'     , 'state':0, 'action':'PRINT','args': dir_0})
    dut.add_cmd({'cmd': delete_cmd, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'dir'     , 'state':1, 'action':'PRINT','args': dir_1})
    # dut.add_cmd({'cmd': update_cmd, 'state':1, 'action':'SET_STATE','args':[2]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':2, 'action':'PRINT','args': dir_2})
    # dut.add_cmd({'cmd': delete_cmd, 'state':2, 'action':'SET_STATE','args':[3]})
    # dut.add_cmd({'cmd': 'dir'     , 'state':3, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    # assert 'test_file_3.cfg' not in d.file.keys()
    # d.file.create(name='test_file_3.cfg', port=dut.http_port)
    # assert 'test_file_3.cfg' in d.file.keys()
    # mmdate = d.file['test_file_3.cfg']['mdate']
    # mmtime = d.file['test_file_3.cfg']['mtime']
    # assert ('test_file_3.cfg', {'size': '1', 'mdate': mmdate, 'permission': 'rw', 'mtime': mmtime}) in d.file.items()
    # d.file.update(name='test_file_3.cfg', port=dut.http_port, text=host_text, new_name='test_file_4.cfg')
    # assert 'test_file_3.cfg' not in d.file.keys()
    # assert 'test_file_4.cfg' in d.file.keys()
    # assert d.file['test_file_4.cfg']['content'] == host_text
    # d.file.delete("test_file_4.cfg")
    # assert 'test_file_4.cfg' not in d.file.keys()
    d.close()


def test_clean(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    os.remove('x210-5.4.3-3.9.rel')
