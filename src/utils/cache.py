# -*- coding: utf-8 -*-

try:
    from hashlib import md5
except ImportError: #pragma: no cover
    from md5 import new as md5
from time import time
import json

class CacheMissException(Exception):
    pass

class Cache(object):
    def __init__(self, enable=True, default_timeout=30):
        self.cache = {}
        self.default_timeout = default_timeout
        self.enable = enable

    def get(self, cmd):
        if self.enable:
            k = md5(json.dumps(cmd)).hexdigest()
            if k in self.cache:
                if self.cache[k][0] > time():
                    return self.cache[k][1]
                else:
                    self.cache.pop(k)

        raise CacheMissException()

    def set(self, cmd, value, timeout=None):
        if not timeout:
            timeout = self.default_timeout

        k = md5(json.dumps(cmd)).hexdigest()
        self.cache[k] = (time()+timeout, value)

    def flush(self):
        self.cache = {}

