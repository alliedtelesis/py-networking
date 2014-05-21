# -*- coding: utf-8 -*-
import re
import ply.lex as lex

class VlanConfigLexer(object):
    states = (
        ('vlandb','exclusive'),
        ('vlanid','exclusive'),
        ('vlanrange','exclusive'),
    )

    tokens = (
        'VLAN_RANGE',
        'VLAN_ID',
        'VLAN_LIST',
        'name',
        'mtu',
        'state',
        'END',
        'VLAN_DB',
    )

    def t_INITIAL_VLANDB_START(self, t):
        r'vlan\s+database'
        t.lexer.begin('vlandb')

    def t_vlandb_end(self, t):
        r'!.*'
        t.lexer.begin('INITIAL')

    def t_vlandb_VLAN_RANGE(self, t):
        r'vlan\s+\d+\-\d+'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('vlanrange')
        t.lexer.id = t.value

    def t_vlandb_VLAN_LIST(self, t):
        r'vlan\s+\d+(\,\d+)+'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('vlanrange')
        t.lexer.id = t.value

    def t_vlandb_VLAN_ID(self, t):
        r'vlan\s+\d+'
        t.value = re.split('\s+',t.value)[1]
        t.lexer.push_state('vlanid')
        t.lexer.id = t.value

    def t_vlanid_name(self, t):
        r'name\s+(\"[^\"]*\"|\w+)'
        v = re.split('\s+',t.value,maxsplit=1)
        if v[1].startswith('"') and v[1].endswith('"'):
            t.value = (t.lexer.id, v[1][1:-1])
        else:
            t.value = (t.lexer.id, v[1])
        return t

    def t_vlanid_vlanrange_mtu(self, t):
        r'mtu\s+[0-9]+'
        t.value = (t.lexer.id, int(re.split('\s+',t.value)[1]))
        return t

    def t_vlanid_vlanrange_state(self, t):
        r'state\s+(enable|disable)'
        t.value = (t.lexer.id, re.split('\s+',t.value)[1])
        return t

    def t_vlanid_vlanrange_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.lexer.pop_state()

    def t_INITIAL_vlandb_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ANY_ignore  = ' \t'

    def   t_INITIAL_SKIP(self,t):
        r'[a-z].*'
        pass

    def t_ANY_comment(self, t):
        r'!.*'
        pass

    def t_ANY_error(self, t): #pragma: no cover
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = lex.lex(object=self)

    def run(self, data):
        self.lexer.input(data)
        result = {}
        for tok in self.lexer:
            if tok.value[0] in result.keys():
                result[tok.value[0]][tok.type]=tok.value[1]
            else:
                result[tok.value[0]] = {tok.type:tok.value[1]}

        return result

