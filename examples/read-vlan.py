from pynetworking import Device


dev = Device('10.17.39.253', username='manager', password='friend')
dev.open()

print "Vlan Id   Name      State     Untagged  Tagged    "
print "--------------------------------------------------"
for vid, info in dev.vlan.items():
    print "{0:10}{1:10}{2:10}{3:<10}{4:<10}".format(
        vid,
        info['name'],
        info['current state'],
        len(info['untagged']),
        len(info['tagged']))

dev.close()
