import pytest
import logging
import socket
import os
import tftpy
import threading
import getpass

from pynetworking import Device, DeviceException


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
Serial number:   1122334455
    """]})


def tftp_make_dir(tftp_client_dir, tftp_server_dir):
    if (os.path.exists(tftp_client_dir) == False):
        os.mkdir(tftp_client_dir)
    if (os.path.exists(tftp_server_dir) == False):
        os.mkdir(tftp_server_dir)


def tftp_server_for_ever(port, tftp_server_dir):
    ip_address = socket.gethostbyname(socket.getfqdn())
    server = tftpy.TftpServer(tftp_server_dir)
    # log_level = logging.DEBUG
    log_level = logging.WARNING
    log = logging.getLogger('tftpy')
    log.setLevel(log_level)
    server.listen(ip_address, port, timeout=20)


def setup_test_firmware_upgrade(dut, image_name):
    dut.tftp_port = 69
    if (dut.mode == 'emulated'):
        # Wait an answer from the device in case of reboot during emulation.
        dut.dontwait = False
        # Only root users can access port 69, that is mandatory for TFTP upload.
        # Normal users like Travis can rely on other ports but greater than 1024.
        if (getpass.getuser() != 'root'):
            dut.tftp_port = 20069
        # Create a dummy image file to be uploaded.
        myfile = open(image_name, 'w')
        myfile.write('1')
        myfile.close()
    else:
        # Don't wait an answer from the device in case of reboot.
        dut.dontwait = True
        # Only root users can access port 69, that is mandatory for TFTP upload.
        assert 'root' == getpass.getuser()

    client_dir = './tftp_client_dir'
    server_dir = './tftp_server_dir'
    tftp_make_dir(client_dir, server_dir)
    if not hasattr(dut, 'tftp_server_thread'):
        dut.tftp_server_thread = threading.Thread(target=tftp_server_for_ever, args=(dut.tftp_port, server_dir, ))
        dut.tftp_server_thread.daemon = True
        dut.tftp_server_thread.start()


def clean_test_firmware_upgrade(dut, image_name):
    if (dut.mode == 'emulated'):
        os.remove('tftp_client_dir/image')
        os.remove(image_name)
    os.rmdir('tftp_client_dir')
    os.remove('tftp_server_dir/' + image_name.split('/')[-1])
    os.rmdir('tftp_server_dir')


def test_facts_1(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")

    out_sys = """

Unit        Type
---- -------------------
 1


Unit     Up time
---- ---------------
 1     00,00:14:51

Unit number:   1
Serial Number:   1122334231
    """
    out_ver = """

        Unit             SW version         Boot version         HW version
------------------- ------------------- ------------------- -------------------
         1               3.0.0.44            1.0.1.07            00.01.00

    """

    setup_dut(dut)
    dut.add_cmd({'cmd':'show system' , 'state':0, 'action':'PRINT','args':[out_sys]})
    dut.add_cmd({'cmd':'show version', 'state':0, 'action':'PRINT','args':[out_ver]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    d.open()
    assert d.facts['model'] == 'not found'
    assert d.facts['unit_number'] == 'not found'
    assert d.facts['serial_number'] == 'not found'
    d.close()


def test_facts_2(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")

    out_sys = """

unit        type
---- -------------------
 1     AT-8000S/24


unit     up time
---- ---------------
 1     00,00:14:51

unit number:   1
serial nr:   1122334455
    """
    out_ver = """

        unit             sw version         boot version         hw version
------------------- ------------------- ------------------- -------------------
         1               3.0.0.44            1.0.1.07            00.01.00

    """

    setup_dut(dut)
    dut.add_cmd({'cmd':'show system' , 'state':0, 'action':'PRINT','args':[out_sys]})
    dut.add_cmd({'cmd':'show version', 'state':0, 'action':'PRINT','args':[out_ver]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level)
    with pytest.raises(DeviceException) as excinfo:
        d.open()
    d.close()


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


def test_firmware_upgrade(dut, log_level):
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
    setup_test_firmware_upgrade(dut, image_name)
    assert (os.path.exists(image_name) == True)
    assert (os.path.exists(false_image_name) == False)

    update_cmd = 'copy\s+tftp://{0}/{1}\s+image'.format(socket.gethostbyname(socket.getfqdn()), image_name)
    dut.add_cmd({'cmd': 'show bootvar', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': update_cmd    , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show bootvar', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level,connection_timeout=300)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware(filename=false_image_name, protocol='tftp', port=dut.tftp_port)
    with pytest.raises(KeyError) as excinfo:
        d.system.update_firmware(filename=image_name, port=dut.tftp_port)
    d.system.update_firmware(filename=image_name, protocol='tftp', port=dut.tftp_port, dontwait=dut.dontwait)
    if (dut.mode == 'emulated'):
        # Real devices will be rebooting here
        assert d.system._is_boot_bank_changed() == True
    d.close()

    clean_test_firmware_upgrade(dut, image_name)


def test_full_path_firmware_upgrade(dut, log_level):
    output_0 = ["""
Unit  Image  Filename   Version    Date                    Status
----  -----  ---------  ---------  ---------------------   -----------
1     1      image-1    3.0.0.44   02-Oct-2011  13:29:54   Active*
1     2      image-2    3.0.0.44   02-Oct-2011  13:29:54   Not active

"*" designates that the image was selected for the next boot

"""]
    output_1 = ["""
Unit  Image  Filename   Version    Date                    Status
----  -----  ---------  ---------  ---------------------   -----------
1     1      image-1    3.0.0.45   02-Oct-2011  13:31:37   Active
1     2      image-2    3.0.0.44   02-Oct-2011  13:29:54   Not active*

"*" designates that the image was selected for the next boot

"""]
    image_file = '8000s-5.4.3-3.9.rel'
    image_path = os.path.dirname(os.path.abspath(__file__)) + '/../examples/'
    image_name = image_path + image_file

    setup_dut(dut)
    setup_test_firmware_upgrade(dut, image_name)
    assert (os.path.exists(image_name) == True)

    update_cmd = 'copy\s+tftp://{0}/{1}\s+image'.format(socket.gethostbyname(socket.getfqdn()), image_file)
    dut.add_cmd({'cmd': 'show bootvar', 'state':0, 'action':'PRINT','args': output_0})
    dut.add_cmd({'cmd': update_cmd    , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'show bootvar', 'state':1, 'action':'PRINT','args': output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol,log_level=log_level,connection_timeout=300)
    d.open()
    d.system.update_firmware(filename=image_name, protocol='tftp', port=dut.tftp_port, dontwait=dut.dontwait)
    if (dut.mode == 'emulated'):
        # Real devices will be rebooting here
        assert d.system._is_boot_bank_changed() == True
    d.close()

    clean_test_firmware_upgrade(dut, image_name)
