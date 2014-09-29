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
  address          ref clock       st  when  poll reach   delay  offset    disp
"""]
    output_1 = ["""
  address          ref clock       st  when  poll reach   delay  offset    disp
*~193.204.114.233  CTD              1     2    64   001    21.8    11.2  7937.5
"""]
    output_2 = ["""
  address          ref clock       st  when  poll reach   delay  offset    disp
*~193.204.114.233  CTD              1     2    64   001    21.8    11.2  7937.5
-~193.204.114.105  CTD              1    42    64   037    20.0    20.7     3.7
"""]
    setup_dut(dut)

    ntp1_address = '193.204.114.233'
    ntp2_address = '193.204.114.105'
    # ntp2_string_address = 'ntp.inrim.it'
    bad_ntp_address = '10.10.10.10.10'
    create_cmd_1 = 'ntp peer {0}'.format(ntp1_address)
    create_cmd_2 = 'ntp peer {0}'.format(ntp2_address)
    delete_cmd_1 = 'no ntp peer {0}'.format(ntp2_address)
    delete_cmd_2 = 'no ntp peer {0}'.format(ntp1_address)

    # Add the routes manually to have the NTP servers reachable:
    #
    #ip name-server 10.17.39.11
    #ip route 193.204.114.233/32 10.17.39.1
    #ip route 193.204.114.105/32 10.17.39.1
    #
    # Note that NTP server addresses are shown in the numeric form, even if they have been set in the literal one.


    dut.add_cmd({'cmd': 'show ntp associations', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1           , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show ntp associations', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': create_cmd_2           , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show ntp associations', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd_1           , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show ntp associations', 'state':3, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': delete_cmd_2           , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show ntp associations', 'state':4, 'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.ntp[bad_ntp_address]

    assert ntp1_address not in d.ntp.keys()
    d.ntp.create(ntp1_address)
    assert ntp1_address in d.ntp.keys()
    with pytest.raises(KeyError) as excinfo:
        d.ntp.create(ntp1_address)
    assert ntp2_address not in d.ntp.keys()
    d.ntp.create(ntp2_address)
    assert ntp2_address in d.ntp.keys()

    pt = d.ntp[ntp1_address]['polltime']
    st = d.ntp[ntp1_address]['status']
    assert (ntp1_address, {'polltime': pt, 'status': st}) in d.ntp.items()

    with pytest.raises(KeyError) as excinfo:
        d.ntp.delete(bad_ntp_address)
    d.ntp.delete(ntp2_address)
    assert ntp2_address not in d.ntp.keys()
    d.ntp.delete()
    assert ntp1_address not in d.ntp.keys()
    d.close()
