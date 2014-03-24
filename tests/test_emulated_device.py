import pytest
from pynetworking import Device
from time import sleep
from paramiko.rsakey import RSAKey
from pprint import pprint

show_version_output = """
AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

Build name : x600-5.4.2-3.14.rel
Build date : Wed Sep 25 12:57:26 NZST 2013
Build type : RELEASE
 NET-SNMP SNMP agent software
 (c) 1996, 1998-2000 The Regents of the University of California.
     All rights reserved;
 (c) 2001-2003, Networks Associates Technology, Inc. All rights reserved;
 (c) 2001-2003, Cambridge Broadband Ltd. All rights reserved;
 (c) 2003, Sun Microsystems, Inc. All rights reserved.
 RSA Data Security, Inc. MD5 Message-Digest Algorithm
 (c) 1991-2, RSA Data Security, Inc. Created 1991. All rights reserved.
 Libedit Library
 (c) 1992, 1993 The Regents of the University of California.
     All rights reserved.
 OpenSSL Library
 Copyright (C) 1998-2011 The OpenSSL Project. All rights reserved.
 Original SSLeay License
 Copyright (C) 1995-1998 Eric Young (eay@cryptsoft.com).
 sFlow(R) Agent Software
 Copyright (c) 2002-2006 InMon Corp.
 DHCP Library
 Copyright (c) 2004-2010 by Internet Systems Consortium, Inc;
 Copyright (c) 1995-2003 by Internet Software Consortium.
 Application Interface Specification Framework
 Copyright (c) 2002-2004 MontaVista Software, Inc;
 Copyright (c) 2005-2010 Red Hat, Inc.
 Hardware Platform Interface Library
 Copyright (c) 2003, Intel Corporation;
 Copyright (C) IBM Corp. 2003-2007.
 Corosync Cluster Engine
 Copyright (c) 2002-2004 MontaVista Software, Inc. All rights reserved.
 File Utility Library
 Copyright (c) Ian F. Darwin 1986-1987, 1989-1992, 1994-1995.
 Software written by Ian F. Darwin and others;
 maintained 1994- Christos Zoulas.

Portions of this product are covered by the GNU GPL, source code may be
downloaded from: http://www.alliedtelesis.co.nz/support/gpl/awp.html
    """
show_system_output = """
    Switch System Status                                   Fri Mar 21 15:45:13 2014

    Board       ID  Bay   Board Name                         Rev   Serial number
    --------------------------------------------------------------------------------
    Base       294        x600-48Ts/XP                       B-0   G1Q79C001
    Expansion  306  Bay1  AT-StackXG                         A-0   N/A
    --------------------------------------------------------------------------------
    RAM:  Total: 512932 kB Free: 413340 kB
    Flash: 63.0MB Used: 23.7MB Available: 39.3MB
    --------------------------------------------------------------------------------
    Environment Status : Normal
    Uptime             : 0 days 00:07:29
    Bootloader version : 1.1.0


    Current software   : x600-5.4.2-3.14.rel
    Software version   : 5.4.2-3.14
    Build date         : Wed Sep 25 12:57:26 NZST 2013

    Current boot config: flash:/default.cfg (file not found)
    User Configured Territory: europe

    System Name
     awplus
     System Contact

     System Location

    """
def test_setup_emulated_device(ssh_server):
    ssh_server.device.add_command('show system', show_system_output, prompt = True)
    ssh_server.device.add_command('show version', show_version_output, prompt = True)
    ssh_server.start()
    sleep(2)

def test_device_open_close(ssh_server):
    d=Device(host='localhost',port=ssh_server.port)
    d.open()
    d.close()

def test_device_ping(ssh_server):
    d=Device(host='localhost',port=ssh_server.port)
    d.open()
    assert d.ping()
    d.close()

def test_device_facts(ssh_server):
    d=Device(host='localhost',port=ssh_server.port)
    d.open()
    assert d.facts['build_date'] == 'Wed Sep 25 12:57:26 NZST 2013'
    assert d.facts['build_name'] == 'x600-5.4.2-3.14.rel'
    assert d.facts['build_type'] == 'RELEASE'
    assert d.facts['version'] == '5.4.2'
    d.close()


