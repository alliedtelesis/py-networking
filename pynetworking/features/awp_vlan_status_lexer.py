# -*- coding: utf-8 -*-
import re
import ply.lex as lex
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

class VlanStatusLexer(object):
    tokens = (
        'VLAN',
        'INTERFACE',
    )

    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_INITIAL_VLAN(self, t):
        r'\d+\s+(\w+|\"[^\"]+\")+\s*\n*\s*(STATIC|DYNAMIC)\s+(ACTIVE)'
        if t.lexer.lineno >3:
            v = re.match(r'(\d+)\s+((\w+)|\"([^\"]+)\")+\s*\n*\s*(STATIC|DYNAMIC)\s+(ACTIVE)',t.value)
            if v.group(3):
                t.value = (v.group(1),v.group(3),v.group(5),v.group(6))
            else:
                t.value = (v.group(1),v.group(4),v.group(5),v.group(6))
            t.lexer.id = v.group(1)
            return t

    def t_INITIAL_INTERFACE(self, t):
        r'port\d+\.\d+\.\d+\((u|t)\)'
        v = t.value[4:-1].split('(')
        t.value = (t.lexer.id,v[0],v[1])
        return t 

    t_ANY_ignore  = ' \t'

    def t_ANY_error(self, t): #pragma: no cover
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = lex.lex(object=self, debug = 0)

    def run(self, data):
        self.lexer.input(data)
        result = OrderedDict()
        for tok in self.lexer:
            if tok.type == 'VLAN':
                result[tok.value[0]] = {
                                        'name' : tok.value[1],
                                        'type' : tok.value[2],
                                        'current state' : tok.value[3],
                                        'tagged':(),
                                        'untagged':()
                                       }
            elif tok.type == 'INTERFACE' and tok.value[2] == 'u':
                result[tok.value[0]]['untagged'] += (tok.value[1],)
            elif tok.type == 'INTERFACE' and tok.value[2] == 't':
                result[tok.value[0]]['tagged'] += (tok.value[1],)
        return result



