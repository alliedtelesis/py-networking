import pytest
from pynetworking import Device


# On the real device, type the following to enable a default gateway if not present:
#
# nac_dev# conf
# nac_dev(config)# ip default-gateway 10.17.39.1
#


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

    # wait_time is just a trick to have the ping completed
    if dut.mode != 'emulated':
        dut.wait_time = 20000
    else:
        dut.wait_time = 1000


def test_dns_crud(dut, log_level):
    output_0 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
exit
ip default-gateway 10.17.39.1
hostname nac_dev
ip ssh server
"""]
    output_1 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
exit
ip default-gateway 10.17.39.1
hostname nac_dev
ip ssh server
ip name-server  10.17.39.11
"""]
    output_2 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
exit
ip default-gateway 10.17.39.1
hostname nac_dev
ip ssh server
ip domain-name com
ip name-server  10.17.39.11
"""]
    output_3 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
exit
ip default-gateway 10.17.39.1
hostname nac_dev
ip ssh server
ip domain-name com
ip name-server  10.17.39.11 10.16.48.11
"""]
    output_ping= ["""
Pinging ntp.inrim.it. (193.204.114.105) with 56 bytes of data:

56 bytes from 193.204.114.105: icmp_seq=1. time=40 ms
56 bytes from 193.204.114.105: icmp_seq=2. time=20 ms
56 bytes from 193.204.114.105: icmp_seq=3. time=20 ms
56 bytes from 193.204.114.105: icmp_seq=4. time=20 ms

----193.204.114.105 PING Statistics----
4 packets transmitted, 4 packets received, 0% packet loss
round-trip (ms) min/avg/max = 20/25/40
"""]

    setup_dut(dut)

    name_server_primary = '10.17.39.11'
    name_server_secondary = '10.16.48.11'
    name_server_list = [name_server_primary,name_server_secondary]
    name_comma_list = '{0},{1}'.format(name_server_primary, name_server_secondary)
    domain_name = 'com'
    host_ip = '193.204.114.105'
    host_name = 'ntp.inrim.it'

    create_cmd_1 = 'ip name-server {0}'.format(name_server_primary)
    create_cmd_2 = 'ip domain-name {0}'.format(domain_name)
    create_cmd_3 = 'ip name-server {0}'.format(name_server_secondary)
    ping_cmd = 'ping {0}'.format(host_name)
    delete_cmd_1 = 'no ip name-server {0}'.format(name_server_secondary)
    delete_cmd_2 = 'no ip domain-name'
    delete_cmd_3 = 'no ip name-server {0}'.format(name_server_primary)

    dut.add_cmd({'cmd': 'show running-config', 'state':0, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1         , 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config', 'state':1, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': create_cmd_2         , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config', 'state':2, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': create_cmd_3         , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config', 'state':3, 'action':'PRINT'    ,'args': output_3})
    dut.add_cmd({'cmd': ping_cmd             , 'state':3, 'action':'PRINT'    ,'args': output_ping})
    dut.add_cmd({'cmd': delete_cmd_1         , 'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show running-config', 'state':4, 'action':'PRINT'    ,'args': output_2})
    dut.add_cmd({'cmd': delete_cmd_2         , 'state':4, 'action':'SET_STATE','args':[5]})
    dut.add_cmd({'cmd': 'show running-config', 'state':5, 'action':'PRINT'    ,'args': output_1})
    dut.add_cmd({'cmd': delete_cmd_3         , 'state':5, 'action':'SET_STATE','args':[6]})
    dut.add_cmd({'cmd': 'show running-config', 'state':6, 'action':'PRINT'    ,'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1         , 'state':6, 'action':'SET_STATE','args':[7]})
    dut.add_cmd({'cmd': create_cmd_3         , 'state':7, 'action':'SET_STATE','args':[8]})
    dut.add_cmd({'cmd': 'show running-config', 'state':8, 'action':'PRINT'    ,'args': output_3})
    dut.add_cmd({'cmd': delete_cmd_1         , 'state':8, 'action':'SET_STATE','args':[9]})
    dut.add_cmd({'cmd': delete_cmd_3         , 'state':9, 'action':'SET_STATE','args':[10]})
    dut.add_cmd({'cmd': 'show running-config', 'state':10,'action':'PRINT'    ,'args': output_0})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create()
    assert d.dns['name_servers'] == ''
    d.dns.create(name_servers=name_server_primary)
    assert d.dns['name_servers'] == name_server_primary
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(name_servers=name_server_primary)

    assert d.dns['default_domain'] == ''
    d.dns.create(default_domain=domain_name)
    assert d.dns['default_domain'] == domain_name
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(default_domain=domain_name)

    assert 'default_domain' in d.dns.keys()
    assert ('default_domain', domain_name) in d.dns.items()
    with pytest.raises(KeyError) as excinfo:
        d.dns['domain_list'] == domain_name

    d.dns.create(name_servers=name_server_secondary)
    assert d.dns['name_servers'] == name_comma_list

    with pytest.raises(KeyError) as excinfo:
        d.dns.read('') == host_ip
    assert d.dns.read(host_name, wait_time=dut.wait_time) == host_ip

    d.dns.delete(name_servers=name_server_secondary)
    assert d.dns['name_servers'] == name_server_primary

    with pytest.raises(KeyError) as excinfo:
        d.dns.delete()
    d.dns.delete(default_domain=domain_name)
    assert d.dns['default_domain'] == ''
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(default_domain=domain_name)

    d.dns.delete(name_servers=name_server_primary)
    assert d.dns['name_servers'] == ''
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(name_servers=name_server_primary)

    d.dns.create(name_server_list)
    assert d.dns['name_servers'] == name_comma_list
    d.dns.delete(name_server_list)
    assert d.dns['name_servers'] == ''
    d.close()
