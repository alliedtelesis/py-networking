# -*- coding: utf-8 -*-
import re
import json
import ply.lex as lex
from pprint import pformat
from pynetworking import Feature
from pprint import pprint
#from pynetworking.features.awp_interface_config_lexer import InterfaceConfigLexer
#from pynetworking.features.ats_interface_status_lexer import InterfaceStatusLexer
from collections import OrderedDict

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
        self._d.log_debug("Configuration {0}".format(pformat(json.dumps(self._interface_config))))

        ifre = re.compile('(?P<stack_no>\d)/(?P<ifp>[eg])(?P<ifn>\d+)\s+'
                          '(?P<description>[ \w\_]+)')
        for line in self._device.cmd("show interfaces description").split('\n'):
            m = ifre.match(line)
            if m and m.group('description') != '':
                self._d.log_debug("description for {0} is '{1}'".format(ifn, m.group('description')))
                ifn = int(m.group('ifn'))
                if self._d.facts['model'] == 'AT-8000S/24' and m.group('ifp') == 'g':
                    ifn += 24
                elif self._d.facts['model'] == 'AT-8000S/48' and m.group('ifp') == 'g':
                    ifn += 48
                ifn = '{0}.0.{1}'.format(m.group('stack_no'), ifn)
                self._interface_config[ifn]['description'] = m.group('description')

    def update(self, ifn, **kwargs):
        self._d.log_info("update {0} {1}".format(ifn,pformat(kwargs)))

    def items(self):
        self._update_interface()
        return self._interface.items()

    def __str__(self):
        self._update_interface()
        return json.dumps(self._interface)

    __repr__ = __str__

    def __getitem__(self, ifn):
        self._update_interface()
        if ifn in self._interface.keys():
            return self._interface[ifn]
        raise KeyError('{0} key does not exist'.format(key))

    def _get_interface_ns(self, ifn):
        ifn = str(ifn)
        m  = re.match('^(?P<prefix>\d+\.\d+\.)(?P<start_no>\d+)\-\d+\.\d+\.(?P<end_no>\d+)$', ifn)
        if m:
            ret = ['{0}{1}'.format(m.group('prefix'),n) for n in range(int(m.group('start_no')),1+int(m.group('end_no')))]
            return ret 
        else:
            return [ifn]

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



