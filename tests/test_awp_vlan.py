import pytest
import os
from pynetworking import Device
from pprint import pprint

test_device = '10.17.39.252'
devicenotonline = pytest.mark.skipif(os.system("ping -c 2 -t 2 " + test_device) != 0,
                                reason="test device {0} is not online".format(test_device))
@devicenotonline
def test_device_vlan(log_level):
    d=Device(host=test_device, log_level=log_level)
    d.open()
#    d.vlan.create(20)
#    print d.vlan
    d.close()

@devicenotonline
def test_get_show_interface(log_level):
    d=Device(host=test_device, log_level=log_level)
    d.open()
    for ifn,ifi in sorted(d.interface.items(), key=lambda ifn: ifn[0]):
        print "\n>>{0}".format(ifn)
        pprint(ifi)
    d.close()

