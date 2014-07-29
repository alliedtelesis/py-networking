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
 
    def update_firmware(self, filename, protocol='http'):
        self._d.log_info("firmware upgrade with {0}".format(filename))

        devfilename = filename.split('/')[-1]
        devfileext = devfilename.split('.')[-1]
        if (devfileext != 'rel'):
            self._d.log_info("firmware name {0} should have .rel extension".format(filename))
            devfilename = devfilename + '.rel'

        if (protocol != 'http'):
            raise KeyError('protocol {0} not supported'.format(protocol))
        if (self._check_running_software(devfilename) == True):
            raise KeyError('cannot overwrite running firmware ({0})'.format(devfilename))
        if (os.path.exists(filename) == False):
            raise KeyError('firmware {0} not available'.format(filename))
        if ('licensed' in self._d.facts.keys()):
            if (self._d.facts['licensed'] == False):
                raise KeyError('unlicensed software running')
            else:
                self._d.log_info('licensed software running')

        self._d.file.create(name=filename, filename=devfilename)
        boot_cmd = 'boot system {0}'.format(devfilename)
        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\(config\)\#'},
                         {'cmd': boot_cmd, 'prompt': '\(config\)\#', 'timeout' : 10000},
                         {'cmd': chr(26) , 'prompt': '\#'},
                         {'cmd': 'reboot', 'prompt': ''},
                         {'cmd': 'y'     , 'prompt': '' , 'dontwait': True}
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

    def _check_running_software(self, release):
        is_running_software = False
        string_to_be_found = 'Current software   : ' + release

        # Boot configuration
        # ----------------------------------------------------------------
        # Current software   : x210-5.4.4.rel
        # Current boot image : flash:/x210-5.4.4.rel
        # Backup  boot image : flash:/x210-5.4.4.rel
        # Default boot config: flash:/default.cfg
        # Current boot config: flash:/my.cfg (file exists)
        # Backup  boot config: flash:/backup.cfg (file not found)
        for line in self._d.cmd("show boot").split('\n'):
            self._d.log_debug("read {0}".format(line))
            if (line.find(string_to_be_found) == 0):
                is_running_software = True
                break

        return is_running_software
