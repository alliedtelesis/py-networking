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
        self._device =  device

    def get_config(self):
        config = ''
        for line in self._device.cmd('show running-config').replace('\r','').split('\n'):
            config += line+'\n'
            if line.startswith("end"):
               break
        return config

    def send_config(self, config):
        log.debug("Executing config {0}".format(config))
        cmds = {'cmds':[{'cmd':'enable','prompt': ''}, {'cmd':'conf t','prompt':''}]}

        for line in config.split('\n'):
            cmds['cmds'].append({'cmd':line,'prompt':''})
        
        return self._device.cmd(cmds)


