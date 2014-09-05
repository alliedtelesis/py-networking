import pytest
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


def test_nodots_mac_crud(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.4    0a0b.0c0d.0e0f   forward   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_2 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.5    0a0b.0c0d.0e0f   discard   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    setup_dut(dut)

    mac_address = '0a0b0c0d0e0f'
    missing_mac_address = '111111111111'
    wrong_mac_address = '1111;1111;1111'
    dotted_mac = '0a0b.0c0d.0e0f'
    ifc = 'port1.0.4'
    ifu = 'port1.0.5'
    create_cmd = 'mac address-table static ' + dotted_mac + ' forward interface ' + ifc + ' vlan 1'
    update_cmd = 'mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'
    delete_cmd = 'no mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'

    dut.add_cmd({'cmd': 'show mac address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd              , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': update_cmd              , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd              , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

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
    d.mac.update(mac_address, ifu, forward=False)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    with pytest.raises(KeyError) as excinfo:
        d.mac.update(missing_mac_address, ifu, forward=False)
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    with pytest.raises(KeyError) as excinfo:
        d.mac.delete(mac_address)
    with pytest.raises(KeyError) as excinfo:
        d.mac.delete('0000.cd1d.7eb0')
    d.close()


def test_colon_mac_crud(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.4    1a1b.1c1d.1e1f   discard   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_2 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.5    1a1b.1c1d.1e1f   discard   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    setup_dut(dut)

    mac_address = '1a:1b:1c:1d:1e:1f'
    dotted_mac = '1a1b.1c1d.1e1f'
    ifc = 'port1.0.4'
    ifu = 'port1.0.5'
    create_cmd = 'mac address-table static ' + dotted_mac + ' discard interface ' + ifc + ' vlan 1'
    update_cmd = 'mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'
    delete_cmd = 'no mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'

    dut.add_cmd({'cmd': 'show mac address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd              , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': update_cmd              , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd              , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc, forward=False)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu, forward=False)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_dashed_mac_crud(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.4    2a2b.2c2d.2e2f   forward   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_2 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.5    2a2b.2c2d.2e2f   discard   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    setup_dut(dut)

    mac_address = '2a-2b-2c-2d-2e-2f'
    dotted_mac = '2a2b.2c2d.2e2f'
    ifc = 'port1.0.4'
    ifu = 'port1.0.5'
    create_cmd = 'mac address-table static ' + dotted_mac + ' forward interface ' + ifc + ' vlan 1'
    update_cmd = 'mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'
    delete_cmd = 'no mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'

    dut.add_cmd({'cmd': 'show mac address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd              , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': update_cmd              , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd              , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu, forward=False)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_dotted_mac_crud(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.4    3a3b.3c3d.1e1f   forward   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_2 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.5    3a3b.3c3d.1e1f   discard   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    setup_dut(dut)

    mac_address = '3a3b.3c3d.1e1f'
    dotted_mac = mac_address
    ifc = 'port1.0.4'
    ifu = 'port1.0.5'
    create_cmd = 'mac address-table static ' + dotted_mac + ' forward interface ' + ifc + ' vlan 1'
    update_cmd = 'mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'
    delete_cmd = 'no mac address-table static ' + dotted_mac + ' discard interface ' + ifu + ' vlan 1'

    dut.add_cmd({'cmd': 'show mac address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd              , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': update_cmd              , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd              , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':3, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac not in d.mac.keys()
    d.mac.create(mac_address, ifc)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac_address, ifu, forward=False)
    assert dotted_mac in d.mac.keys()
    assert (dotted_mac, {'vlan': '1', 'interface': ifu, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac_address)
    assert dotted_mac not in d.mac.keys()
    d.close()


def test_delete_all(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.2    4a4b.4c4d.4e4f   forward   static
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]

    setup_dut(dut)

    mac_address = '4a4b.4c4d.4e4f'
    dotted_mac = mac_address
    ifc = 'port1.0.2'
    create_cmd = 'mac address-table static ' + dotted_mac + ' forward interface ' + ifc + ' vlan 1'

    dut.add_cmd({'cmd': 'show mac address-table'        , 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd                      , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table'        , 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': 'clear mac address-table static', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show mac address-table'        , 'state':2, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.mac.create(mac_address, ifc)
    assert d.mac._check_static_entry_presence() == True
    d.mac.delete()
    assert d.mac._check_static_entry_presence() == False
    d.close()
