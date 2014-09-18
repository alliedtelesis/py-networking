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


def test_update_date_time(dut, log_level):
    setup_dut(dut)

    dt = datetime.now()
    # dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.clock.update(dt=dt)
    d.close()


def test_update_time_zone(dut, log_level):
    setup_dut(dut)

    tz1 = timezone('Europe/Rome')
    tz2 = timezone('America/Santiago')
    tz3 = timezone('Australia/Sydney')
    tz4 = timezone('America/New_York')

    # dut.add_cmd({'cmd': 'dir'   , 'state':0, 'action':'PRINT','args': dir_0})
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)
    d.open()
    d.clock.update(tz=tz1)
    d.clock.update(tz=tz2)
    d.clock.update(tz=tz3)
    d.clock.update(tz=tz4)
    d.close()
