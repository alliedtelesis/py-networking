# -*- coding: utf-8 -*-
import re
from time import sleep
from pprint import pformat
import socket
import logging
import zmq
import json
import os

try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

log = logging.getLogger(__name__)

class ats_system(object):
    """
    System for ATS
    """
    def __init__(self, device):
        self._d =  device

    def get_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        for line in self._d.cmd('show running-config').replace('\r','').split('\n'):
            config += line+'\n'
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def get_startup_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        for line in self._d.cmd('show startup-config').replace('\r','').split('\n'):
            config += line+'\n'
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def save_config(self):
        self._d.log_info('save running configuration')
        cmds = {'cmds':[{'cmd': 'copy r s', 'prompt':''},
                        {'cmd': 'y'       , 'prompt':'\#'}]}
        self._d.cmd(cmds, cache=False, flush_cache=True)
        self._d.load_system()

    def shell_init(self):
        self._d.log_info('shell_init')
        return [{'cmd': 'terminal datadump', 'prompt':'\#'},]

    def shell_prompt(self):
        self._d.log_info('shell_prompt')
        return r'[\>\#]'

    def ping(self):
        self._d.log_info('ping')
        self._d.cmd('show version', use_cache=False)

    def update(self, name, port=69, server=''):
        self._d.log_info("upgrading image {0}".format(name))

        if (os.path.exists(name) == False):
            raise KeyError('image {0} not available'.format(name))

        self._d.file.create(name='image', port=port, filename=name, server=server)
        boot_cmd = 'boot system image-{0}'.format(self._get_stand_by_bank())
        cmds = {'cmds': [{'cmd': boot_cmd, 'prompt': '\#'},
                         {'cmd': 'reload', 'prompt': ''  },
                         {'cmd': 'y'     , 'prompt': '\#'}
                        ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)

    def _get_stand_by_bank(self):
        self._d.log_info("_get_stand_by_bank")
        self._image = OrderedDict()
        stand_by_bank = 1

        # 1     1      image-1    3.0.0.44   02-Oct-2011  13:29:54   Not active
        ifre = re.compile('(?P<unit>\d+)\s+'
                          '(?P<image>\d+)\s+'
                          '(?P<file_name>[^\s]+)\s+'
                          '(?P<version>[^\s]+)\s+'
                          '(?P<date>[^\s]+)\s+'
                          '(?P<time>[^\s]+)\s+'
                          '(?P<status>[^\s]+)\s+')
        for line in self._d.cmd("show bootvar").split('\n'):
            m = ifre.match(line)
            self._d.log_debug("read {0}".format(line))
            if m:
                bnk_status = False
                if (m.group('status')[:6] == 'Active'):
                    bnk_status = True
                next_boot = False
                if line[-2] == '*':
                    stand_by_bank = m.group('image')
                    next_boot = True
                key = m.group('file_name')
                self._image[key] = {'unit': m.group('unit'),
                                    'image': m.group('image'),
                                    'name': key,
                                    'version': m.group('version'),
                                    'mdate': m.group('date'),
                                    'mtime': m.group('time'),
                                    'active': bnk_status,
                                    'nextboot': next_boot
                                   }
        self._d.log_debug("Image {0}".format(pformat(json.dumps(self._image))))

        return stand_by_bank
