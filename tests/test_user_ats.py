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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
"""]
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config'                     , 'state':0, 'action':'PRINT','args': config_0})
    dut.add_cmd({'cmd': 'username operator password enemy level 1', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config'                     , 'state':1, 'action':'PRINT','args': config_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'operator' not in d.user.keys()
    d.user.create("operator", password="enemy", privilege_level=1)
    assert 'operator' in d.user.keys()
    assert d.user['operator']['privilege_level'] == '1'
    d.close()


def test_change_user_password(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ. level 1 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
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
    dut.add_cmd({'cmd': 'show running-config'              , 'state':0, 'action':'PRINT','args': config_0})
    dut.add_cmd({'cmd': 'username operator password newpwd', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config'              , 'state':1, 'action':'PRINT','args': config_1})
    dut.add_cmd({'cmd': 'username operator password enemy' , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config'              , 'state':2, 'action':'PRINT','args': config_2})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    old_pwd = d.user['operator']['password']
    d.user.update("operator", password="newpwd")
    assert old_pwd != d.user['operator']['password']
    old_pwd = d.user['operator']['password']
    d.user.update("operator", password="enemy")
    assert old_pwd != d.user['operator']['password']
    old_pwd = d.user['operator']['password']
    d.close()


def test_change_user_privilege(dut, log_level):
    config_0 = ["""
!
service password-encryption
!
no banner motd
!
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 2 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
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
    dut.add_cmd({'cmd': 'show running-config'      , 'state':0, 'action':'PRINT','args': config_0})
    dut.add_cmd({'cmd': 'username operator level 2', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config'      , 'state':1, 'action':'PRINT','args': config_1})
    dut.add_cmd({'cmd': 'username operator level 1', 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config'      , 'state':2, 'action':'PRINT','args': config_2})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username operator password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 1 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
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
    dut.add_cmd({'cmd': 'show running-config' , 'state':0, 'action':'PRINT','args': config_0})
    dut.add_cmd({'cmd': 'no username operator', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config' , 'state':1, 'action':'PRINT','args': config_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username encuser password $1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/ level 10 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
username encuser password $1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ. level 10 encrypted
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
username manager password $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0 level 15 encrypted
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

    enc_pwd_1 = '$1$uWpWUKfS$l0FbezBRUBllEpc8.9kIF/'
    enc_pwd_2 = '$1$CEgGZi0q$3JfHL/fM2F5YS47c/54ZQ.'
    setup_dut(dut)
    dut.add_cmd({'cmd': 'show running-config'                                           , 'state':0, 'action':'PRINT','args': config_0})
    dut.add_cmd({'cmd': 'username encuser password ' + enc_pwd_1 + ' level 10 encrypted', 'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'show running-config'                                           , 'state':1, 'action':'PRINT','args': config_1})
    dut.add_cmd({'cmd': 'username encuser password ' + enc_pwd_2 + ' encrypted'         , 'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show running-config'                                           , 'state':2, 'action':'PRINT','args': config_2})
    dut.add_cmd({'cmd': 'no username encuser'                                           , 'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'show running-config'                                           , 'state':3, 'action':'PRINT','args': config_3})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert 'encuser' not in d.user.keys()
    d.user.create("encuser", password=enc_pwd_1, privilege_level=10, encrypted=True)
    assert ('encuser', {'password': enc_pwd_1, 'privilege_level': '10'}) in d.user.items()
    d.user.update("encuser", password=enc_pwd_2, encrypted=True)
    assert ('encuser', {'password': enc_pwd_2, 'privilege_level': '10'}) in d.user.items()
    d.user.delete("encuser")
    with pytest.raises(KeyError):
        d.user['encuser']
    d.close()


