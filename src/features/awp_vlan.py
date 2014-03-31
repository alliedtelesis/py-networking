# -*- coding: utf-8 -*-
from pynetworking import Feature
import re
import ply.lex as lex
from pprint import pprint

class awp_vlan(Feature):
    """
    Vlan feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._vlan={}

    def load_config(self, config):
        l = _VlanDbLexer()
        self._vlan = l.run(config)

    def create(self, vlan_id, **kwargs):
        cmd = "vlan database\nvlan {0}".format(vlan_id)
        if len(self._get_vlan_ids(vlan_id)) == 1:
            if 'name' in kwargs:
                cmd += " name {0}".format(kwargs['name'])
        if 'mtu' in kwargs:
            cmd += " mtu {0}".format(int(kwargs['mtu']))
        if 'state' in kwargs:
            if kwargs['state'] == 'enable' or kwargs['state'] == 'disable':
                cmd += " state {0}".format(kwargs['state'])
            else:
                raise ValueError("{0} is and invalid vlan state".format(kwargs['state'])) 

        self._device.cfg.send_config(cmd)
        self._device.load_config()

    def delete(self, vlan_id):
        self._get_vlan_ids(vlan_id)
        self._device.cfg.send_config("vlan database\nno vlan {0}".format(vlan_id))
        self._device.load_config()

    def update(self, vlan_id, **kwargs):
        vlan_ids = self._get_vlan_ids(vlan_id)
        existing_vlan_ids = []
        for i in self._vlan.keys():
            existing_vlan_ids += self._get_vlan_ids(i)

        non_existing_ids = [i for i in vlan_ids if i not in existing_vlan_ids]

        if len(non_existing_ids) == 0:
            self.create(vlan_id, **kwargs)
        else:
            raise KeyError('{0} vlans do not exist'.format(non_existing_ids))

    def __str__(self):
        return str(self._vlan)

    def __getitem__(self, key):
        key = int(key)
        ret = {}
        for vlan_id,vlan in self._vlan.items():
            if key in self._get_vlan_ids(vlan_id):
                ret = dict(ret.items() + vlan.items())

        if ret:
            return ret
        raise KeyError('{0} key does not exist'.format(key))

    def _get_vlan_ids(self, vlan_id):
        vlan_id = str(vlan_id)
        m  = re.match('^\d+(,\d+)*$', vlan_id)
        if m:
            return map(int,vlan_id.split(','))
        m = re.search('^(?P<start>\d+)\-(?P<end>\d+)$',vlan_id)
        if m:
            return range(int(m.group('start')),int(m.group('end')))
        raise ValueError('{0} is not a valid vlan id, range or list'.format(vlan_id))

class _VlanDbLexer(object):
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
        r'name\s+[a-zA-Z][a-zA-Z0-9]*'
        t.value = (t.lexer.id, re.split('\s+',t.value)[1])
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

    def t_INITIAL_END(self, t):
        r'end'
        pass

    # Error handling rule
    def t_ANY_error(self, t):
        print "Illegal character '%s'" % t.value[0]
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



