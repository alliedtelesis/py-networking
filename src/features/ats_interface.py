# -*- coding: utf-8 -*-
import re
import json
from pprint import pformat
from pynetworking import Feature
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

class ats_interface(Feature):
    """
    Interface feature implementation for ATS
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._interface_config={}
        self._interface={}
        self._d = device

    def load_config(self, config):
        self._d.log_info("load_config")
        self._d.log_debug("Loading config for ats_interface {0}".format(config))
        self._interface_config = OrderedDict()
        # 1/e1     100M-Copper  Full    100    Enabled  Off      Up      Disabled Auto
        ifre = re.compile('(?P<stack_no>\d)/(?P<ifp>[eg])(?P<ifn>\d+)\s+'
                          '(?P<type>[^\s]+)\s+'
                          '(?P<configured_duplex>[^\s]+)\s+'
                          '(?P<configured_speed>[^\s]+)\s+'
                          '(?P<negotiation>[^\s]+)\s+'
                          '(?P<flow_control>[^\s]+)\s+'
                          '(?P<enable>(Up|Down))\s+'
                          '(?P<back_pressure>[^\s]+)\s+'
                          '(?P<configured_polarity>[^\s]+)\s+')
        for line in self._device.cmd("show interfaces configuration").split('\n'):
            m = ifre.match(line)
            if m:
                if m.group('configured_speed') == '--':
                    continue
                ifn = int(m.group('ifn'))
                if self._d.facts['model'] == 'AT-8000S/24' and m.group('ifp') == 'g':
                    ifn += 24
                elif self._d.facts['model'] == 'AT-8000S/48' and m.group('ifp') == 'g':
                    ifn += 48
                ifn = '{0}.0.{1}'.format(m.group('stack_no'), ifn)

                if m.group('enable') == 'Up':
                    enable = True
                else:
                    enable = False

                self._interface_config[ifn] = { 'enable': enable,
                                                'configured_speed': m.group('configured_speed'),
                                                'configured_duplex': m.group('configured_duplex').lower(),
                                                'configured_polarity': m.group('configured_polarity').lower(),
                                               }

        ifre = re.compile('(?P<stack_no>\d)/(?P<ifp>[eg])(?P<ifn>\d+)\s+'
                          '(?P<description>[ \w\_]+)')
        for line in self._device.cmd("show interfaces description").split('\n'):
            m = ifre.match(line)
            if m and m.group('description') != '':
#                self._d.log_debug("description for {0} is '{1}'".format(ifn, m.group('description')))
                ifn = int(m.group('ifn'))
                if self._d.facts['model'] == 'AT-8000S/24' and m.group('ifp') == 'g':
                    ifn += 24
                elif self._d.facts['model'] == 'AT-8000S/48' and m.group('ifp') == 'g':
                    ifn += 48
                ifn = '{0}.0.{1}'.format(m.group('stack_no'), ifn)
                if ifn in self._interface_config:
                    self._interface_config[ifn]['description'] = m.group('description')
        self._d.log_debug("Configuration {0}".format(pformat(json.dumps(self._interface_config))))

    def update(self, ifn, **kwargs):
        self._d.log_info("update {0} {1}".format(ifn,pformat(kwargs)))
        self._update_interface()
        if ifn not in self._interface.keys():
            raise ValueError('interface {0} does not exist'.format(ifn))

        cmds = {'cmds':[{'cmd': 'conf',                                         'prompt':'\(config\)\#'},
                        {'cmd': 'interface ethernet '+self._to_ifn_native(ifn), 'prompt':'\(config-if\)\#'},
                       ]}
        run_cmd = False
        if 'description' in kwargs:
            description = kwargs['description']
            if ' ' in description:
                description = '"{0}"'.format(description)
            if 'description' in self._interface[ifn] and self._interface[ifn]['description'] == description:
                return

            run_cmd = True
            cmds['cmds'].append({'cmd': 'description {0}'.format(description),'prompt':'\(config-if\)\#'})

        if run_cmd:
            cmds['cmds'].append({'cmd': chr(26),                               'prompt':'\#'})
            self._device.cmd(cmds, cache=False, flush_cache=True)
            self._device.load_system()

    def items(self):
        self._update_interface()
        return self._interface.items()

    def keys(self):
        self._update_interface()
        return self._interface.keys()

    def __str__(self):
        self._update_interface()
        return json.dumps(self._interface)

    __repr__ = __str__  #pragma: no cover

    def __getitem__(self, ifn):
        self._update_interface()
        if ifn in self._interface.keys():
            return self._interface[ifn]
        raise IndexError

    def _update_interface(self):
        self._d.log_info("_update_interface")
        self._interface = OrderedDict()
        # 1/e1     100M-Copper  Full    100   Enabled  Off  Up          Disabled Off
        ifre = re.compile('(?P<stack_no>\d)/(?P<ifp>[eg])(?P<ifn>\d+)\s+'
                          '(?P<type>[^\s]+)\s+'
                          '(?P<current_duplex>[^\s]+)\s+'
                          '(?P<current_speed>[^\s]+)\s+'
                          '(?P<negotiation>[^\s]+)\s+'
                          '(?P<flow_control>[^\s]+)\s+'
                          '(?P<link>(Up|Down))\s+'
                          '(?P<current_polarity>[^\s]+)\s+'
                          '[^\n]+')
        for line in self._device.cmd("show interfaces status").split('\n'):
            m = ifre.match(line)
            if m:
                ifn = int(m.group('ifn'))
                if self._d.facts['model'] == 'AT-8000S/24' and m.group('ifp') == 'g':
                    ifn += 24
                elif self._d.facts['model'] == 'AT-8000S/48' and m.group('ifp') == 'g':
                    ifn += 48
                
                ifn = '{0}.0.{1}'.format(m.group('stack_no'), ifn)

                if m.group('link') == 'Up':
                    if m.group('current_polarity') == 'Off':
                        self._interface[ifn] = {'link': True,
                                                'current_speed': m.group('current_speed'),
                                                'current_duplex': m.group('current_duplex').lower(),
                                                'current_polarity': 'mdi'
                                               } 
                    else:
                        self._interface[ifn] = {'link': False,
                                                'current_speed': m.group('current_speed'),
                                                'current_duplex': m.group('current_duplex').lower(),
                                                'current_polarity': 'mdix'
                                               } 
                else:
                    self._interface[ifn] = {'link': False }
                self._interface[ifn] = dict(self._interface[ifn].items() + self._interface_config[ifn].items())

        self._d.log_debug("Status {0}".format(pformat(json.dumps(self._interface))))

    def _to_ifn_native(self, ifn):
        self._d.log_info("_to_ifn_native "+ifn)
        stack_no = ifn.split('.')[0]
        if_no = int(ifn.split('.')[2])
        if self._d.facts['model'] == 'AT-8000S/24' and if_no > 24:
            return "{0}/g{1}".format(stack_no, if_no-24)
        elif self._d.facts['model'] == 'AT-8000S/48'and if_no > 48:
            return "{0}/g{1}".format(stack_no, if_no-48)
        else:
            return "{0}/e{1}".format(stack_no, if_no)

