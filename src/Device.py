# -*- coding: utf-8 -*-

class Device(object):

    def __init__(self, host, username='manager', password='friend', protocol='ssh', type='auto'):
        if protocol not in ('telnet','ssh','serial'):
            raise ValueError("Unsupported protocol "+protocol)
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._conn = None
        self._facts = {}
        self._type = type

    @property
    def username(self):
        return self._username

    def open(self):
        pass

    def close(self):
        pass

    def cmd(self, cmd):
        return ""

    def config(self):
        return ""
