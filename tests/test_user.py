import pytest
from pynetworking.Device import Device


def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd': 'show version', 'state': -1, 'action': 'PRINT', 'args': ["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})


def test_add_user(dut, log_level, use_mock):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username testuser privilege 5 password enemy', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    assert 'testuser' not in d.user.keys()
    d.user.create("testuser", password="enemy", privilege_level=5)
    assert 'testuser' in d.user.keys()
    assert d.user['testuser']['privilege_level'] == '5'
    with pytest.raises(KeyError) as excinfo:
        d.user.create("", password="enemy", privilege_level=5)
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.create("testuser", password="enemy", privilege_level=5)
    assert 'user name {0} already exists'.format('testuser') in excinfo.value
    d.close()


def test_change_user_password(dut, log_level, use_mock):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ.
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username testuser password newpwd', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': 'username testuser password enemy', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    old_pwd = d.user['testuser']['password']
    d.user.update("testuser", password="newpwd")
    assert old_pwd != d.user['testuser']['password']
    old_pwd = d.user['testuser']['password']
    d.user.update("testuser", password="enemy")
    assert old_pwd != d.user['testuser']['password']
    old_pwd = d.user['testuser']['password']
    d.user.update("testuser", password="newpwd")
    with pytest.raises(KeyError) as excinfo:
        d.user.update("")
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.update("xxxxxxxxxxxxxxxx", password="newpwd")
    assert 'user name xxxxxxxxxxxxxxxx does not exist' in excinfo.value
    d.close()


def test_change_user_privilege(dut, log_level, use_mock):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username testuser privilege 1', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': 'username testuser privilege 5', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    assert d.user['testuser']['privilege_level'] == '5'
    d.user.update("testuser", privilege_level=1)
    assert d.user['testuser']['privilege_level'] == '1'
    d.user.update("testuser", privilege_level=5)
    assert d.user['testuser']['privilege_level'] == '5'
    d.close()


def test_remove_user(dut, log_level, use_mock):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username testuser privilege 5 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'no username testuser', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    d.user.delete("testuser")
    with pytest.raises(KeyError):
        d.user['testuser']
    d.close()


def test_encrypted_password(dut, log_level, use_mock):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_1 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username encuser privilege 10 password 8 $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_2 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
username encuser privilege 10 password 8 $1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ.
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]
    config_3 = ["""
!
service password-encryption
!
no banner motd
!
username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
!
ssh server allow-users manager
service ssh
!
interface port1.0.1-1.0.50
 switchport
 switchport mode access
!
interface vlan1
 ip address 10.17.39.253/24
!
end
"""]

    # Regular expressions are used. In emulated mode, if the password contains metacharacters like: . ^ $ * + ? { [ ] \ | ( )
    # prepone them a \ character, otherwise they won't match. Follow the example here below.
    enc_pwd_1 = '$1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/'
    enc_pwd_2 = '$1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ.'
    re_enc_pwd_1 = '\$1\$uWpWUKfS\$l0FbezBRUBllEpc8\.9kIF/'
    re_enc_pwd_2 = '\$1\$CEgGZi0q\$3JfHL/fM2F5YS47c/54ZQ\.'

    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config', 'state': 0, 'action': 'PRINT', 'args': config_0})
    dut.add_cmd({'cmd': 'username\s+encuser\s+privilege\s+10\s+password\s+8\s+' + re_enc_pwd_1, 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 1, 'action': 'PRINT', 'args': config_1})
    dut.add_cmd({'cmd': 'username\s+encuser\s+password\s+8\s+' + re_enc_pwd_2, 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 2, 'action': 'PRINT', 'args': config_2})
    dut.add_cmd({'cmd': 'no username encuser', 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'show running-config', 'state': 3, 'action': 'PRINT', 'args': config_3})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()
    assert 'encuser' not in d.user.keys()
    d.user.create("encuser", password=enc_pwd_1, privilege_level=10, encrypted=True)
    assert ('encuser', {'password': enc_pwd_1, 'privilege_level': '10'}) in d.user.items()
    d.user.update("encuser", password=enc_pwd_2, encrypted=True)
    assert ('encuser', {'password': enc_pwd_2, 'privilege_level': '10'}) in d.user.items()
    d.user.delete("encuser")
    with pytest.raises(KeyError):
        d.user['encuser']
    with pytest.raises(KeyError) as excinfo:
        d.user.delete("")
    assert 'user name cannot be empty' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        d.user.delete("xxxxxxxxxxxxxxxx")
    assert 'user name xxxxxxxxxxxxxxxx does not exist' in excinfo.value
    d.close()
