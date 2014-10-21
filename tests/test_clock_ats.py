import pytest
from pynetworking.Device import Device
from datetime import datetime
from pytz import timezone


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


def test_update(dut, log_level, use_mock):
    clock_output_0 = ["""
*01:13:50 (UTC+0)  Oct 1 2006
No time source

Time zone:
Offset is UTC+0
"""]
    clock_output_1 = ["""
*23:10:40 CEST(UTC+2)  Sep 30 2006

No time source

Time zone:
Acronym is CET
Offset is UTC+1

Summertime:
Acronym is CEST
Recurring every year.
Begins at 05 01 03 02:00.
Ends at 05 01 10 03:00.
Offset is 60 minutes.
"""]
    clock_output_2 = ["""
*23:11:16 UYT(UTC-3)  Sep 30 2006

No time source

Time zone:
Acronym is UYT
Offset is UTC-3

Summertime:
Acronym is UYST
Recurring every year.
Begins at 01 01 10 02:00.
Ends at 02 01 03 02:00.
Offset is 60 minutes.
"""]
    clock_output_3 = ["""
*11:11:59 AEST(UTC+10)  Oct 1 2006
No time source

Time zone:
Acronym is AEST
Offset is UTC+10

Summertime:
Acronym is AEDT
Recurring every year.
Begins at 01 01 10 02:00.
Ends at 01 01 04 03:00.
Offset is 60 minutes.
"""]
    clock_output_4 = ["""
*22:12:30 EDT(UTC-4)  Sep 30 2006
No time source

Time zone:
Acronym is EST
Offset is UTC-5

Summertime:
Acronym is EDT
Recurring every year.
Begins at 02 01 03 02:00.
Ends at 01 01 11 02:00.
Offset is 60 minutes.
"""]
    clock_output_5 = ["""
*09:13:23 CST(UTC+8)  Oct 1 2006
No time source

Time zone:
Acronym is CST
Offset is UTC+8
"""]
    clock_output_6 = ["""
*16:13:28 CKT(UTC-10)  Sep 30 2006
No time source

Time zone:
Acronym is CKT
Offset is UTC-10
"""]

    setup_dut(dut)

    dt = datetime.now()

    tz1 = timezone('Europe/Rome')
    tz2 = timezone('America/Montevideo')
    tz3 = timezone('Australia/Sydney')
    tz4 = timezone('America/New_York')
    tz5 = timezone('Asia/Shanghai')
    tz6 = timezone('Pacific/Rarotonga')

    dut.add_cmd({'cmd': 'show clock detail', 'state': 0, 'action': 'PRINT', 'args': clock_output_0})
    dut.add_cmd({'cmd': 'clock timezone 1 zone CET', 'state': 0, 'action': 'SET_STATE', 'args': [1]})
    dut.add_cmd({'cmd': 'clock su r 5 sun mar 2:00 5 sun oct 3:00 o 60 z CEST', 'state': 1, 'action': 'SET_STATE', 'args': [2]})
    dut.add_cmd({'cmd': 'show clock detail', 'state': 2, 'action': 'PRINT', 'args': clock_output_1})
    dut.add_cmd({'cmd': 'clock timezone -3 zone UYT', 'state': 2, 'action': 'SET_STATE', 'args': [3]})
    dut.add_cmd({'cmd': 'clock su r 1 sun oct 2:00 2 sun mar 2:00 o 60 z UYST', 'state': 3, 'action': 'SET_STATE', 'args': [4]})
    dut.add_cmd({'cmd': 'show clock detail', 'state': 4, 'action': 'PRINT', 'args': clock_output_2})
    dut.add_cmd({'cmd': 'clock timezone 10 zone AEST', 'state': 4, 'action': 'SET_STATE', 'args': [5]})
    dut.add_cmd({'cmd': 'clock su r 1 sun oct 2:00 1 sun apr 3:00 o 60 z AEDT', 'state': 5, 'action': 'SET_STATE', 'args': [6]})
    dut.add_cmd({'cmd': 'show clock detail', 'state': 6, 'action': 'PRINT', 'args': clock_output_3})
    dut.add_cmd({'cmd': 'clock timezone -5 zone EST', 'state': 6, 'action': 'SET_STATE', 'args': [7]})
    dut.add_cmd({'cmd': 'clock su r 2 sun mar 2:00 1 sun nov 2:00 o 60 z EDT', 'state': 7, 'action': 'SET_STATE', 'args': [8]})
    dut.add_cmd({'cmd': 'show clock detail', 'state': 8, 'action': 'PRINT', 'args': clock_output_4})
    dut.add_cmd({'cmd': 'clock timezone 8 zone CST', 'state': 8, 'action': 'SET_STATE', 'args': [9]})
    dut.add_cmd({'cmd': 'no clock summer-time r', 'state': 9, 'action': 'SET_STATE', 'args': [10]})
    dut.add_cmd({'cmd': 'show clock detail', 'state': 10, 'action': 'PRINT', 'args': clock_output_5})
    dut.add_cmd({'cmd': 'clock timezone -10 zone CKT', 'state': 10, 'action': 'SET_STATE', 'args': [11]})
    dut.add_cmd({'cmd': 'no clock summer-time r', 'state': 11, 'action': 'SET_STATE', 'args': [12]})
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
    assert d.clock['summertime_start'] == ''
    assert d.clock['summertime_end'] == ''
    assert d.clock['summertime_offset'] == ''

    d.clock.update(datetime=dt, timezone=tz6)
    assert d.clock['timezone_name'] == 'CKT'
    assert d.clock['timezone_offset'] == '-10:00'
    assert d.clock['summertime_start'] == ''
    assert d.clock['summertime_end'] == ''
    assert d.clock['summertime_offset'] == ''

    assert 'utc_time' in d.clock.keys()
    assert 'local_time' in d.clock.keys()
    assert ('timezone_offset', '-10:00') in d.clock.items()

    d.close()
