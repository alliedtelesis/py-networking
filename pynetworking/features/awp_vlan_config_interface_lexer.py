# -*- coding: utf-8 -*-
import re
import ply.lex as lex
from pprint import pprint

class VlanInterfaceConfigLexer(object):
    states = (
        ('ifport','exclusive'),
        ('ifportrange','exclusive'),
    )

    tokens = (
        'IF_PORT',
        'IF_PORT_RANGE',
        'IF_VLAN',
        'switchport_mode',
        'END',
    )

    def t_if_end(self, t):
        r'!.*'
        t.lexer.begin('INITIAL')

    def t_INITIAL_IF_PORT_RANGE(self, t):
        r'interface\s+port\d+\.\d+\.\d+\-\d+\.\d+\.\d+\s*\n'
        t.value = re.split('\s+',t.value)[1][4:]
        t.lexer.push_state('ifportrange')
        t.lexer.id = t.value

    def t_INITIAL_IF_PORT(self, t):
        r'interface\s+port\d+\.\d+\.\d+\s*\n'
        t.value = re.split('\s+',t.value)[1][4:]
        t.lexer.push_state('ifport')
        t.lexer.id = t.value

    def t_ifport_ifportrange_switchport_mode(self, t):
        r'switchport\s+mode\s+(access|trunk)'
        v = re.split('\s+', t.value, maxsplit=2)
        t.value = (t.lexer.id, v[2])
        return t

    def t_ifport_ifportrange_end(self, t):
        r'!.*'
        t.lexer.pop_state()

    def t_ANY_newline(self, t):
        r'\n+'
        pass

    t_ANY_ignore  = ' \t'

    def t_ifport_ifportrange_SKIP(self,t):
        r'[a-z].*\n'
        pass

    def t_INITIAL_SKIP(self,t):
        r'[a-z].*'
        pass

    def t_INITIAL_comment(self, t):
        r'!.*'
        pass

    def t_ANY_error(self, t): #pragma: no cover
        print "Illegal character '%s'" % t.value[0]
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = lex.lex(object=self,debug=0)

    def run(self, data):
        self.lexer.input(data)
        result = {}
        for tok in self.lexer:
            if tok.value[0] in result.keys():
                result[tok.value[0]][tok.type.replace('_',' ')]=tok.value[1]
            else:
                result[tok.value[0]] = {tok.type.replace('_',' '):tok.value[1]}
        return result


