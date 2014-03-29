import pytest
from pynetworking import Device


#@pytest.mark.current
def test_device_vlan():
    d=Device(host='10.17.39.254')
    d.open()
    d.vlan.create(20)
    print d.vlan
    d.close()
