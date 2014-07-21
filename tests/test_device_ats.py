import pytest
import logging
import socket
import os
import tftpy
import threading
import getpass

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


def tftp_server_for_ever(port):
    tftp_client_dir = './tftp_client_dir'
    if (os.path.exists(tftp_client_dir) == False):
        os.mkdir(tftp_client_dir)
    tftp_server_dir = './tftp_server_dir'
    if (os.path.exists(tftp_server_dir) == False):
        os.mkdir(tftp_server_dir)
        ip_address = socket.gethostbyname(socket.getfqdn())
        server = tftpy.TftpServer(tftp_server_dir)
        # log_level = logging.DEBUG
        log_level = logging.WARNING
        log = logging.getLogger('tftpy')
        log.setLevel(log_level)
        server.listen(ip_address, port, timeout=10)


def setup_tftp_server(dut, image_name):
    dut.tftp_port = 69
    if (dut.mode == 'emulated'):
        if (getpass.getuser() != 'root'):
            dut.tftp_port = 20069
        myfile = open(image_name, 'w')
        myfile.write('1')
        myfile.close()
    else:
        assert 'root' == getpass.getuser()
    dut.tftp_server_thread = threading.Thread(target=tftp_server_for_ever, args=(dut.tftp_port,))
    dut.tftp_server_thread.daemon = True
    dut.tftp_server_thread.start()


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
    dut.add_cmd({'cmd': 'y'                  , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show running-config', 'state':4, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':4, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':4, 'action':'SET_PROMPT','args':['(config-vlan)#']})
    dut.add_cmd({'cmd': 'vlan database'      , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'no vlan 3999'       , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show running-config', 'state':6, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':6, 'action':'PRINT','args':[config_with_vlan]})
    dut.add_cmd({'cmd': 'copy r s'           , 'state':6, 'action':'SET_STATE','args':[7]})
    dut.add_cmd({'cmd': 'y'                  , 'state':7, 'action':'SET_STATE','args':[8]})
    dut.add_cmd({'cmd': 'show running-config', 'state':8, 'action':'PRINT','args':[config_no_vlan]})
    dut.add_cmd({'cmd': 'show startup-config', 'state':8, 'action':'PRINT','args':[config_no_vlan]})

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


def test_software_upgrade(dut, log_level):
    output_0 = ["""
Unit  Image  Filename   Version    Date                    Status
----  -----  ---------  ---------  ---------------------   -----------
1     1      image-1    3.0.0.44   02-Oct-2011  13:29:54   Not active
1     2      image-2    3.0.0.44   02-Oct-2011  13:29:54   Active*

"*" designates that the image was selected for the next boot

"""]
    output_1 = ["""
Unit  Image  Filename   Version    Date                    Status
----  -----  ---------  ---------  ---------------------   -----------
1     1      image-1    3.0.0.45   02-Oct-2011  13:31:37   Not active*
1     2      image-2    3.0.0.44   02-Oct-2011  13:29:54   Active

"*" designates that the image was selected for the next boot

"""]
    image_name = '8000s-5.4.3-3.9.rel'
    false_image_name = '8001s-5.4.3-3.9.rel'
    setup_dut(dut)
    setup_tftp_server(dut, image_name)
    local_tftp_server = socket.gethostbyname(socket.getfqdn())
    update_cmd = 'copy tftp://{0}/test_file_2.cfg image'.format(local_tftp_server)
    dut.add_cmd({'cmd': 'show bootvar', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': update_cmd    , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show bootvar', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert (os.path.exists(image_name) == True)
    assert (os.path.exists(false_image_name) == False)
    with pytest.raises(KeyError) as excinfo:
        d.system.update(release=false_image_name, port=dut.tftp_port)
    d.system.update(release=image_name, port=dut.tftp_port)
    d.close()

    if (dut.mode == 'emulated'):
        os.remove('tftp_client_dir/image')
        os.remove(image_name)
    os.rmdir('tftp_client_dir')
    os.remove('tftp_server_dir/' + image_name)
    os.rmdir('tftp_server_dir')
