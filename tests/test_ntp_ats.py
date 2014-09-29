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


def test_ntp_crud(dut, log_level):
    output_0 = ["""
"""]
    output_1 = ["""
"""]
    output_2 = ["""
"""]
    output_3 = ["""
"""]
    output_4 = ["""
"""]
    output_5 = ["""
"""]
    setup_dut(dut)

    ntp1_address = 'ntp.inrim.it'
    ntp2_address = '10.17.39.111'
    bad_ntp_address = '10.10.10.10.10'
    create_cmd_1 = 'ntp peer {0}'.format(ntp1_address)
    create_cmd_2 = 'ntp peer {0}'.format(ntp2_address)
    update_cmd_1 = 'ntp peer {0}'.format(ntp1_address)
    update_cmd_2 = 'ntp peer {0}'.format(ntp2_address)
    delete_cmd_1 = 'no ntp peer {0}'.format(ntp1_address)
    delete_cmd_2 = 'no ntp peer'

    dut.add_cmd({'cmd': 'show ntp status', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1     , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': create_cmd_2     , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': update_cmd_1     , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':3, 'action':'PRINT'    ,'args': output_3})
    dut.add_cmd({'cmd': update_cmd_2     , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':4, 'action':'PRINT'    ,'args': output_4})
    dut.add_cmd({'cmd': delete_cmd_1     , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':5, 'action':'PRINT'    ,'args': output_5})
    dut.add_cmd({'cmd': delete_cmd_2     , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show ntp status', 'state':6, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.ntp[bad_ntp_address]

    assert ntp1_address not in d.ntp.keys()
    d.ntp.create(ntp1_address)
    with pytest.raises(KeyError) as excinfo:
        d.ntp.create(ntp1_address)
    assert ntp1_address in d.ntp.keys()
    assert ntp2_address not in d.ntp.keys()
    d.ntp.create(ntp2_address, 120)
    assert ntp2_address in d.ntp.keys()

    with pytest.raises(KeyError) as excinfo:
        d.ntp.update(bad_ntp_address)
    d.ntp.update(ntp1_address, 240)
    assert ntp[ntp1_address][polltime] == 240
    d.ntp.update(ntp2_address)
    assert ntp[ntp2_address][polltime] == 60

    with pytest.raises(KeyError) as excinfo:
        d.ntp.delete(bad_ntp_address)
    d.ntp.delete(ntp1_address)
    assert ntp1_address not in d.ntp.keys()
    d.ntp.delete()
    assert ntp2_address not in d.ntp.keys()
    d.close()
