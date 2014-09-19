import pytest
import os
import socket
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey
from datetime import datetime, timedelta
from pytz import timezone
import pytz

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


def test_update(dut, log_level):
    clock_output_0 = ["""
UTC Time:   Thu, 18 Sep 2014 14:19:21 +0000
Timezone: UTC
Timezone Offset: +00:00
Summer time zone: None
"""]
    clock_output_1 = ["""
Local Time: Fri, 19 Sep 2014 12:02:07 +0300
UTC Time:   Fri, 19 Sep 2014 09:02:07 +0000
Timezone: CEST
Timezone Offset: +02:00
Summer time zone: CEST
Summer time starts: Last Sunday in March at 02:00:00
Summer time ends: Last Sunday in October at 03:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_2 = ["""
Local Time: Fri, 19 Sep 2014 07:02:41 -0200
UTC Time:   Fri, 19 Sep 2014 09:02:41 +0000
Timezone: UYT
Timezone Offset: -03:00
Summer time zone: UYT
Summer time starts: First Sunday in October at 02:00:00
Summer time ends: Second Sunday in March at 02:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_3 = ["""
Local Time: Fri, 19 Sep 2014 19:03:30 +1000
UTC Time:   Fri, 19 Sep 2014 09:03:30 +0000
Timezone: AEST
Timezone Offset: +10:00
Summer time zone: AEST
Summer time starts: First Sunday in October at 02:00:00
Summer time ends: First Sunday in April at 03:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_4 = ["""
Local Time: Fri, 19 Sep 2014 06:03:56 -0300
UTC Time:   Fri, 19 Sep 2014 09:03:56 +0000
Timezone: EDT
Timezone Offset: -04:00
Summer time zone: EDT
Summer time starts: Second Sunday in March at 02:00:00
Summer time ends: First Sunday in November at 02:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_5 = ["""
Local Time: Fri, 19 Sep 2014 17:04:20 +0800
UTC Time:   Fri, 19 Sep 2014 09:04:20 +0000
Timezone: CST
Timezone Offset: +08:00
Summer time zone: None
"""]

    setup_dut(dut)

    dt = datetime.now()

    tz1 = timezone('Europe/Rome')
    tz2 = timezone('America/Montevideo')
    tz3 = timezone('Australia/Sydney')
    tz4 = timezone('America/New_York')
    tz5 = timezone('Asia/Shanghai')

    dut.add_cmd({'cmd': 'show clock'                  , 'state':0, 'action':'PRINT','args': clock_output_0})
    dut.add_cmd({'cmd': 'clock timezone 2 zone CEST'  , 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'clock su r 5 sun mar 2:00 5 sun oct 3:00 o 60 z CEST', 'state':1, 'action':'SET_STATE','args': [2]})
    dut.add_cmd({'cmd': 'show clock'                  , 'state':2, 'action':'PRINT','args': clock_output_1})
    dut.add_cmd({'cmd': 'clock timezone -3 zone UYT'  , 'state':2, 'action':'SET_STATE','args': [3]})
    dut.add_cmd({'cmd': 'clock su r 1 sun oct 2:00 2 sun mar 2:00 o 60 z UYT' , 'state':3, 'action':'SET_STATE','args': [4]})
    dut.add_cmd({'cmd': 'show clock'                  , 'state':4, 'action':'PRINT','args': clock_output_2})
    dut.add_cmd({'cmd': 'clock timezone 10 zone AEST' , 'state':4, 'action':'SET_STATE','args': [5]})
    dut.add_cmd({'cmd': 'clock su r 1 sun oct 2:00 1 sun apr 3:00 o 60 z AEST', 'state':5, 'action':'SET_STATE','args': [6]})
    dut.add_cmd({'cmd': 'show clock'                  , 'state':6, 'action':'PRINT','args': clock_output_3})
    dut.add_cmd({'cmd': 'clock timezone -4 zone EDT'  , 'state':6, 'action':'SET_STATE','args': [7]})
    dut.add_cmd({'cmd': 'clock su r 2 sun mar 2:00 1 sun nov 2:00 o 60 z EDT' , 'state':7, 'action':'SET_STATE','args': [8]})
    dut.add_cmd({'cmd': 'show clock'                  , 'state':8, 'action':'PRINT','args': clock_output_4})
    dut.add_cmd({'cmd': 'clock timezone 8 zone CST'   , 'state':8, 'action':'SET_STATE','args': [9]})
    dut.add_cmd({'cmd': 'no clock summer-time'        , 'state':9, 'action':'SET_STATE','args': [10]})
    dut.add_cmd({'cmd': 'show clock'                  , 'state':10,'action':'PRINT','args': clock_output_5})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()

    # print (dut.port)
    # sleep(1000)
    with pytest.raises(KeyError) as excinfo:
        d.clock.update(dt=None, tz=None)
    with pytest.raises(KeyError) as excinfo:
        assert d.clock['calendar'] == ''

    d.clock.update(tz=tz1)
    assert d.clock['timezone_name'] == 'CEST'
    assert d.clock['timezone_offset'] == '+02:00'
    assert d.clock['summertime_start'] == 'Last Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'Last Sunday in October at 03:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(tz=tz2)
    assert d.clock['timezone_name'] == 'UYT'
    assert d.clock['timezone_offset'] == '-03:00'
    assert d.clock['summertime_start'] == 'First Sunday in October at 02:00:00'
    assert d.clock['summertime_end'] == 'Second Sunday in March at 02:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(tz=tz3)
    assert d.clock['timezone_name'] == 'AEST'
    assert d.clock['timezone_offset'] == '+10:00'
    assert d.clock['summertime_start'] == 'First Sunday in October at 02:00:00'
    assert d.clock['summertime_end'] == 'First Sunday in April at 03:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(tz=tz4)
    assert d.clock['timezone_name'] == 'EDT'
    assert d.clock['timezone_offset'] == '-04:00'
    assert d.clock['summertime_start'] == 'Second Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'First Sunday in November at 02:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(dt=dt,tz=tz5)
    assert d.clock['timezone_name'] == 'CST'
    assert d.clock['timezone_offset'] == '+08:00'
    assert d.clock['summertime_start'] == ''
    assert d.clock['summertime_end'] == ''
    assert d.clock['summertime_offset'] == ''

    assert 'utc_time' in d.clock.keys()
    assert 'local_time' in d.clock.keys()
    assert ('timezone_offset', '+08:00') in d.clock.items()

    d.close()
