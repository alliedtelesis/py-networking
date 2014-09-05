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
Serial number:   1122334455
    """]})


def test_nodots_mac_crud(dut, log_level):
    output_0 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_1 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       0a:0b:0c:0d:0e:0f    1/e6   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_2 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       0a:0b:0c:0d:0e:0f    1/e9   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    setup_dut(dut)

    mac_address = '0a0b0c0d0e0f'
    new_mac_addr = '0a0b0c0deeff'
    dyn_mac_addr = '00:00:cd:24:04:8b'
    missing_mac_address = '111111111111'
    wrong_mac_address = '1111;1111;1111'
    dotted_mac = '0a0b.0c0d.0e0f'
    ifc = '1/e6'
    ifu = '1/e9'
    create_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifc + ' permanent'
    update_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifu + ' permanent'
    delete_cmd = 'no bridge address ' + dotted_mac

    dut.add_cmd({'cmd': 'show bridge address-table', 'state':0, 'action':'PRINT'     ,'args': output_0})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': create_cmd                 , 'state':0, 'action':'SET_STATE' ,'args':[1]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':1, 'action':'PRINT'     ,'args': output_1})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':1, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': update_cmd                 , 'state':1, 'action':'SET_STATE' ,'args':[2]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':2, 'action':'PRINT'     ,'args': output_2})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': delete_cmd                 , 'state':2, 'action':'SET_STATE' ,'args':[3]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':3, 'action':'PRINT'     ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.mac[missing_mac_address]
    with pytest.raises(KeyError) as excinfo:
        d.mac.create(wrong_mac_address, ifc)
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    with pytest.raises(KeyError) as excinfo:
        d.mac.create(mac_address, ifc)
    with pytest.raises(KeyError) as excinfo:
        d.mac.create(new_mac_addr, ifu, forward=False)

    with pytest.raises(KeyError) as excinfo:
        d.mac.update(mac_address, ifu, forward=False)
    with pytest.raises(KeyError) as excinfo:
        d.mac.update(missing_mac_address, ifu)
    d.mac.update(mac_address, ifu)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'forward', 'type': 'static'}) in d.mac.items()

    with pytest.raises(KeyError) as excinfo:
        d.mac.delete(missing_mac_address)
    with pytest.raises(KeyError) as excinfo:
        d.mac.delete(dyn_mac_addr)
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    with pytest.raises(KeyError) as excinfo:
        d.mac.delete('0000.cd1d.7eb0')
    d.close()


def test_colon_mac_crud(dut, log_level):
    output_0 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_1 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       1a:1b:1c:1d:1e:1f    1/e6   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_2 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       1a:1b:1c:1d:1e:1f    1/e9   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    setup_dut(dut)

    mac_address = '1a:1b:1c:1d:1e:1f'
    dotted_mac = '1a1b.1c1d.1e1f'
    ifc = '1/e6'
    ifu = '1/e9'
    create_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifc + ' permanent'
    update_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifu + ' permanent'
    delete_cmd = 'no bridge address ' + dotted_mac

    dut.add_cmd({'cmd': 'show bridge address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': create_cmd                 , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':1, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': update_cmd                 , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': delete_cmd                 , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_dashed_mac_crud(dut, log_level):
    output_0 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_1 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       2a:2b:2c:2d:2e:2f    1/e6   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_2 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       2a:2b:2c:2d:2e:2f    1/e9   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    setup_dut(dut)

    mac_address = '2a-2b-2c-2d-2e-2f'
    dotted_mac = '2a2b.2c2d.2e2f'
    ifc = '1/e6'
    ifu = '1/e9'
    create_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifc + ' permanent'
    update_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifu + ' permanent'
    delete_cmd = 'no bridge address ' + dotted_mac

    dut.add_cmd({'cmd': 'show bridge address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': create_cmd                 , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':1, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': update_cmd                 , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': delete_cmd                 , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_dotted_mac_crud(dut, log_level):
    output_0 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_1 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       3a:3b:3c:3d:3e:3f    1/e6   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_2 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       3a:3b:3c:3d:3e:3f    1/e9   static
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    setup_dut(dut)

    mac_address = '3a3b.3c3d.3e3f'
    dotted_mac = mac_address
    ifc = '1/e6'
    ifu = '1/e9'
    create_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifc + ' permanent'
    update_cmd = 'bridge address ' + dotted_mac + ' ethernet ' + ifu + ' permanent'
    delete_cmd = 'no bridge address ' + dotted_mac

    dut.add_cmd({'cmd': 'show bridge address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd                 , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':1, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': update_cmd                 , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': 'interface vlan 1'         , 'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': delete_cmd                 , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_delete_all(dut, log_level):
    output_0 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
   1       00:00:cd:24:04:8b    1/e1   dynamic
   1       00:00:cd:37:0a:d3    1/e1   dynamic
"""]
    output_1 = ["""
Aging time is 300 sec

  Vlan        Mac Address       Port     Type
-------- --------------------- ------ ----------
"""]

    setup_dut(dut)

    dut.add_cmd({'cmd': 'show bridge address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': 'clear bridge'             , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show bridge address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.mac.keys() != []
    d.mac.delete()
    assert d.mac.keys() == []
    d.close()
