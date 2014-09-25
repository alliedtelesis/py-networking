# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
from time import sleep
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_ntp(Feature):
    """
    ntp feature implementation for ATS
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._ntp={}
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")
        self._ntp = OrderedDict()

        #ntp address-table static xxxx.xxxx.xxxx forward interface port1.0.1 vlan 1
        ifre = re.compile('ntp\s+address-table\s+static\s+(?P<ntp>[^\s]+)\s+'
                          '(?P<action>[^\s]+)\s+'
                          'interface\s+(?P<interface>[^\s]+)\s+'
                          'vlan\s+(?P<vlan>\d+)')

        for line in config.split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = m.group('ntp')
                self._ntp[key] = {'vlan': m.group('vlan'),
                                  'interface': m.group('interface'),
                                  'action': m.group('action'),
                                  'type': 'static'
                                 }
        self._d.log_info(self._ntp)


    def create(self, address):
        self._d.log_info("add SNTP server {0}".format(address))
        self._update_ntp()

        if address in self._ntp.keys():
            raise KeyError('SNTP server {0} already added'.format(address))

        set_cmd = 'sntp server {0}'.format(address)
        cmds = {'cmds': [{'cmd': 'conf' , 'prompt': '\(config\)\#'},
                         {'cmd': set_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': chr(26), 'prompt': '\#'}
                        ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_ntp()


    # def update(self, ntp, interface, forward=True, vlan=1):
    #     self._d.log_info("update MAC address {0} entry".format(ntp))
    #     self._update_mac()
    #
    #     ntp = self._get_dotted_mac(ntp)
    #     if ntp not in self._ntp.keys():
    #         raise KeyError('MAC address {0} is not existing'.format(ntp))
    #
    #     fwd = 'forward'
    #     if (forward == False):
    #        fwd = 'discard'
    #     set_cmd = 'ntp address-table static {0} {1} interface {2} vlan {3}'.format(ntp, fwd, interface, vlan)
    #     cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
    #                      {'cmd': 'conf t', 'prompt': '\(config\)\#'},
    #                      {'cmd': set_cmd , 'prompt': '\(config\)\#'},
    #                      {'cmd': chr(26) , 'prompt': '\#'}
    #                     ]}
    #     self._device.cmd(cmds, cache=False, flush_cache=True)
    #     sleep(1)
    #     self._update_mac()


    def delete(self, address=''):
        self._d.log_info("remove SNTP server {0}".format(address))
        self._update_ntp()

        if address != '' and address not in self._ntp.keys():
            raise KeyError('SNTP server {0} not present'.format(address))

        del_cmd = 'no sntp server {0}'.format(address)
        cmds = {'cmds': [{'cmd': 'conf' , 'prompt': '\(config\)\#'},
                         {'cmd': del_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': chr(26), 'prompt': '\#'}
                        ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_ntp()


    def items(self):
        self._update_ntp()
        return self._ntp.items()


    def keys(self):
        self._update_ntp()
        return self._ntp.keys()


    def __getitem__(self, address):
        self._update_ntp()
        if address not in self._ntp.keys():
            raise KeyError('SNTP server {0} does not exist'.format(address))
        return self._ntp[address]


    def _update_ntp(self):
        self._d.log_info("_update_ntp")
        self._ntp = OrderedDict()

        # 1    port1.0.1    0000.cd1d.7eb0   forward   dynamic
        ifre = re.compile('(?P<address>[^\s]+)\s+'
                          '(?P<polltime>[^\s]+)\s+'
                          '(?P<status>[^\s]+)')
        self._device.cmd("terminal length 0")
        for line in self._device.cmd("show ntp status").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = m.group('address')
                self._ntp[key] = {'polltime': m.group('polltime'),
                                  'status': m.group('status')
                                 }
        self._d.log_debug("ntp {0}".format(pformat(json.dumps(self._ntp))))
