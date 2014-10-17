import pytest
from pynetworking import Device


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
Serial number:
    """]})


def test_add_user(dut, log_level):
    config_0 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
"""]
    config_1 = ["""
interface range ethernet 1/e(1-16)
spanning-tree portfast
exit
interface vlan 1
ip address 10.17.39.252 255.255.255.0
name default_vlan
exit
hostname nac_dev
ip ssh server
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username operator password enemy level 1', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'operator' not in d.user.keys()
    d.user.create("operator", password="enemy", privilege_level=1)
    assert 'operator' in d.user.keys()
    assert d.user['operator']['privilege_level'] == '1'
    with pytest.raises(KeyError) as excinfo:
        d.user.create("", password="enemy", privilege_level=1)
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.create("operator", password="enemy", privilege_level=1)
    assert 'user name {0} already exists'.format('operator') in excinfo.value
    d.close()


def test_change_user_password(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password a5e3094ce553e08de5ba237525b106d5  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username operator password newpwd', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': 'username operator password enemy', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level)
    d.open()
    old_pwd = d.user['operator']['password']
    d.user.update("operator", password="newpwd")
    assert old_pwd != d.user['operator']['password']
    old_pwd = d.user['operator']['password']
    d.user.update("operator", password="enemy")
    assert old_pwd != d.user['operator']['password']
    old_pwd = d.user['operator']['password']
    with pytest.raises(KeyError) as excinfo:
        d.user.update("")
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.update("xxxxxxxxxxxxxxxx", password="newpwd")
    assert 'user name xxxxxxxxxxxxxxxx does not exist' in excinfo.value
    d.close()


def test_change_user_privilege(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d level 2 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username operator level 2', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': 'username operator level 1', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level)
    d.open()
    assert d.user['operator']['privilege_level'] == '1'
    d.user.update("operator", privilege_level=2)
    assert d.user['operator']['privilege_level'] == '2'
    d.user.update("operator", privilege_level=1)
    assert d.user['operator']['privilege_level'] == '1'
    d.close()


def test_remove_user(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username operator password cde2fde1fa1551a704d775ce2315915d  encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'no username operator', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level)
    d.open()
    d.user.delete("operator")
    with pytest.raises(KeyError):
        d.user['operator']
    d.close()


def test_encrypted_password(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username encuser password 0c88028bf3aa6a6a143ed846f2be1ea4 level 10 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
username encuser password c6009f08fc5fc6385f1ea1f5840e179f level 10 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]
    config_3 = ["""
!
service password-encryption
!
no banner motd
!
username manager password 3af00c6cad11f7ab5db4467b66ce503e level 15 encrypted
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.252/24
!
end
"""]

    usr = 'encuser'
    enc_pwd_1 = '0c88028bf3aa6a6a143ed846f2be1ea4'
    enc_pwd_2 = 'c6009f08fc5fc6385f1ea1f5840e179f'

    cmd_create = 'us ' + usr + ' p ' + enc_pwd_1 + ' l 10 e'
    cmd_update = 'us ' + usr + ' p ' + enc_pwd_2 + ' encrypted'

    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': cmd_create, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': cmd_update, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    dut.add_cmd({'cmd': 'no username encuser', 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 3, 'action': 'PRINT', 'args': config_3})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level)
    d.open()
    assert usr not in d.user.keys()
    d.user.create(usr, password=enc_pwd_1, privilege_level=10, encrypted=True)
    assert (usr, {'password': enc_pwd_1, 'privilege_level': '10'}) in d.user.items()
    d.user.update(usr, password=enc_pwd_2, encrypted=True)
    assert (usr, {'password': enc_pwd_2, 'privilege_level': '10'}) in d.user.items()
    d.user.delete(usr)
    with pytest.raises(KeyError):
        d.user[usr]
    with pytest.raises(KeyError) as excinfo:
        d.user.delete("")
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.delete("xxxxxxxxxxxxxxxx")
    assert 'user name xxxxxxxxxxxxxxxx does not exist' in excinfo.value
    d.close()
