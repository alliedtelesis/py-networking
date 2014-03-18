import pytest
from pynetworking.Device import Device

def test_device_create():
    Device(host='localhost', username='manager', password='friend')
    Device(host='localhost', protocol='ssh')
    Device(host='localhost', protocol='telnet')
    Device(host='localhost', protocol='serial')
    with pytest.raises(ValueError):
        Device(host='localhost', protocol='http')
    d=Device(host='localhost')
    assert d.username == 'manager'


