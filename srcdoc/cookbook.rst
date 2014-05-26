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

    TBD

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
        except Device Exception as e:
            if not str(e).startswith('cannot connect to'):
                print 'Error connecting to {0} ({1})'.format(host,str(e))

Example output::

    TBD

Print the list of interfaces of a device
""""""""""""""""""""""""""""""""""""""""
Print a list of the interfaces of a device with thier name, admin state, link and current speed, if link is up::

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

    TBD

Print the list of vlans of a device
"""""""""""""""""""""""""""""""""""
Print the list of the vlans of a device along with thier name, state and list of tagged and untagged interfaces::

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

    TBD