# -*- coding: utf-8 -*-
import pytest
from pynetworking import Device
from time import sleep
from jinja2 import Template


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

    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    print dut.port
    d.open()
    print(d.interface)
    d.close()


