# -*- coding: utf-8 -*-
import re
import ply.lex as lex
from pprint import pprint
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

class InterfaceStatusLexer(object):
    states = (
        ('if','exclusive'),
        ('lo','exclusive'),
        ('vlan','exclusive'),
    )

    tokens = (
        'link',
        'enable',
        'hardware',
        'current_duplex',
        'current_speed',
        'current_polarity',
        'configured_duplex',
        'configured_speed',
        'configured_polarity',
    )

    def t_INITIAL_IF(self, t):
        r'Interface\s+port\d+\.\d+\.\d+\s*\n'
        t.value = re.split('\s+',t.value)[1][4:]
        t.lexer.push_state('if')
        t.lexer.id = t.value

    def t_INITIAL_VLAN(self, t):
        r'Interface\s+vlan\d+\s*\n'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('vlan')
        t.lexer.id = t.value

    def t_INITIAL_LO(self, t):
        r'Interface\s+lo\d*\s*\n'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('lo')
        t.lexer.id = t.value

    def t_if_lo_vlan_link(self,t):
        r'\s+Link\sis\s(UP|DOWN)'
        if re.split('\s+',t.value)[3] == 'UP':
            t.value = (t.lexer.id,True)
        else:
            t.value = (t.lexer.id,False)
        return t

    def t_if_lo_vlan_enable(self,t):
        r'administrative\s+state\s+is\s+(UP|DOWN)'
        if re.split('\s+',t.value)[3] == 'UP':
            t.value = (t.lexer.id,True)
        else:
            t.value = (t.lexer.id,False)
        return t

    def t_if_lo_vlan_current_duplex(self,t):
        r'current\s+duplex\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    def t_if_lo_vlan_current_speed(self,t):
        r'current\s+speed\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    def t_if_lo_vlan_configured_polarity(self,t):
        r'configured\s+polarity\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    def t_if_lo_vlan_configured_duplex(self,t):
        r'configured\s+duplex\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    def t_if_lo_vlan_configured_speed(self,t):
        r'configured\s+speed\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    def t_if_lo_vlan_current_polarity(self,t):
        r'current\s+polarity\s+\w+'
        t.value = (t.lexer.id,re.split('\s+',t.value)[2])
        return t

    t_ANY_ignore  = ' \t'

    def t_if_lo_vlan_end_section(self, t):
        r'Time\s+since\s+last\s+state\s+change'
        t.lexer.pop_state()
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self, t): #pragma: no cover
        t.lexer.skip(1)

    def __init__(self,debug=0):
        self._debug = debug
        self.lexer = lex.lex(object=self,debug=debug)

    def run(self, data):
        self.lexer.input(data)
        result = OrderedDict()
        for tok in self.lexer:
            if tok.value[0] in result.keys():
                result[tok.value[0]][tok.type.replace('_',' ')]=tok.value[1]
            else:
                result[tok.value[0]] = {tok.type.replace('_',' '):tok.value[1]}
        return result


