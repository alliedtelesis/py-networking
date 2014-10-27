import pytest
from pynetworking.Device import Device


def setup_dut(dut):
    dut.reset()
    dut.prompt = '#'
    dut.add_cmd({'cmd': 'show version', 'state': -1, 'action': 'PRINT', 'args': ["""

        Unit             SW version         Boot version         HW version
------------------- ------------------- ------------------- -------------------
         1               3.0.0.44            1.0.1.07            00.01.00

    """]})
    dut.add_cmd({'cmd': 'show system', 'state': -1, 'action': 'PRINT', 'args': ["""

Unit        Type
---- -------------------
 1     AT-8000S/24


Unit     Up time
---- ---------------
 1     00,00:14:51

Unit Number:   1
Serial number:   1122334455
    """]})


def test_ntp_crud(dut, log_level, use_mock):
    # Get the SNTP servers reachable:  ip default-gateway 10.17.39.1
    # Give a DNS service:              ip name-server 10.17.39.11
    #
    # SNTP servers are:
    #  193.204.114.233  (ntp.inrim.it)
    #  193.204.114.105  (ntp.inrim2.it)
    #
    # Note that NTP server addresses are shown in the numeric form, even if they have been set in the literal one.

    output_r_c = ["""
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
vlan database
vlan 1
exit
!
clock source sntp
sntp unicast client enable
sntp server 83.64.124.251
!
end
"""]
    output_c_0 = ["""
Polling interval: 60 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_c_1 = ["""
Polling interval: 60 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_c_2 = ["""
Polling interval: 120 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_c_3 = ["""
Polling interval: 240 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_c_4 = ["""
Polling interval: 60 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_c_5 = ["""
Polling interval: 60 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]
    output_s_0 = ["""
Clock is not synchronized

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
"""]
    output_s_1 = ["""
Clock is synchronized, stratum 1, reference is 193.204.114.233, unicast

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.233    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]
    output_s_2 = ["""
Clock is synchronized, stratum 1, reference is 193.204.114.105, unicast

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.105    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
193.204.114.233    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]
    output_s_3 = ["""
Clock is synchronized, stratum 1, reference is 193.204.114.105, unicast

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.105    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
193.204.114.233    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]
    output_s_4 = ["""
Clock is synchronized, stratum 1, reference is 193.204.114.105, unicast

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.105    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
193.204.114.233    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]
    output_s_5 = ["""
Clock is not synchronized

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.233    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]

    setup_dut(dut)

    ntp_address_1 = '193.204.114.233'
    ntp_address_2 = '193.204.114.105'
    bad_ntp_address = '10.10.10.10.10'
    def_polltime = '60'
    polltime_1 = '120'
    polltime_2 = '240'
    create_cmd_1 = 'sntp server {0}'.format(ntp_address_1)
    create_cmd_2 = 'sntp server {0}'.format(ntp_address_2)
    update_cmd_1 = 'sntp client poll timer {0}'.format(polltime_2)
    update_cmd_2 = 'sntp client poll timer {0}'.format(def_polltime)
    delete_cmd_1 = 'no sntp server {0}'.format(ntp_address_2)
    delete_cmd_2 = 'no sntp server {0}'.format(ntp_address_1)

    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': output_r_c})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 0, 'action': 'PRINT', 'args': output_c_0})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 0, 'action': 'PRINT', 'args': output_s_0})
    dut.add_cmd({'cmd': create_cmd_1, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 1, 'action': 'PRINT', 'args': output_c_1})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 1, 'action': 'PRINT', 'args': output_s_1})
    dut.add_cmd({'cmd': create_cmd_2, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 2, 'action': 'PRINT', 'args': output_c_2})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 2, 'action': 'PRINT', 'args': output_s_2})
    dut.add_cmd({'cmd': update_cmd_1, 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 3, 'action': 'PRINT', 'args': output_c_3})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 3, 'action': 'PRINT', 'args': output_s_3})
    dut.add_cmd({'cmd': update_cmd_2, 'state': 3, 'action': 'SET_STATE', 'args': [4]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 4, 'action': 'PRINT', 'args': output_c_4})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 4, 'action': 'PRINT', 'args': output_s_4})
    dut.add_cmd({'cmd': delete_cmd_1, 'state': 4, 'action': 'SET_STATE', 'args': [5]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 5, 'action': 'PRINT', 'args': output_c_5})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 5, 'action': 'PRINT', 'args': output_s_5})
    dut.add_cmd({'cmd': delete_cmd_2, 'state': 5, 'action': 'SET_STATE', 'args': [6]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 6, 'action': 'PRINT', 'args': output_c_0})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 6, 'action': 'PRINT', 'args': output_s_0})

    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    with pytest.raises(KeyError) as excinfo:
        d.ntp[bad_ntp_address]
    assert 'SNTP server {0} is not present'.format(bad_ntp_address) in excinfo.value
    assert ntp_address_1 not in d.ntp.keys()
    d.ntp.create(ntp_address_1)
    with pytest.raises(KeyError) as excinfo:
        d.ntp.create(ntp_address_1)
    assert 'SNTP server {0} already added'.format(ntp_address_1) in excinfo.value
    assert ntp_address_1 in d.ntp.keys()
    assert ntp_address_2 not in d.ntp.keys()
    d.ntp.create(ntp_address_2, polltime_1)
    assert ntp_address_2 in d.ntp.keys()
    assert d.ntp[ntp_address_1]['polltime'] == polltime_1
    assert d.ntp[ntp_address_2]['polltime'] == polltime_1
    assert (ntp_address_1, {'polltime': polltime_1, 'status': 'up'}) in d.ntp.items()

    with pytest.raises(KeyError) as excinfo:
        d.ntp.update(bad_ntp_address)
    assert 'SNTP server {0} is not present'.format(bad_ntp_address) in excinfo.value
    d.ntp.update(ntp_address_1, polltime_2)
    assert d.ntp[ntp_address_1]['polltime'] == polltime_2
    assert d.ntp[ntp_address_2]['polltime'] == polltime_2
    d.ntp.update(ntp_address_2)
    assert d.ntp[ntp_address_1]['polltime'] == def_polltime
    assert d.ntp[ntp_address_2]['polltime'] == def_polltime

    with pytest.raises(KeyError) as excinfo:
        d.ntp.delete(bad_ntp_address)
    assert 'SNTP server {0} is not present'.format(bad_ntp_address) in excinfo.value
    d.ntp.delete(ntp_address_2)
    assert ntp_address_2 not in d.ntp.keys()
    d.ntp.delete()
    assert ntp_address_1 not in d.ntp.keys()
    d.close()

def test_ntp_host_name(dut, log_level, use_mock):
    # Add the routes manually to have the NTP servers reachable.
    #
    # ip route 0.0.0.0/0 10.17.39.1
    #
    # Note that NTP server addresses are shown in the numeric form, even if they have been set in the literal one.
    output_0 = ["""
Clock is not synchronized

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
"""]
    output_1 = ["""
Clock is synchronized, stratum 1, reference is 193.204.114.105, unicast

Unicast servers:

    Server       Status      Last Response     Offset   Delay
                                               [mSec]   [mSec]
--------------- --------- ------------------- --------- -------
193.204.114.105    up     09:44:04.0 UTC Sep    -9387      0
                          30 2014
"""]
    output_rc_0 = ["""
"""]
    output_rc_1 = ["""
ip name-server  10.17.39.11
"""]
    output_ping = ["""
Pinging ntp.inrim.it. (193.204.114.105) with 56 bytes of data:

56 bytes from 193.204.114.105: icmp_seq=1. time=40 ms
56 bytes from 193.204.114.105: icmp_seq=2. time=20 ms
56 bytes from 193.204.114.105: icmp_seq=3. time=20 ms
56 bytes from 193.204.114.105: icmp_seq=4. time=20 ms

----193.204.114.105 PING Statistics----
4 packets transmitted, 4 packets received, 0% packet loss
round-trip (ms) min/avg/max = 20/25/40
"""]
    output_cfg = ["""
Polling interval: 60 seconds.
No MD5 authentication keys.
Authentication is not required for synchronization.
No trusted keys.
"""]

    setup_dut(dut)

    name_server_primary = '10.17.39.11'
    ntp_host_name = 'ntp.inrim.it'

    adddns_cmd = 'ip name-server {0}'.format(name_server_primary)
    deldns_cmd = 'no ip name-server {0}'.format(name_server_primary)
    ping_cmd = 'ping {0}'.format(ntp_host_name)
    create_cmd = 'sntp server {0}'.format(ntp_host_name)
    # delete_cmd = 'no sntp server {0}'.format(ntp_host_name)
    delete_cmd = 'no sntp server 193.204.114.105'

    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': output_rc_0})
    dut.add_cmd({'cmd': adddns_cmd, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': output_rc_1})
    dut.add_cmd({'cmd': ping_cmd, 'state': 1, 'action': 'PRINT', 'args': output_ping})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 1, 'action': 'PRINT', 'args': output_cfg})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 1, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': create_cmd, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 2, 'action': 'PRINT', 'args': output_cfg})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 2, 'action': 'PRINT', 'args': output_1})
    dut.add_cmd({'cmd': delete_cmd, 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'show sntp config', 'state': 3, 'action': 'PRINT', 'args': output_cfg})
    dut.add_cmd({'cmd': 'show sntp status', 'state': 3, 'action': 'PRINT', 'args': output_0})
    dut.add_cmd({'cmd': 'show running-config', 'state': 3, 'action': 'PRINT', 'args': output_rc_1})
    dut.add_cmd({'cmd': deldns_cmd, 'state': 3, 'action': 'SET_STATE', 'args': [4]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 4, 'action': 'PRINT', 'args': output_rc_0})

    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    d.dns.create(name_servers=name_server_primary)
    assert d.dns['name_servers'] == name_server_primary
    ntp_ip_address = d.dns.read(ntp_host_name)
    assert '193.204.114.105' == ntp_ip_address

    assert ntp_ip_address not in d.ntp.keys()
    d.ntp.create(ntp_host_name)
    assert ntp_ip_address in d.ntp.keys()

    # d.ntp.delete(ntp_host_name)
    d.ntp.delete(ntp_ip_address)
    assert ntp_ip_address not in d.ntp.keys()

    d.dns.delete(name_servers=name_server_primary)
    d.close()
