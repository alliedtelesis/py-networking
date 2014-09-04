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


def test_create_update_delete_entry(dut, log_level):
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
1    port1.0.4    1a1b.1c1d.1e1f   forward   static
1    port1.0.4    2a2b.2c2d.2e2f   forward   static
1    port1.0.4    4a4b.4c4d.4e4f   forward   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_2 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
2    port1.0.5    0a0b.0c0d.0e0f   discard   static
2    port1.0.5    1a1b.1c1d.1e1f   discard   static
2    port1.0.5    2a2b.2c2d.2e2f   discard   static
2    port1.0.5    4a4b.4c4d.4e4f   forward   static
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]

    setup_dut(dut)

    mac1 = '0a0b0c0d0e0f'
    mac2 = '1a:1b:1c:1d:1e:1f'
    mac3 = '2a-2b-2c-2d-2e-2f'
    mac4 = '4a4b.4c4d.4e4f'
    dotted_mac1 = '0a0b.0c0d.0e0f'
    dotted_mac2 = '1a1b.1c1d.1e1f'
    dotted_mac3 = '2a2b.2c2d.2e2f'
    dotted_mac4 = mac4
    ifc = 'port1.0.4'
    ifu = 'port1.0.5'
    create_cmd_1 = 'mac address-table static ' + dotted_mac1 + ' forward interface ' + ifc + ' vlan 1'
    create_cmd_2 = 'mac address-table static ' + dotted_mac2 + ' forward interface ' + ifc + ' vlan 1'
    create_cmd_3 = 'mac address-table static ' + dotted_mac3 + ' forward interface ' + ifc + ' vlan 1'
    create_cmd_4 = 'mac address-table static ' + dotted_mac4 + ' forward interface ' + ifc + ' vlan 1'
    update_cmd_1 = 'mac address-table static ' + dotted_mac1 + ' discard interface ' + ifu + ' vlan 2'
    update_cmd_2 = 'mac address-table static ' + dotted_mac2 + ' discard interface ' + ifu + ' vlan 2'
    update_cmd_3 = 'mac address-table static ' + dotted_mac3 + ' discard interface ' + ifu + ' vlan 2'
    update_cmd_4 = 'mac address-table static ' + dotted_mac4 + ' forward interface ' + ifu + ' vlan 2'
    delete_cmd_1 = 'no mac address-table static ' + dotted_mac1 + ' discard interface ' + ifu + ' vlan 2'
    delete_cmd_2 = 'no mac address-table static ' + dotted_mac2 + ' discard interface ' + ifu + ' vlan 2'
    delete_cmd_3 = 'no mac address-table static ' + dotted_mac3 + ' discard interface ' + ifu + ' vlan 2'
    delete_cmd_4 = 'no mac address-table static ' + dotted_mac4 + ' discard interface ' + ifu + ' vlan 2'

    dut.add_cmd({'cmd': 'show mac address-table', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1            , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': create_cmd_2            , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': create_cmd_3            , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': create_cmd_4            , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':4, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': update_cmd_1            , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':5, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': update_cmd_2            , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':6, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': update_cmd_3            , 'state':6, 'action':'SET_STATE','args':[7]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':7, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': update_cmd_4            , 'state':7, 'action':'SET_STATE','args':[8]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':8, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd_1            , 'state':8, 'action':'SET_STATE','args':[9]})
    dut.add_cmd({'cmd': delete_cmd_2            , 'state':9, 'action':'SET_STATE','args':[10]})
    dut.add_cmd({'cmd': delete_cmd_3            , 'state':10,'action':'SET_STATE','args':[11]})
    dut.add_cmd({'cmd': delete_cmd_4            , 'state':11,'action':'SET_STATE','args':[12]})
    dut.add_cmd({'cmd': 'show mac address-table', 'state':12,'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert dotted_mac1 not in d.mac.keys()
    assert dotted_mac2 not in d.mac.keys()
    assert dotted_mac3 not in d.mac.keys()
    assert dotted_mac4 not in d.mac.keys()
    d.mac.create(mac1, ifc)
    d.mac.create(mac2, ifc)
    d.mac.create(mac3, ifc)
    d.mac.create(mac4, ifc)
    assert dotted_mac1 in d.mac.keys()
    assert dotted_mac2 in d.mac.keys()
    assert dotted_mac3 in d.mac.keys()
    assert dotted_mac4 in d.mac.keys()
    assert (dotted_mac1, {'vlan': '1', 'interface': ifc, 'action': 'forward', 'type': 'static'}) in d.mac.items()
    d.mac.update(mac1, ifu, forward=False, vlan=2)
    d.mac.update(mac2, ifu, forward=False, vlan=2)
    d.mac.update(mac3, ifu, forward=False, vlan=2)
    d.mac.update(mac4, ifu, forward=False, vlan=2)
    assert dotted_mac1 in d.mac.keys()
    assert dotted_mac2 in d.mac.keys()
    assert dotted_mac3 in d.mac.keys()
    assert dotted_mac4 in d.mac.keys()
    assert (dotted_mac1, {'vlan': '2', 'interface': ifu, 'action': 'discard', 'type': 'static'}) in d.mac.items()
    d.mac.delete(mac1)
    d.mac.delete(mac2)
    d.mac.delete(mac3)
    d.mac.delete(mac4)
    assert dotted_mac1 not in d.mac.keys()
    assert dotted_mac2 not in d.mac.keys()
    assert dotted_mac3 not in d.mac.keys()
    assert dotted_mac4 not in d.mac.keys()
    d.close()


def test_delete_all(dut, log_level):
    output_0 = ["""
VLAN port             mac            fwd
1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
1    port1.0.1    00c0.ee82.fa41   forward   dynamic
1    port1.0.1    1803.73b5.06ea   forward   dynamic
"""]
    output_1 = ["""
VLAN port             mac            fwd
"""]

    setup_dut(dut)

    dut.add_cmd({'cmd': 'show mac address-table' , 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': 'clear mac address-table', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show mac address-table' , 'state':1, 'action':'PRINT'    ,'args': output_1})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.mac.keys() != {}
    d.mac.delete()
    assert d.mac.keys() == {}
    d.close()
