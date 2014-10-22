import pytest
from pynetworking import Device


# On the real device, type the following to enable a default gateway if not present:
#
# > enable
# # conf t
# (config)# ip route 0.0.0.0/0 10.17.39.1
#


def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd': 'show version', 'state': -1, 'action': 'PRINT', 'args': ["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})

    # wait_time is just a trick to have the ping completed
    if dut.mode != 'emulated':
        dut.wait_time = 20000
    else:
        dut.wait_time = 1000


def test_dns_crud(dut, log_level, use_mock):
    output_0 = ["""
"""]
    output_1 = ["""
ip name-server 10.17.39.11
"""]
    output_2 = ["""
ip domain-list com
ip name-server 10.17.39.11
"""]
    output_3 = ["""
ip domain-list com
ip name-server 10.17.39.11
ip name-server 10.16.48.11
"""]
    output_ping = ["""
PING ntp.inrim.it (193.204.114.105) 56(84) bytes of data.
64 bytes from ntp.ien.it (193.204.114.105): icmp_req=1 ttl=52 time=28.6 ms
64 bytes from ntp.inrim.it (193.204.114.105): icmp_req=2 ttl=52 time=21.2 ms
64 bytes from ntp.ien.it (193.204.114.105): icmp_req=3 ttl=52 time=24.7 ms
64 bytes from ntp.inrim.it (193.204.114.105): icmp_req=4 ttl=52 time=22.6 ms
64 bytes from ntp.ien.it (193.204.114.105): icmp_req=5 ttl=52 time=21.4 ms

--- ntp.inrim.it ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4005ms
rtt min/avg/max/mdev = 21.289/23.755/28.617/2.729 ms
"""]

    setup_dut(dut)

    name_server_primary = '10.17.39.11'
    name_server_secondary = '10.16.48.11'
    name_server_list = [name_server_primary, name_server_secondary]
    name_comma_list = '{0},{1}'.format(name_server_primary, name_server_secondary)
    domain_name = 'com'
    host_ip = '193.204.114.105'
    host_name = 'ntp.inrim.it'

    create_cmd_1 = 'ip name-server {0}'.format(name_server_primary)
    create_cmd_2 = 'ip domain-list {0}'.format(domain_name)
    create_cmd_3 = 'ip name-server {0}'.format(name_server_secondary)
    ping_cmd = 'ping {0}'.format(host_name)
    delete_cmd_1 = 'no ip name-server {0}'.format(name_server_secondary)
    delete_cmd_2 = 'no ip domain-list {0}'.format(domain_name)
    delete_cmd_3 = 'no ip name-server {0}'.format(name_server_primary)

    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': create_cmd_2, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': output_2})
    dut.add_cmd({'cmd': create_cmd_3, 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 3, 'action': 'PRINT', 'args': output_3})
    dut.add_cmd({'cmd': ping_cmd, 'state': 3, 'action': 'PRINT', 'args': output_ping})
    dut.add_cmd({'cmd': delete_cmd_1, 'state': 3, 'action': 'SET_STATE', 'args': [4]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 4, 'action': 'PRINT', 'args': output_2})
    dut.add_cmd({'cmd': delete_cmd_2, 'state': 4, 'action': 'SET_STATE', 'args': [5]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 5, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd_3, 'state': 5, 'action': 'SET_STATE', 'args': [6]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 6, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': create_cmd_1, 'state': 6, 'action': 'SET_STATE', 'args': [7]})
    dut.add_cmd({'cmd': create_cmd_3, 'state': 7, 'action': 'SET_STATE', 'args': [8]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 8, 'action': 'PRINT', 'args': output_3})
    dut.add_cmd({'cmd': delete_cmd_1, 'state': 8, 'action': 'SET_STATE', 'args': [9]})
    dut.add_cmd({'cmd': delete_cmd_3, 'state': 9, 'action': 'SET_STATE', 'args': [10]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 10, 'action': 'PRINT', 'args': output_0})

    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.dns.create()
    assert 'at least one parameter is mandatory' in excinfo.value
    assert d.dns['name_servers'] == ''
    d.dns.create(name_servers=name_server_primary)
    assert d.dns['name_servers'] == name_server_primary
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(name_servers=name_server_primary)
    assert 'default domain {0} already added'.format(name_server_primary) in excinfo.value

    assert d.dns['default_domain'] == ''
    d.dns.create(default_domain=domain_name)
    assert d.dns['default_domain'] == domain_name
    with pytest.raises(KeyError) as excinfo:
        d.dns.create(default_domain=domain_name)
    assert 'default domain {0} already added'.format(name_server_primary) in excinfo.value

    assert 'default_domain' in d.dns.keys()
    assert ('default_domain', domain_name) in d.dns.items()
    with pytest.raises(KeyError) as excinfo:
        d.dns['domain_list'] == domain_name
    assert 'entry domain_list does not exist' in excinfo.value

    d.dns.create(name_servers=name_server_secondary)
    assert d.dns['name_servers'] == name_comma_list

    with pytest.raises(KeyError) as excinfo:
        d.dns.read('') == host_ip
    assert 'hostname parameter is mandatory' in excinfo.value
    assert d.dns.read(host_name, wait_time=dut.wait_time) == host_ip

    d.dns.delete(name_servers=name_server_secondary)
    assert d.dns['name_servers'] == name_server_primary

    with pytest.raises(KeyError) as excinfo:
        d.dns.delete()
    assert 'at least one parameter is mandatory' in excinfo.value
    d.dns.delete(default_domain=domain_name)
    assert d.dns['default_domain'] == ''
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(default_domain=domain_name)
    assert 'default domain {0} not configured'.format(domain_name) in excinfo.value

    d.dns.delete(name_servers=name_server_primary)
    assert d.dns['name_servers'] == ''
    with pytest.raises(KeyError) as excinfo:
        d.dns.delete(name_servers=name_server_primary)
    assert 'DNS server {0} already deleted'.format(name_server_primary) in excinfo.value

    d.dns.create(name_server_list)
    assert d.dns['name_servers'] == name_comma_list
    d.dns.delete(name_server_list)
    assert d.dns['name_servers'] == ''
    d.close()
