# -*- coding: utf-8 -*-
import re
import ply.lex as lex

class VlanConfigLexer(object):
    states = (
        ('vlandb','exclusive'),
        ('vlaninterface','exclusive'),
    )

    tokens = (
        'VLANLIST',
        'name',
    )

    def t_INITIAL_VLANDB_START(self, t):
        r'vlan\s+database'
        t.lexer.begin('vlandb')

    def t_vlandb_vlaninterface_end(self, t):
        r'exit'
        t.lexer.begin('INITIAL')

    def t_vlandb_VLANLIST(self, t):
        r'vlan\s+[^\n]+'
        t.value = re.split('\s+',t.value)[1]
        return t

    def t_INITIAL_VLANINTERFACE_START(self, t):
        r'interface\s+vlan\s+\d+'
        t.lexer.begin('vlaninterface')
        t.value = re.split('\s+',t.value)[2]
        t.lexer.id = t.value

    def t_vlaninterface_name(self, t):
        r'name\s+(\"[^\"]*\"|\w+)'
        v = re.split('\s+',t.value,maxsplit=1)
        if v[1].startswith('"') and v[1].endswith('"'):
            t.value = (t.lexer.id, v[1][1:-1])
        else:
            t.value = (t.lexer.id, v[1])
        return t

    t_ANY_ignore  = ' \t'

    def   t_ANY_SKIP(self,t):
        r'[a-z].*'
        pass

    def t_ANY_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(self, t): #pragma: no cover
        t.lexer.skip(1)

    def __init__(self, debug=0):
        self._debug = debug
        self.lexer = lex.lex(object=self, debug=debug)

    def run(self, data):
        self.lexer.input(data)
        result = {'1': {'name':'1'}}
        for tok in self.lexer:
            if tok.type == 'VLANLIST':
                for vid in tok.value.split(','):
                    result[vid] = {'name': vid}
                continue
            if tok.type == 'name':
                result[tok.value[0]]['name'] = tok.value[1]

        return result

