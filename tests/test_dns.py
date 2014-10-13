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


def test_dns_crud(dut, log_level):
    output_c_0 = ["""
"""]
    output_h_0 = ["""
Default domain is not set
Name/address lookup uses domain service
"""]
    output_c_1 = ["""
ip name-server 10.17.39.11
"""]
    output_h_1 = ["""
Default domain is not set
Name/address lookup uses domain service
Name servers are
10.17.39.11

"""]
    output_c_2 = ["""
ip domain-list com
ip name-server 10.17.39.11
"""]
    output_h_2 = ["""
Default domain is not set
Domain list: com
Name/address lookup uses domain service
Name servers are
10.17.39.11

"""]
    output_c_3 = ["""
ip domain-list com
ip name-server 10.17.39.11 10.16.48.11
"""]
    output_h_3 = ["""
Default domain is not set
Domain list: com
Name/address lookup uses domain service
Name servers are
10.17.39.11
10.16.48.11

"""]
    output_c_4 = ["""
ip domain-list com
ip name-server 10.17.39.11 10.16.48.11
"""]
    output_h_4 = ["""
Default domain is not set
Domain list: com
Name/address lookup uses domain service
Name servers are
10.17.39.11
10.16.48.11

"""]

    setup_dut(dut)

    name_server_primary = '10.17.39.11'
    name_server_secondary = '10.16.48.11'
    domain_name_primary = 'com'

    create_cmd_1 = 'ip name-server {0}'.format(name_server_primary)
    create_cmd_2 = 'ip domain-list {0}'.format(domain_name_primary)
    create_cmd_3 = 'ip name-server {0}'.format(name_server_secondary)
    delete_cmd_2 = 'no ip name-server {0}'.format(name_server_secondary)
    delete_cmd_3 = 'no ip domain-list {0}'.format(domain_name_primary)
    delete_cmd_4 = 'no ip name-server {0}'.format(name_server_primary)

    dut.add_cmd({'cmd': 'show running-config', 'state':0, 'action':'PRINT'    ,'args': output_c_0})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':0, 'action':'PRINT'    ,'args': output_h_0})
    dut.add_cmd({'cmd': create_cmd_1         , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config', 'state':1, 'action':'PRINT'    ,'args': output_c_1})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':1, 'action':'PRINT'    ,'args': output_h_1})
    dut.add_cmd({'cmd': create_cmd_2         , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config', 'state':2, 'action':'PRINT'    ,'args': output_c_2})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':2, 'action':'PRINT'    ,'args': output_h_2})
    dut.add_cmd({'cmd': create_cmd_3         , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config', 'state':3, 'action':'PRINT'    ,'args': output_c_3})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':3, 'action':'PRINT'    ,'args': output_h_3})
    dut.add_cmd({'cmd': create_cmd_4         , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show running-config', 'state':4, 'action':'PRINT'    ,'args': output_c_4})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':4, 'action':'PRINT'    ,'args': output_h_4})
    dut.add_cmd({'cmd': delete_cmd_1         , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show running-config', 'state':5, 'action':'PRINT'    ,'args': output_c_3})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':5, 'action':'PRINT'    ,'args': output_h_3})
    dut.add_cmd({'cmd': delete_cmd_2         , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show running-config', 'state':6, 'action':'PRINT'    ,'args': output_c_2})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':6, 'action':'PRINT'    ,'args': output_h_2})
    dut.add_cmd({'cmd': delete_cmd_3         , 'state':6, 'action':'SET_STATE','args':[7]})
    dut.add_cmd({'cmd': 'show running-config', 'state':7, 'action':'PRINT'    ,'args': output_c_1})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':7, 'action':'PRINT'    ,'args': output_h_1})
    dut.add_cmd({'cmd': delete_cmd_4         , 'state':7, 'action':'SET_STATE','args':[8]})
    dut.add_cmd({'cmd': 'show running-config', 'state':8, 'action':'PRINT'    ,'args': output_c_0})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':8, 'action':'PRINT'    ,'args': output_h_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create()
    assert name_server_primary not in d.dns.keys()
    d.dns.create(name_servers=name_server_primary)
    assert name_server_primary in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(name_servers=name_server_primary)

    assert domain_name_primary not in d.dns.keys()
    d.dns.create(default_domain=domain_name_primary)
    assert domain_name_primary in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(default_domain=domain_name_primary)
    assert d.dns[name_server_primary]['static'] == True
    with pytest.raises(KeyError) as excinfo:
        assert d.dns['0.0.0.0']['static'] == True
    assert (name_server_primary, {'static': True}) in d.dns.items()
    assert (domain_name_primary, {'static': True}) in d.dns.items()

    d.dns.create(name_servers=name_server_secondary)
    d.dns.delete(name_servers=name_server_secondary)

    with pytest.raises(KeyError) as excinfo:
        d.dns.delete()
    d.dns.delete(default_domain=domain_name_primary)
    assert domain_name_primary not in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(default_domain=domain_name_primary)

    d.dns.delete(name_servers=name_server_primary)
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(name_servers=name_server_primary)
    assert name_server_primary not in d.dns.keys()
    d.close()
