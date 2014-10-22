from pynetworking.Device import Device
from pprint import pprint


for host in ('10.17.39.253', '10.17.39.254'):
    dev = Device(host)
    dev.open()
    print "Host: {0}".format(host)
    pprint(dev.facts)
    dev.close()
