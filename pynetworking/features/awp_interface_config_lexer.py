# -*- coding: utf-8 -*-
import re
import ply.lex as lex

class InterfaceConfigLexer(object):
    states = (
        ('ifport','exclusive'),
        ('ifportrange','exclusive'),
        ('ifvlan','exclusive'),
    )

    tokens = (
        'IF_PORT',
        'IF_PORT_RANGE',
        'IF_VLAN',
        'description',
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

    def t_INITIAL_IF_VLAN(self, t):
        r'interface\s+vlan\d+\s*\n'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('ifvlan')
        t.lexer.id = t.value

    def t_ifport_ifportrange_ifvlan_description(self, t):
        r'description\s+(\"[^\"]*\"|\w+)'
        v = re.split('\s+',t.value,maxsplit=1)
        if v[1].startswith('"') and v[1].endswith('"'):
            t.value = (t.lexer.id, v[1][1:-1])
        else:
            t.value = (t.lexer.id, v[1])
        return t

    def t_ifport_ifportrange_ifvlan_end(self, t):
        r'!.*'
        t.lexer.pop_state()

    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ANY_ignore  = ' \t'

    def t_ifport_ifportrange_ifvlan_SKIP(self,t):
        r'[a-z].*\n'
        pass

    def t_INITIAL_SKIP(self,t):
        r'[a-z].*'
        pass

    def t_INITIAL_comment(self, t):
        r'!.*'
        pass

    def t_ANY_error(self, t): #pragma: no cover
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


