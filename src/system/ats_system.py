# -*- coding: utf-8 -*-
import re
from time import sleep
import socket
import logging
import zmq
import json

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
            if line.startswith("end"):
               break
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def shell_init(self):
        self._d.log_info('shell init')
        return [{'cmd': 'terminal datadump', 'prompt':r'[\n\r]+[\w\_]+\#'},]

    def ping(self):
        self._d.log_info('ping')
        self._d.cmd('show version')
        
