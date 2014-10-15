from pynetworking import Device
from pprint import pprint


dev=Device('10.17.39.253',username='manager',password='friend')
dev.open()
pprint(dev.facts)
dev.close()
