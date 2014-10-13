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


def test_dns_crud(dut, log_level):
    output_c_0 = ["""
"""]
    output_h_0 = ["""
System Name:  nac_dev
Default domain:  Domain name is not configured



Name/address lookup is enable


Name servers (Preference order): Name server is not configured



"""]
    output_c_1 = ["""
ip name-server 10.17.39.11
"""]
    output_h_1 = ["""
System Name:  nac_dev
Default domain:  Domain name is not configured



Name/address lookup is enable


Name servers (Preference order): 10.17.39.11



"""]
    output_c_2 = ["""
ip domain-name com
ip name-server 10.17.39.11
"""]
    output_h_2 = ["""
System Name:  nac_dev
Default domain:  com


Name/address lookup is enable


Name servers (Preference order): 10.17.39.11
"""]
    output_c_3 = ["""
ip domain-name com
ip name-server 10.17.39.11 10.16.48.11
"""]
    output_h_3 = ["""
System Name:  nac_dev
Default domain:  com


Name/address lookup is enable


Name servers (Preference order): 10.17.39.11 10.16.48.11
"""]

    setup_dut(dut)

    dns_server_primary = '10.17.39.11'
    dns_server_secondary = '10.16.48.11'
    default_domain_name = 'com'

    create_cmd_1 = 'ip name-server {0}'.format(dns_server_primary)
    create_cmd_2 = 'ip domain-name {0}'.format(default_domain_name)
    create_cmd_3 = 'ip name-server {0}'.format(dns_server_secondary)
    delete_cmd_1 = 'no ip name-server {0}'.format(dns_server_secondary)
    delete_cmd_2 = 'no ip domain-name'
    delete_cmd_3 = 'no ip name-server {0}'.format(dns_server_primary)

    dut.add_cmd({'cmd': 'show running-config', 'state':0, 'action':'PRINT'    ,'args': output_c_0})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':0, 'action':'PRINT'    ,'args': output_h_0})
    dut.add_cmd({'cmd': create_cmd_1, 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config', 'state':1, 'action':'PRINT'    ,'args': output_c_1})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':1, 'action':'PRINT'    ,'args': output_h_1})
    dut.add_cmd({'cmd': create_cmd_2, 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config', 'state':2, 'action':'PRINT'    ,'args': output_c_2})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':2, 'action':'PRINT'    ,'args': output_h_2})
    dut.add_cmd({'cmd': create_cmd_3, 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config', 'state':3, 'action':'PRINT'    ,'args': output_c_3})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':3, 'action':'PRINT'    ,'args': output_h_3})
    dut.add_cmd({'cmd': delete_cmd_1, 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show running-config', 'state':4, 'action':'PRINT'    ,'args': output_c_2})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':4, 'action':'PRINT'    ,'args': output_h_2})
    dut.add_cmd({'cmd': delete_cmd_2, 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show running-config', 'state':5, 'action':'PRINT'    ,'args': output_c_1})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':5, 'action':'PRINT'    ,'args': output_h_1})
    dut.add_cmd({'cmd': delete_cmd_3, 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show running-config', 'state':6, 'action':'PRINT'    ,'args': output_c_0})
    dut.add_cmd({'cmd': 'show hosts'         , 'state':6, 'action':'PRINT'    ,'args': output_h_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create()
    assert dns_server_primary not in d.dns.keys()
    d.dns.create(name_servers=dns_server_primary)
    assert dns_server_primary in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(name_servers=dns_server_primary)

    assert default_domain_name not in d.dns.keys()
    d.dns.create(default_domain=default_domain_name)
    assert default_domain_name in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(default_domain=default_domain_name)
    assert d.dns[dns_server_primary]['static'] == True
    with pytest.raises(KeyError) as excinfo:
        assert d.dns['0.0.0.0']['static'] == True
    assert (dns_server_primary, {'static': True}) in d.dns.items()
    assert (default_domain_name, {'static': True}) in d.dns.items()

    d.dns.create(name_servers=dns_server_secondary)
    d.dns.delete(name_servers=dns_server_secondary)

    with pytest.raises(KeyError) as excinfo:
        d.dns.delete()
    d.dns.delete(default_domain=default_domain_name)
    assert default_domain_name not in d.dns.keys()
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(default_domain=default_domain_name)

    d.dns.delete(name_servers=dns_server_primary)
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(name_servers=dns_server_primary)
    assert dns_server_primary not in d.dns.keys()
    d.close()
