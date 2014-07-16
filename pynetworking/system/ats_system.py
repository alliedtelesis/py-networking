# -*- coding: utf-8 -*-
import re
from time import sleep
import socket
import logging
import zmq
import json
import ats_file

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

    def update(self, name, server='', filename=''):
        self._d.log_info("upgrading image {0}".format(name))
        self._update_image_dict()

        if (os.path.exists(name) == False):
            raise KeyError('image {0} not available'.format(name))

        self._file.create(self, 'image', port=port, filename=name, server=server)
        boot_cmd = 'boot system image-{0}'.format(self._get_stand_by_bank())
        cmds = {'cmds': [{'cmd': boot_cmd, 'prompt': '\#'},
                         {'cmd': 'reboot', 'prompt': ''  },
                         {'cmd': 'y'     , 'prompt': '\#'}
                        ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)
        self._d.load_system()

    def _get_stand_by_bank(self):
        stand_by_bank = 1 #FIXME
        return stand_by_bank
