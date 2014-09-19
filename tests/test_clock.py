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
    dut.add_cmd({'cmd':'show version',        'state':-1, 'action': 'PRINT','args':["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
    """]})


def test_update(dut, log_level):
    clock_output_0 = ["""
UTC Time:   Thu, 18 Sep 2014 14:19:21 +0000
Timezone: UTC
Timezone Offset: +00:00
Summer time zone: None
"""]
    clock_output_1 = ["""
Local Time: Thu, 18 Sep 2014 10:21:17 -0400
UTC Time:   Thu, 18 Sep 2014 14:21:17 +0000
Timezone: EDT
Timezone Offset: -05:00
Summer time zone: EDT
Summer time starts: Second Sunday in March at 02:00:00
Summer time ends: First Sunday in November at 02:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]

    setup_dut(dut)

    dt = datetime.now()

    tz1 = timezone('Europe/Rome')
    tz2 = timezone('America/Santiago')
    tz3 = timezone('Australia/Sydney')
    tz4 = timezone('America/New_York')

    dut.add_cmd({'cmd': 'show clock'                , 'state':0, 'action':'PRINT','args': clock_output_0})
    dut.add_cmd({'cmd': 'clock timezone CEST plus 2', 'state':0, 'action':'SET_STATE','args': [1]})
    dut.add_cmd({'cmd': 'clock summer-time CEST recurring 5 Sun Mar 2:00 5 Sun Oct 3:00 60', 'state':1, 'action':'SET_STATE','args': [2]})
    dut.add_cmd({'cmd': 'show clock'                , 'state':2, 'action':'PRINT','args': clock_output_1})
    dut.add_cmd({'cmd': 'clock timezone EDT minus 4', 'state':2, 'action':'SET_STATE','args': [3]})
    dut.add_cmd({'cmd': 'clock summer-time EDT recurring 2 Sun Mar 2:00 1 Sun Nov 2:00 60', 'state':3, 'action':'SET_STATE','args': [4]})
    dut.add_cmd({'cmd': 'show clock'                , 'state':4, 'action':'PRINT','args': clock_output_1})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    # print(dut.port)
    # sleep(1000)
    with pytest.raises(KeyError) as excinfo:
        d.clock.update(dt=None, tz=None)
    d.clock.update(tz=tz1)
    assert d.clock['timezone_name'] == 'CEST'
    assert d.clock['timezone_offset'] == '+01:00'
    assert d.clock['summertime_start'] == 'Last Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'Last Sunday in October at 03:00:00'
    assert d.clock['summertime_offset'] == '60'
    # d.clock.update(tz=tz2)
    # d.clock.update(tz=tz3)

    d.clock.update(tz=tz4)
    assert d.clock['timezone_name'] == 'EDT'
    assert d.clock['timezone_offset'] == '-05:00'
    assert d.clock['summertime_start'] == 'Second Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'First Sunday in November at 02:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.close()
