# -*- coding: utf-8 -*-
import pytest
from pynetworking import Device
from time import sleep
from jinja2 import Template


ats_supported_sw_version = '3.0.0.44'
ats_supported_boot_version = '1.0.1.07'
ats_basic_supported_model = 'AT-8000S'
ats_supported_model = [ats_basic_supported_model + '/' + '24', ats_basic_supported_model + '/' + '48']
ats_model_port_number = 0
ats_total_port_number = 0

show_interface_header = """

                                               Flow    Admin     Back   Mdix
Port     Type         Duplex  Speed  Neg      control  State   Pressure Mode
-------- ------------ ------  -----  -------- -------  -----   -------- ----
"""


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


def test_show_system(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert (d.model in ats_supported_model)
    global ats_model_port_number
    ats_model_port_number = d.model[len(ats_basic_supported_model) + 1:]
    d.close()


def test_show_version(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    assert (d.sw_version == ats_supported_sw_version)
    d.close()


def test_get_interface(dut, log_level):
    if dut.mode != 'emulated':
        pytest.skip("only on emulated")
    setup_dut(dut)
    dut.add_cmd({'cmd':'show interfaces status', 'state':0, 'action':'PRINT','args':["""

                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
1/e1     100M-Copper  Full    100   Enabled  Off  Up          Disabled On     
1/e2     100M-Copper    --      --     --     --  Down           --     --    
1/e3     100M-Copper    --      --     --     --  Down           --     --    
1/e4     100M-Copper    --      --     --     --  Down           --     --    
1/e5     100M-Copper    --      --     --     --  Down           --     --    
1/e6     100M-Copper    --      --     --     --  Down           --     --    
1/e7     100M-Copper    --      --     --     --  Down           --     --    
1/e8     100M-Copper    --      --     --     --  Down           --     --    
1/e9     100M-Copper    --      --     --     --  Down           --     --    
1/e10    100M-Copper    --      --     --     --  Down           --     --    
1/e11    100M-Copper    --      --     --     --  Down           --     --    
1/e12    100M-Copper    --      --     --     --  Down           --     --    
1/e13    100M-Copper    --      --     --     --  Down           --     --    
1/e14    100M-Copper    --      --     --     --  Down           --     --    
1/e15    100M-Copper    --      --     --     --  Down           --     --    
1/e16    100M-Copper    --      --     --     --  Down           --     --    
1/e17    100M-Copper    --      --     --     --  Down           --     --    
1/e18    100M-Copper    --      --     --     --  Down           --     --    
1/e19    100M-Copper    --      --     --     --  Down           --     --    
1/e20    100M-Copper    --      --     --     --  Down           --     --    
1/e21    100M-Copper    --      --     --     --  Down           --     --    
1/e22    100M-Copper    --      --     --     --  Down           --     --    
1/e23    100M-Copper    --      --     --     --  Down           --     --    
1/e24    100M-Copper    --      --     --     --  Down           --     --    
1/e25         --        --      --     --     --  Not Present    --     --    
1/e26         --        --      --     --     --  Not Present    --     --    
1/e27         --        --      --     --     --  Not Present    --     --    
1/e28         --        --      --     --     --  Not Present    --     --    
1/e29         --        --      --     --     --  Not Present    --     --    
1/e30         --        --      --     --     --  Not Present    --     --    
1/e31         --        --      --     --     --  Not Present    --     --    
1/e32         --        --      --     --     --  Not Present    --     --    
1/e33         --        --      --     --     --  Not Present    --     --    
1/g1     1G-Combo-C     --      --     --     --  Down           --     --    
1/g2     1G-Combo-C     --      --     --     --  Down           --     --    
1/g3          --        --      --     --     --  Not Present    --     --    
1/g4          --        --      --     --     --  Not Present    --     --    
2/e1          --        --      --     --     --  Not Present    --     --    
2/e2          --        --      --     --     --  Not Present    --     --    
2/e3          --        --      --     --     --  Not Present    --     --    
    """]})

    dut.add_cmd({'cmd':'show interfaces configuration', 'state':0, 'action':'PRINT','args':["""
                                               Flow    Admin     Back   Mdix
Port     Type         Duplex  Speed  Neg      control  State   Pressure Mode
-------- ------------ ------  -----  -------- -------  -----   -------- ----
1/e1     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e2     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e3     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e4     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e5     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e6     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e7     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e8     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e9     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e10    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e11    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e12    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e13    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e14    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e15    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e16    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e17    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e18    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e19    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e20    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e21    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e22    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e23    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e24    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e25         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e26         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e27         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e28         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e29         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e30         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e31         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e32         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e33         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e34         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e35         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e36         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e37         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e38         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e39         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e40         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e41         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e42         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e43         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e44         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e45         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e46         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e47         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e48         --      Full      --   Enabled  Off      Up      Disabled Auto
1/g1     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g2     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g3          --      Full      --   Enabled  Off      Up      Disabled Auto
1/g4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e1          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e2          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e3          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e5          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e6          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e7          --      Full      --   Enabled  Off      Up      Disabled Auto
    """]})

    dut.add_cmd({'cmd':'show interfaces description', 'state':0, 'action':'PRINT','args':["""
Port      Description
-------   -----------
1/e1
1/e2
1/e3
1/e4      singleworddescription
1/e5
1/e6
1/e7
1/e8
1/e9
1/e10
1/e11
1/e12     some_description
1/e13
1/e14
1/e15
1/e16
1/e17
1/e18
1/e19
1/e20     some description
1/e21
1/e22
1/e23
1/e24
1/e25
1/e26
1/e27
1/e28
1/e29
1/e30
1/e31
1/e32
1/e33
1/e34
1/e35
1/e36
1/e37
1/e38
1/e39
1/e40
1/e41
1/e42
1/e43
1/e44
1/e45
1/e46
1/e47
1/e48
1/g1
1/g2
1/g3
1/g4
2/e1
2/e2
2/e3
    """]})

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()

    assert d.facts['os'] == 'ats'
    assert d.interface['1.0.4']['link'] == False
    assert d.interface['1.0.4']['description'] == 'singleworddescription'
    assert d.interface['1.0.12']['description'] == 'some_description'
    assert d.interface['1.0.20']['description'] == 'some description'

    ats_total_port_number = len(d.interface.keys())

    index_list = [1,8,24,25,26]

    for index in index_list:
        ref = '1.0.{0}'.format(index)
        assert d.interface[ref]['configured_duplex'] == 'full'
        assert d.interface[ref]['configured_polarity'] == 'auto'
        assert d.interface[ref]['enable'] == True
        assert d.interface[ref]['link'] == False

    for index in range(1,2):
        ref = '1.0.{0}'.format(index)
        assert d.interface[ref]['configured_speed'] == '100'

    for index in range(25,ats_total_port_number+1):
        ref = '1.0.{0}'.format(index)
        assert d.interface[ref]['configured_speed'] == '1000'

    print('There are {0} available ports'.format(ats_total_port_number))

    d.close()


def test_enable_interface(dut, log_level):
    if dut.mode != 'emulated':
       pytest.skip("only on emulated")
    setup_dut(dut)
    show_interface = show_interface_header
# 1/e1     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
    for interface in range(1,int(ats_model_port_number)+1):
        entry = '1/e%-2d    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto\n' % (interface)
        show_interface += entry

    dut.add_cmd({'cmd': 'show interfaces configuration',       'state':0, 'action':'PRINT','args':[show_interface]})

    print('\nAdd here code to test enabling and disabling of interfaces')

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()

    d.close()

def test_update_description(dut, log_level):
    setup_dut(dut)
    dut.add_cmd({'cmd':'show interfaces status', 'state':-1, 'action':'PRINT','args':["""

                                             Flow Link          Back   Mdix
Port     Type         Duplex  Speed Neg      ctrl State       Pressure Mode
-------- ------------ ------  ----- -------- ---- ----------- -------- -------
1/e1     100M-Copper  Full    100   Enabled  Off  Up          Disabled On
1/e2     100M-Copper    --      --     --     --  Down           --     --
1/e3     100M-Copper    --      --     --     --  Down           --     --
1/e4     100M-Copper    --      --     --     --  Down           --     --
1/e5     100M-Copper    --      --     --     --  Down           --     --
1/e6     100M-Copper    --      --     --     --  Down           --     --
1/e7     100M-Copper    --      --     --     --  Down           --     --
1/e8     100M-Copper    --      --     --     --  Down           --     --
1/e9     100M-Copper    --      --     --     --  Down           --     --
1/e10    100M-Copper    --      --     --     --  Down           --     --
1/e11    100M-Copper    --      --     --     --  Down           --     --
1/e12    100M-Copper    --      --     --     --  Down           --     --
1/e13    100M-Copper    --      --     --     --  Down           --     --
1/e14    100M-Copper    --      --     --     --  Down           --     --
1/e15    100M-Copper    --      --     --     --  Down           --     --
1/e16    100M-Copper    --      --     --     --  Down           --     --
1/e17    100M-Copper    --      --     --     --  Down           --     --
1/e18    100M-Copper    --      --     --     --  Down           --     --
1/e19    100M-Copper    --      --     --     --  Down           --     --
1/e20    100M-Copper    --      --     --     --  Down           --     --
1/e21    100M-Copper    --      --     --     --  Down           --     --
1/e22    100M-Copper    --      --     --     --  Down           --     --
1/e23    100M-Copper    --      --     --     --  Down           --     --
1/e24    100M-Copper    --      --     --     --  Down           --     --
1/e25         --        --      --     --     --  Not Present    --     --
1/e26         --        --      --     --     --  Not Present    --     --
1/e27         --        --      --     --     --  Not Present    --     --
1/e28         --        --      --     --     --  Not Present    --     --
1/e29         --        --      --     --     --  Not Present    --     --
1/e30         --        --      --     --     --  Not Present    --     --
1/e31         --        --      --     --     --  Not Present    --     --
1/e32         --        --      --     --     --  Not Present    --     --
1/e33         --        --      --     --     --  Not Present    --     --
1/g1     1G-Combo-C     --      --     --     --  Down           --     --
1/g2     1G-Combo-C     --      --     --     --  Down           --     --
1/g3          --        --      --     --     --  Not Present    --     --
1/g4          --        --      --     --     --  Not Present    --     --
2/e1          --        --      --     --     --  Not Present    --     --
2/e2          --        --      --     --     --  Not Present    --     --
2/e3          --        --      --     --     --  Not Present    --     --
    """]})

    dut.add_cmd({'cmd':'show interfaces configuration', 'state':-1, 'action':'PRINT','args':["""
                                               Flow    Admin     Back   Mdix
Port     Type         Duplex  Speed  Neg      control  State   Pressure Mode
-------- ------------ ------  -----  -------- -------  -----   -------- ----
1/e1     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e2     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e3     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e4     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e5     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e6     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e7     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e8     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e9     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e10    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e11    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e12    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e13    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e14    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e15    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e16    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e17    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e18    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e19    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e20    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e21    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e22    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e23    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e24    100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
1/e25         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e26         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e27         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e28         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e29         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e30         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e31         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e32         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e33         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e34         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e35         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e36         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e37         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e38         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e39         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e40         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e41         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e42         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e43         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e44         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e45         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e46         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e47         --      Full      --   Enabled  Off      Up      Disabled Auto
1/e48         --      Full      --   Enabled  Off      Up      Disabled Auto
1/g1     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g2     1G-Combo-C   Full    1000   Enabled  Off      Up      Disabled Auto
1/g3          --      Full      --   Enabled  Off      Up      Disabled Auto
1/g4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e1          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e2          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e3          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e4          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e5          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e6          --      Full      --   Enabled  Off      Up      Disabled Auto
2/e7          --      Full      --   Enabled  Off      Up      Disabled Auto
    """]})

    dut.add_cmd({'cmd':'show interfaces description', 'state':0, 'action':'PRINT','args':["""
Port      Description
-------   -----------
1/e1
1/e2
1/e3
1/e4      singleworddescription
1/e5
1/e6
1/e7
1/e8
1/e9
1/e10
1/e11
1/e12     some_description
1/e13
1/e14
1/e15
1/e16
1/e17
1/e18
1/e19
1/e20     some description
1/e21
1/e22
1/e23
1/e24
1/e25
1/e26
1/e27
1/e28
1/e29
1/e30
1/e31
1/e32
1/e33
1/e34
1/e35
1/e36
1/e37
1/e38
1/e39
1/e40
1/e41
1/e42
1/e43
1/e44
1/e45
1/e46
1/e47
1/e48
1/g1
1/g2
1/g3
1/g4
2/e1
2/e2
2/e3
    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/e18',         'state':0, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/e18',         'state':0, 'action':'SET_STATE','args':[1]})
    dut.add_cmd({'cmd': 'description "test description"',   'state':1, 'action':'SET_STATE','args':[2]})
    dut.add_cmd({'cmd': 'show interfaces description',      'state':2, 'action':'PRINT','args':["""
Port      Description
-------   -----------
1/e1
1/e2
1/e3
1/e4      singleworddescription
1/e5
1/e6
1/e7
1/e8
1/e9
1/e10
1/e11
1/e12     some_description
1/e13
1/e14
1/e15
1/e16
1/e17
1/e18     test description
1/e19
1/e20     some description
1/e21
1/e22
1/e23
1/e24
1/e25
1/e26
1/e27
1/e28
1/e29
1/e30
1/e31
1/e32
1/e33
1/e34
1/e35
1/e36
1/e37
1/e38
1/e39
1/e40
1/e41
1/e42
1/e43
1/e44
1/e45
1/e46
1/e47
1/e48
1/g1
1/g2
1/g3
1/g4
2/e1
2/e2
2/e3
    """]})
    dut.add_cmd({'cmd': 'interface ethernet 1/g1',          'state':2, 'action':'SET_PROMPT','args':['(config-if)#']})
    dut.add_cmd({'cmd': 'interface ethernet 1/g1',          'state':2, 'action':'SET_STATE','args':[3]})
    dut.add_cmd({'cmd': 'description test_description',     'state':3, 'action':'SET_STATE','args':[4]})
    dut.add_cmd({'cmd': 'show interfaces description',      'state':4, 'action':'PRINT','args':["""
Port      Description
-------   -----------
1/e1
1/e2
1/e3
1/e4      singleworddescription
1/e5
1/e6
1/e7
1/e8
1/e9
1/e10
1/e11
1/e12     some_description
1/e13
1/e14
1/e15
1/e16
1/e17
1/e18     test description
1/e19
1/e20     some description
1/e21
1/e22
1/e23
1/e24
1/e25
1/e26
1/e27
1/e28
1/e29
1/e30
1/e31
1/e32
1/e33
1/e34
1/e35
1/e36
1/e37
1/e38
1/e39
1/e40
1/e41
1/e42
1/e43
1/e44
1/e45
1/e46
1/e47
1/e48
1/g1      test_description
1/g2
1/g3
1/g4
2/e1
2/e2
2/e3
    """]})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.interface.update('1.0.18',description='test description')
    assert d.interface['1.0.18']['description'] == 'test description'
    d.interface.update('1.0.25',description='test_description')
    assert d.interface['1.0.25']['description'] == 'test_description'
    d.close()