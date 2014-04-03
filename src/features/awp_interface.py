# -*- coding: utf-8 -*-
from pynetworking import Feature
import re
import ply.lex as lex
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
        self._device = device

    def load_config(self, config):
        l = InterfaceConfigLexer()
        self._interface_config = l.run(config)
        self._update_interface()

    def update(self, ifn, **kwargs):
        pass

    def items(self):
        self._update_interface()
        return self._interface.items()

    def __str__(self):
        self._update_interface()
        return str(self._interface)

    __repr__ = __str__

    def __getitem__(self, ifn):
        self._update_interface()
        if ifn in self._interface:
            return self._interface[ifn]
        raise KeyError('{0} key does not exist'.format(key))

    def _get_interface_ns(self, ifn):
        ifn = str(ifn)
        m  = re.match('^port(?P<prefix>\d+\.\d+\.)(?P<start_no>\d+)\-\d+\.\d+\.(?P<end_no>\d+)$', ifn)
        if m:
            ret = ['port{0}{1}'.format(m.group('prefix'),n) for n in range(int(m.group('start_no')),1+int(m.group('end_no')))]
            return ret 
        else:
            return [ifn]

    def _update_interface(self):
        l = InterfaceStatusLexer()
        self._interface = l.run(self._device.cmd("show interface"))
        for ifn,ifi in self._interface.items():
            for ifr,ifc in self._interface_config.items():
                if ifn in self._get_interface_ns(ifr):
                    self._interface[ifn] = dict(self._interface[ifn].items() + ifc.items())



