# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class awp_file(Feature):
    """
    File feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._file_config={}
        self._file={}
        self._d = device
        self._d.log_debug("loading feature")

    def load_config(self, config):
        self._d.log_info("loading config")
        self._file_config = OrderedDict()

        # 588 -rw- Jun 10 2014 12:38:10  michele.cfg
        ifre = re.compile('\s+(?P<size>\d+)\s+'
                          '(?P<permission>[^\s]+)\s+'
                          '(?P<month>[^\s]+)\s+'
                          '(?P<day>\d+)\s+'
                          '(?P<year>\d+)\s+'
                          '(?P<hhmmss>[^\s]+)\s+'
                          '(?P<file_name>[^\s]+)')
        for line in self._device.cmd("dir").split('\n'):
            m = ifre.match(line)
            self._d.log_info("read {0}".format(line))
            if m:
                self._file_config[m.group('file_name')] = {'size': m.group('size'),
                                                           'permission': m.group('permission'),
                                                           'month': m.group('month'),
                                                           'day': m.group('day'),
                                                           'year': m.group('year'),
                                                           'hhmmss': m.group('hhmmss')
                                                          }
        self._d.log_info(self._file_config)


    def copy(self, source_file, dest_file, source_ip_address, dest_ip_address, protocol='tftp'):
        if (source_ip_address == 'localhost'):
            self._d.log_info("copying {0} to {1}://{2}/{3}".format(source_file, protocol, dest_ip_address, dest_file))
        else:
            if (dest_ip_address == 'localhost'):
                self._d.log_info("copying {0}://{1}/{2} to {3}".format(protocol, source_ip_address, source_file, dest_file))
            else:
                self._d.log_info("no localhost file specified")
                return

        self._update_file()

        copy_cmd = ''
        # copy_cmd = 'copy {0}'.format(file_name) ...... to be defined
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': 'conf t', 'prompt':'\(config\)\#'},
                        {'cmd': copy_cmd, 'prompt':'\(config\)\#'},
                        {'cmd': chr(26) , 'prompt':'\#'},
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()


    def delete(self, file_name):
        self._d.log_info("remove {0}".format(file_name))
        self._update_file()

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': 'enable'  , 'prompt':'\#'},
                        {'cmd': delete_cmd, 'prompt':''  },
                        {'cmd': 'y'       , 'prompt':'\#'}
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()


    def items(self):
        self._update_file()
        return self._file.items()


    def keys(self):
        self._update_file()
        return self._file.keys()


    def __getitem__(self, filename):
        self._update_file()
        if filename in self._file.keys():
            return self._file[filename]
        raise KeyError('file {0} does not exist'.format(filename))


    def _update_file(self):
        self._d.log_info("_update_file")
        self._file = OrderedDict()

        # 588 -rw- Jun 10 2014 12:38:10  michele.cfg
        ifre = re.compile('\s+(?P<size>\d+)\s+'
                          '(?P<permission>[^\s]+)\s+'
                          '(?P<month>[^\s]+)\s+'
                          '(?P<day>\d+)\s+'
                          '(?P<year>\d+)\s+'
                          '(?P<hhmmss>[^\s]+)\s+'
                          '(?P<file_name>[^\s]+)')
        for line in self._device.cmd("dir").split('\n'):
            m = ifre.match(line)
            self._d.log_info("read {0}".format(line))
            if m:
                key = m.group('file_name')
                self._file[key] = {'size': m.group('size'),
                                   'permission': m.group('permission'),
                                   'month': m.group('month'),
                                   'day': m.group('day'),
                                   'year': m.group('year'),
                                   'hhmmss': m.group('hhmmss')
                                  }
                self._file[key] = dict(self._file[key].items() + self._file_config[key].items())
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._file))))
