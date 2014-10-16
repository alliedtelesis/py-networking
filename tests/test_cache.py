from pynetworking.utils import Cache, CacheMissException
from time import sleep
import pytest


def test_cache1():
    c = Cache(default_timeout=2)
    cmds = {'cmds': [{'cmd': 'show vlan', 'prompt': '\#'},
                     {'cmd': 'show interface', 'prompt': '\#'},
                     ]}
    cmd_output = 'this is a test output'
    c.set(cmds, cmd_output)
    assert cmd_output == c.get(cmds)
    sleep(3)
    with pytest.raises(CacheMissException):
        c.get(cmds)


def test_cache2():
    c = Cache(default_timeout=2)
    cmds = {'cmds': [{'cmd': 'show vlan', 'prompt': '\#'},
                     {'cmd': 'show interface', 'prompt': '\#'},
                     ]}
    cmd_output = 'this is a test output'
    c.set(cmds, cmd_output)
    sleep(1)
    c.flush()
    with pytest.raises(CacheMissException):
        c.get(cmds)


def test_cache3():
    c = Cache(default_timeout=2)
    cmds1 = {'cmds': [{'cmd': 'show vlan', 'prompt': '\#'},
                      {'cmd': 'show interface', 'prompt': '\#'},
                      ]}
    cmds2 = {'cmds': [{'cmd': 'show vlan1', 'prompt': '\#'},
                      {'cmd': 'show interface1', 'prompt': '\#'},
                      ]}
    cmd_output1 = 'this is a test output 1'
    cmd_output2 = 'this is a test output 2'
    c.set(cmds1, cmd_output1)
    c.set(cmds2, cmd_output2)
    assert cmd_output1 == c.get(cmds1)
    assert cmd_output2 == c.get(cmds2)
