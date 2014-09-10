# -*- coding: utf-8 -*-
import re
import ply.lex as lex

class VlanConfigLexer(object):
    states = (
        ('vlandb','exclusive'),
        ('vlaninterface','exclusive'),
        # ('vlanrange','exclusive'),
)

    tokens = (
        'VLANLIST',
        'VLANRANGE',
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
        # r'vlan\s+\d+(\,\d+)+'
        print ("BEFORE SPLIT\n")
        print (t.value)
        t.value = re.split('\s+',t.value)[1]
        print ("AFTER SPLIT\n")
        print (t.value)
        print ("DONE\n")
        return t

    def t_vlandb_VLANRANGE(self, t):
        r'vlan\s+\d+\-\d+'
        print ("BEFORE SPLIT\n")
        print (t.value)
        t.value = re.split('\s+',t.value)[1]
        print ("AFTER SPLITTED\n")
        print (t.value)
        print ("DONE\n")
        # t.lexer.push_state('vlanrange')
        # # str = t.value
        # # a = str.split('-')[0]
        # # b = str.split('-')[1]
        # print ("RESPLIT\n")
        # print (a)
        # print ("\n")
        # print (b)
        # print ("RESPLIT\n")
        # t.value = a + ',' + b
        # t.lexer.push_state('vlanrange')
        # t.lexer.id = t.value
        return t

    # def t_vlanid_vlanrange_newline(self, t):
    #    r'\n+'
    #    t.lexer.lineno += len(t.value)
    #    t.lexer.pop_state()
    #
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
            print("tok is")
            print(tok)
            # if tok.type == 'VLANLIST':
            #     for vid in tok.value.split(','):
            #         result[vid] = {'name': vid}
            #     continue
            if tok.type == 'VLANLIST':
                for vid in tok.value.split(','):
                    print ("vid is \n")
                    print vid
                    if '-' in vid:
                        a = vid.split('-')[0]
                        b = vid.split('-')[1]
                        result[a] = {'name': a}
                        result[b] = {'name': b}
                    else:
                        result[vid] = {'name': vid}
                continue
            if tok.type == 'VLANRANGE':
                print('TO BE WRITTEN')
            if tok.type == 'name':
                result[tok.value[0]]['name'] = tok.value[1]

        return result
