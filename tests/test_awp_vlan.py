import pytest
import os
from pynetworking import Device

test_device = '10.17.39.254'
devicenotonline = pytest.mark.skipif(os.system("ping -q -c 1 -t 1 " + test_device) != 0,
                                reason="test device {0} is not online".format(test_device))

@devicenotonline
def test_device_vlan():
    d=Device(host=test_device)
    d.open()
    d.vlan.create(20)
    print d.vlan
    d.close()

def test_get_show_interface():
    d=Device(host=test_device)
    d.open()
    with open('show_interface1.dat', 'w') as f:
        f.write(d.cmd("show interface"))
    d.close()

