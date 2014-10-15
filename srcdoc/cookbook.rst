Cookbook
********

Read single device facts
""""""""""""""""""""""""
Read a single device facts and print them on the console::

    from pynetworking import Device
    from pprint import pprint

    dev=Device('192.168.1.10',username='manager',password='friend')
    dev.open()
    pprint(dev.facts)
    dev.close()

Example output::

    {'build_date': u'Tue Dec 17 14:24:21 NZDT 2013',
     'build_name': u'x210-5.4.3-3.9.rel',
     'build_type': u'RELEASE',
     'hardware_rev': u'B-0',
     'model': u'x210-24GT',
     'os': 'awp',
     'serial_number': u'G22TCB02G',
     'sw_release': u'5.4.3',
     'version': u'5.4.3'}
 

Read multiple devices facts
"""""""""""""""""""""""""""
Scan my 192.168.1.0/24 network for devices and print their facts on the console::

    from pynetworking import Device, DeviceException
    from pprint import pprint

    for host in ['192.168.1.{0}'.format(i) for i in range(1,255)]:
        dev=Device(host)
        try:
            dev.open()
            print "Host: {0}".format(host)
            pprint(dev.facts)
            dev.close()
        except DeviceException as e:
            if not str(e).startswith('cannot connect to'):
                print 'Error connecting to {0} ({1})'.format(host,str(e))

Example output::

    .....
    .....
    Host: 192.168.1.10
    {'build_date': u'Tue Dec 17 14:24:21 NZDT 2013',
     'build_name': u'x210-5.4.3-3.9.rel',
     'build_type': u'RELEASE',
     'hardware_rev': u'B-0',
     'model': u'x210-24GT',
     'os': 'awp',
     'serial_number': u'G22TCB02G',
     'sw_release': u'5.4.3',
     'version': u'5.4.3'}
    .....
    .....


Print the list of interfaces of a device
""""""""""""""""""""""""""""""""""""""""
Print a list of the interfaces of a device with their name, admin state, link and current speed, if link is up::

    from pynetworking import Device

    dev=Device('192.168.10.10',username='manager',password='friend')
    dev.open()

    print "Name           State      Link     Speed     "
    print "---------------------------------------------"
    for name,info in dev.interface.items():
        print "{0:10}{1:>10}{2:>10}{3:>10}".format(
                name,
                'up' if info['enable'] else 'down',
                'up' if info['link'] else 'down',
                info['current speed'] if 'current speed' in info else ''
                )
    dev.close()

Example output::

    Name           State      Link     Speed     
    ---------------------------------------------
    1.0.1             up        up      1000
    1.0.2             up      down          
    1.0.3             up      down          
    1.0.4             up      down          
    1.0.5             up      down          
    1.0.6             up      down          
    1.0.7             up      down          
    1.0.8             up      down          
    1.0.9             up      down          
    1.0.10            up      down          
    1.0.11            up      down          
    1.0.12            up      down          
    1.0.13            up      down          
    1.0.14            up      down          
    1.0.15            up      down          
    1.0.16            up      down          
    1.0.17            up      down          
    1.0.18            up      down          
    1.0.19            up      down          
    1.0.20            up      down          
    1.0.21            up      down          
    1.0.22            up      down          
    1.0.23            up      down          
    1.0.24            up      down          
    lo                up        up          
    vlan1             up        up    


Print the list of vlans of a device
"""""""""""""""""""""""""""""""""""
Print the list of the vlans of a device along with their name, state and list of tagged and untagged interfaces::

    from pynetworking import Device
    from pprint import pprint

    dev=Device('10.17.39.253',username='manager',password='friend')
    dev.open()

    print "Vlan Id   Name      State     Untagged  Tagged    "
    print "--------------------------------------------------"
    for vid,info in dev.vlan.items():
        print "{0:10}{1:10}{2:10}{3:<10}{4:<10}".format(
                vid,
                info['name'],
                info['current state'],
                len(info['untagged']),
                len(info['tagged'])
                )

    dev.close()

Example output::

    Vlan Id   Name      State     Untagged  Tagged    
    --------------------------------------------------
    1         default   ACTIVE    23        0         
    10        video     ACTIVE    0         0         
    11        voice     ACTIVE    1         0         
    12        data      ACTIVE    0         1         
    13        mgmt      ACTIVE    0         1     


Set the device clock
""""""""""""""""""""
Set the current date and time and set the timezone::

    from datetime import datetime, timedelta
    from pytz import timezone
    from pynetworking import Device

    datetime = datetime.now()
    timezone = timezone("America/New_York")

    dev = Device('10.17.39.253',username='manager',password='friend')
    dev.open()

    dev.clock.update(datetime,timezone)

    for key in dev.clock.keys():
        print("{0} is: {1}".format(key, dev.clock[key]))

    dev.close()

Example output::

    local_time is: Thu, 25 Sep 2014 08:01:43 -0400
    utc_time is: Thu, 25 Sep 2014 12:01:43 +0000
    timezone_name is: EDT
    timezone_offset is: -05:00
    summertime_start is: Second Sunday in March at 02:00:00
    summertime_end is: First Sunday in November at 02:00:00
    summertime_offset is: 60
