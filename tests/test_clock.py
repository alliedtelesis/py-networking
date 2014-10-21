import pytest
from pynetworking.Device import Device
from datetime import datetime
from pytz import timezone


def setup_dut(dut):
    dut.reset()
    dut.add_cmd({'cmd': 'show version', 'state': -1, 'action': 'PRINT', 'args': ["""
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
"""]})


def test_update(dut, log_level, use_mock):
    clock_output_0 = ["""
UTC Time:   Thu, 18 Sep 2014 14:19:21 +0000
Timezone: UTC
Timezone Offset: +00:00
Summer time zone: None
"""]
    clock_output_1 = ["""
Local Time: Fri, 19 Sep 2014 11:02:07 +0200
UTC Time:   Fri, 19 Sep 2014 09:02:07 +0000
Timezone: CET
Timezone Offset: +01:00
Summer time zone: CEST
Summer time starts: Last Sunday in March at 02:00:00
Summer time ends: Last Sunday in October at 03:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_2 = ["""
Local Time: Fri, 19 Sep 2014 06:02:41 -0300
UTC Time:   Fri, 19 Sep 2014 09:02:41 +0000
Timezone: UYT
Timezone Offset: -03:00
Summer time zone: UYST
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
Summer time zone: AEDT
Summer time starts: First Sunday in October at 02:00:00
Summer time ends: First Sunday in April at 03:00:00
Summer time offset: 60 mins
Summer time recurring: Yes
"""]
    clock_output_4 = ["""
Local Time: Fri, 19 Sep 2014 05:03:56 -0400
UTC Time:   Fri, 19 Sep 2014 09:03:56 +0000
Timezone: EST
Timezone Offset: -05:00
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
    clock_output_6 = ["""
Local Time: Fri, 18 Sep 2014 23:04:29 -1000
UTC Time:   Fri, 18 Sep 2014 23:04:29 -1000
Timezone: CKT
Timezone Offset: -10:00
Summer time zone: None
"""]

    setup_dut(dut)

    # tests use a fixed date, otherwise they can fail depending on the current date
    dt = datetime(2014, 9, 19, 11, 2, 0)     # dt = datetime.now()

    tz1 = timezone('Europe/Rome')
    tz2 = timezone('America/Montevideo')
    tz3 = timezone('Australia/Sydney')
    tz4 = timezone('America/New_York')
    tz5 = timezone('Asia/Shanghai')
    tz6 = timezone('Pacific/Rarotonga')

    dut.add_cmd({'cmd': 'show clock', 'state': 0, 'action': 'PRINT', 'args': clock_output_0})
    dut.add_cmd({'cmd': 'clock timezone CET plus 1', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'clock summer-time CEST recurring 5 Sun Mar 2:00 5 Sun Oct 3:00 60', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show clock', 'state': 2, 'action': 'PRINT', 'args': clock_output_1})
    dut.add_cmd({'cmd': 'clock timezone UYT minus 3', 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'clock summer-time UYST recurring 1 Sun Oct 2:00 2 Sun Mar 2:00 60', 'state': 3, 'action': 'SET_STATE', 'args': [4]})
    dut.add_cmd({'cmd': 'show clock', 'state': 4, 'action': 'PRINT', 'args': clock_output_2})
    dut.add_cmd({'cmd': 'clock timezone AEST plus 10', 'state': 4, 'action': 'SET_STATE', 'args': [5]})
    dut.add_cmd({'cmd': 'clock summer-time AEDT recurring 1 Sun Oct 2:00 1 Sun Apr 3:00 60', 'state': 5, 'action': 'SET_STATE', 'args': [6]})
    dut.add_cmd({'cmd': 'show clock', 'state': 6, 'action': 'PRINT', 'args': clock_output_3})
    dut.add_cmd({'cmd': 'clock timezone EST minus 5', 'state': 6, 'action': 'SET_STATE', 'args': [7]})
    dut.add_cmd({'cmd': 'clock summer-time EDT recurring 2 Sun Mar 2:00 1 Sun Nov 2:00 60', 'state': 7, 'action': 'SET_STATE', 'args': [8]})
    dut.add_cmd({'cmd': 'show clock', 'state': 8, 'action': 'PRINT', 'args': clock_output_4})
    dut.add_cmd({'cmd': 'clock timezone CST plus 8', 'state': 8, 'action': 'SET_STATE', 'args': [9]})
    dut.add_cmd({'cmd': 'no clock summer-time', 'state': 9, 'action': 'SET_STATE', 'args': [10]})
    dut.add_cmd({'cmd': 'show clock', 'state': 10, 'action': 'PRINT', 'args': clock_output_5})
    dut.add_cmd({'cmd': 'clock timezone CKT minus 10', 'state': 10, 'action': 'SET_STATE', 'args': [11]})
    dut.add_cmd({'cmd': 'no clock summer-time', 'state': 11, 'action': 'SET_STATE', 'args': [12]})
    dut.add_cmd({'cmd': 'show clock', 'state': 12, 'action': 'PRINT', 'args': clock_output_6})
    d = Device(host=dut.host, port=dut.port, protocol=dut.protocol, log_level=log_level, mock=use_mock)
    d.open()

    with pytest.raises(KeyError) as excinfo:
        d.clock.update(datetime=None, timezone=None)
    assert 'either datetime or timezone argument must be given' in excinfo.value
    with pytest.raises(KeyError) as excinfo:
        assert d.clock['calendar'] == ''
    assert 'parameter calendar does not exist' in excinfo.value

    d.clock.update(datetime=dt, timezone=tz1)
    assert d.clock['timezone_name'] == 'CET'
    assert d.clock['timezone_offset'] == '+01:00'
    assert d.clock['summertime_zone'] == 'CEST'
    assert d.clock['summertime_start'] == 'Last Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'Last Sunday in October at 03:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(datetime=dt, timezone=tz2)
    assert d.clock['timezone_name'] == 'UYT'
    assert d.clock['timezone_offset'] == '-03:00'
    assert d.clock['summertime_zone'] == 'UYST'
    assert d.clock['summertime_start'] == 'First Sunday in October at 02:00:00'
    assert d.clock['summertime_end'] == 'Second Sunday in March at 02:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(datetime=dt, timezone=tz3)
    assert d.clock['timezone_name'] == 'AEST'
    assert d.clock['timezone_offset'] == '+10:00'
    assert d.clock['summertime_zone'] == 'AEDT'
    assert d.clock['summertime_start'] == 'First Sunday in October at 02:00:00'
    assert d.clock['summertime_end'] == 'First Sunday in April at 03:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(datetime=dt, timezone=tz4)
    assert d.clock['timezone_name'] == 'EST'
    assert d.clock['timezone_offset'] == '-05:00'
    assert d.clock['summertime_zone'] == 'EDT'
    assert d.clock['summertime_start'] == 'Second Sunday in March at 02:00:00'
    assert d.clock['summertime_end'] == 'First Sunday in November at 02:00:00'
    assert d.clock['summertime_offset'] == '60'

    d.clock.update(datetime=dt, timezone=tz5)
    assert d.clock['timezone_name'] == 'CST'
    assert d.clock['timezone_offset'] == '+08:00'
    assert d.clock['summertime_zone'] == ''
    assert d.clock['summertime_start'] == ''
    assert d.clock['summertime_end'] == ''
    assert d.clock['summertime_offset'] == ''

    d.clock.update(datetime=dt, timezone=tz6)
    assert d.clock['timezone_name'] == 'CKT'
    assert d.clock['timezone_offset'] == '-10:00'
    assert d.clock['summertime_zone'] == ''
    assert d.clock['summertime_start'] == ''
    assert d.clock['summertime_end'] == ''
    assert d.clock['summertime_offset'] == ''

    assert 'utc_time' in d.clock.keys()
    assert 'local_time' in d.clock.keys()
    assert ('timezone_offset', '-10:00') in d.clock.items()

    d.close()
