# -*- coding: utf-8 -*-
import re
from time import sleep
import socket
import logging
import zmq
import json

log = logging.getLogger(__name__)

class awp_config(object):
    """
    Configuration feature implementation for AWP
    """
    def __init__(self, device):
        self._d =  device

    def get_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\n\w+\#'},
                        {'cmd': 'show running-config',       'prompt':'\n\w+\#'},
                       ]}
        for line in self._d.cmd(cmds).replace('\r','').split('\n'):
            config += line+'\n'
            if line.startswith("end"):
               break
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config



