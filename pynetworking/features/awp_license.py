# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class awp_license(Feature):
    """
    Software licensing feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._d = device


    def set_license(self, label='', key='', certificate=''):
        self._d.log_info("set license")
        self._update_license()

        if not ((label == '' and key == '' and certificate != "") or (label != '' and key != '' and certificate == "")):
            raise KeyError('Either label and key or certificate must be given')

        set_cmd = 'copy {0}://{1}:{2}/{3} {4}'.format(protocol, host_ip_address, port, filename, name)
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': set_cmd , 'prompt':'\#'}
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_license()


    def delete(self, label):
        self._d.log_info("remove license {0}".format(label))
        self._update_license()

        if file_name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(file_name))

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': 'enable'  , 'prompt':'\#'},
                        {'cmd': delete_cmd, 'prompt':''  },
                        {'cmd': 'y'       , 'prompt':'\#', 'timeout': 10000}
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_license()


    def items(self):
        self._update_license()
        return self._license.items()


    def keys(self):
        self._update_license()
        return self._license.keys()


    def __getitem__(self, label):
        self._update_license()
        if label in self._license.keys():
            return self._license[label]
        raise KeyError('license {0} does not exist'.format(label))


    def _update_license(self):
        self._d.log_info("_update_license")
        self._license = OrderedDict()

        # 588 -rw- Jun 10 2014 12:38:10  michele.cfg
        ifre = re.compile('\s+(?P<size>\d+)\s+'
                          '(?P<permission>[^\s]+)\s+'
                          '(?P<month>[^\s]+)\s+'
                          '(?P<day>\d+)\s+'
                          '(?P<year>\d+)\s+'
                          '(?P<hhmmss>[^\s]+)\s+'
                          '(?P<file_name>[^\s]+)')
        for line in self._device.cmd("show license").split('\n'):
            m = ifre.match(line)
            if m:
                key = m.group('file_name')
                self._license[key] = {'size': m.group('size'),
                                   'permission': m.group('permission'),
                                   'mdate': m.group('day') + '-' + m.group('month') + '-' + m.group('year'),
                                   'mtime': m.group('hhmmss')
                                  }
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._license))))
