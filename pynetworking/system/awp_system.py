# -*- coding: utf-8 -*-
import re
from time import sleep
import os
import socket
import logging
import zmq
import json

log = logging.getLogger(__name__)

class awp_system(object):
    """
    System for AWP
    """
    def __init__(self, device):
        self._d =  device

    def get_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\#'},
                        {'cmd': 'show running-config',       'prompt':'\#'},
                       ]}
        for line in self._d.cmd(cmds).replace('\r','').split('\n'):
            config += line+'\n'
            if line.startswith("end"):
               break
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def get_startup_config(self):
        self._d.log_info('getting device startup configuration')
        config = ''
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\#'},
                        {'cmd': 'show startup-config',       'prompt':'\#'},
                       ]}
        for line in self._d.cmd(cmds).replace('\r','').split('\n'):
            config += line+'\n'
            if line.startswith("end"):
               break
        self._d.log_debug('got device startup configuration \n{0}'.format(config))
        return config

    def save_config(self):
        self._d.log_info('save running configuration')
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': 'write' , 'prompt':'\#'},
                        {'cmd': chr(26) , 'prompt':'\#'}
                       ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)
        self._d.load_system()
 
    def update(self, name, filename=''):
        self._d.log_info("upgrading image {0}".format(name))

        if (os.path.exists(name) == False):
            raise KeyError('image {0} not available'.format(name))

        self._d.file.create(name=filename, filename=name)
        boot_cmd = 'boot system {0}'.format(filename)
        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\#'},
                         {'cmd': boot_cmd, 'prompt': '\#', 'timeout' : 10000},
                         {'cmd': 'reboot', 'prompt': ''  },
                         {'cmd': 'y'     , 'prompt': '\#'}
                        ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)

    def shell_init(self):
        self._d.log_info('shell_init')
        return [{'cmd': 'terminal length 0', 'prompt':'[\>\#]'},]

    def shell_prompt(self):
        self._d.log_info('shell_prompt')
        return r'[\>\#]'

    def ping(self):
        self._d.log_info('ping')
        self._d.cmd('show version', use_cache=False)
