# -*- coding: utf-8 -*-
import re
import json
import ply.lex as lex
from pprint import pformat
from pynetworking import Feature
from pprint import pprint
from pynetworking.features.awp_interface_config_lexer import InterfaceConfigLexer
from pynetworking.features.awp_interface_status_lexer import InterfaceStatusLexer

class awp_interface(Feature):
    """
    Interface feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._interface_config={}
        self._interface={}
        self._d = device

    def load_config(self, config):
        self._d.log_info("load_config")
        self._d.log_debug("Loading config for awp_interface {0}".format(config))
        l = InterfaceConfigLexer()
        self._interface_config = l.run(config)

    def update(self, ifn, **kwargs):
        self._d.log_info("update {0} {1}".format(ifn,pformat(kwargs)))
        self._update_interface()
        if ifn not in self._interface.keys():
            raise ValueError('interface {0} does not exist'.format(ifn))
        
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\#'},
                        {'cmd': 'conf t',                    'prompt':'\(config\)\#'},
                        {'cmd': 'interface port{0}'.format(ifn), 'prompt':'\(config-if\)\#'},
                       ]}  
        run_cmd = False
        if 'enable' in kwargs:
            if self._interface[ifn]['enable'] != kwargs['enable']:
                run_cmd = True
                if kwargs['enable']:
                    cmds['cmds'].append({'cmd': 'no shutdown','prompt':'\(config-if\)\#'})
                else:
                    cmds['cmds'].append({'cmd': 'shutdown','prompt':'\(config-if\)\#'})
        elif 'description' in kwargs:
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

    def __str__(self):
        self._update_interface()
        return json.dumps(self._interface)

    __repr__ = __str__  #pragma: no cover

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
        l = InterfaceStatusLexer()
        self._interface = l.run(self._device.cmd("show interface"))
        for ifn,ifi in self._interface.items():
            for ifr,ifc in self._interface_config.items():
                if ifn in self._get_interface_ns(ifr):
                    self._d.log_debug("Updating {0} with {1}".format(ifn,ifc))
                    self._interface[ifn] = dict(self._interface[ifn].items() + ifc.items())
        self._d.log_debug("Loaded awp_interface {0}".format(pformat(json.dumps(self._interface))))



