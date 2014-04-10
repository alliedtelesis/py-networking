# -*- coding: utf-8 -*-
import re
from time import sleep
import socket
import logging

log = logging.getLogger(__name__)

class awp_config(object):
    """
    Configuration feature implementation for AWP
    """
    def __init__(self, device):
        self._device =  device

    def get_config(self):
        config = self._device.cmd('show running-config').replace('\r','').split('\n')
        return '\n'.join(config)

    def send_config(self, config):
        log.debug("Executing config {0}".format(config))
        chan = self._device.get_channel()
        if chan:
            try:
                chan.send('enable\n')
                self._eat_prompt(chan)
                chan.send('conf t\n')
                self._eat_prompt(chan)
                for line in config.split('\n'):
                    chan.send(line+'\n')
                    self._eat_prompt(chan)
                chan.send('logout\n')
            except:
                raise
            return True
                
        return False

    def _eat_prompt(self,chan, prompt=r'[\>\#]{1}',timeout=5):
        chan.settimeout(timeout)
        try:
            buff = ''
            while True:
                buff += chan.recv(999)
                if re.search(prompt,buff):
                    return 
        except socket.timeout:
            pass

        if not re.search(prompt,buff):
            raise socket.timeout



