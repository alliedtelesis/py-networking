from pynetworking import Device

dev=Device('10.17.39.253',username='manager',password='friend')
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
