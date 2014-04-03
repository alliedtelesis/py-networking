# -*- coding: utf-8 -*-
from pynetworking import Feature
from pynetworking.features.awp_vlan_config_lexer import VlanConfigLexer
from pynetworking.features.awp_vlan_status_lexer import VlanStatusLexer
import re
from pprint import pprint

class awp_vlan(Feature):
    """
    Vlan feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._vlan_config={}
        self._vlan={}

    def load_config(self, config):
        l = VlanConfigLexer()
        self._vlan_config = l.run(config)
        self._update_vlan()

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
        for i in self._vlan_config.keys():
            existing_vlan_ids += self._get_vlan_ids(i)

        non_existing_ids = [i for i in vlan_ids if i not in existing_vlan_ids]

        if len(non_existing_ids) == 0:
            self.create(vlan_id, **kwargs)
        else:
            raise KeyError('{0} vlans do not exist'.format(non_existing_ids))

    def __str__(self):
        self._update_vlan()
        return str(self._vlan)

    def __getitem__(self, vid):
        self._update_vlan()
        vid = str(vid)
        if vid in self._vlan:
            return self._vlan[vid]
        raise KeyError('vlan id {0} does not exist'.format(vid))

    def _get_vlan_ids(self, vlan_id):
        vlan_id = str(vlan_id)
        m  = re.match('^\d+(,\d+)*$', vlan_id)
        if m:
            return map(int,vlan_id.split(','))
        m = re.search('^(?P<start>\d+)\-(?P<end>\d+)$',vlan_id)
        if m:
            return range(int(m.group('start')),int(m.group('end'))+1)
        raise ValueError('{0} is not a valid vlan id, range or list'.format(vlan_id))

    def _update_vlan(self):
        l = VlanStatusLexer()
        vlan = l.run(self._device.cmd("show vlan all"))
        for vln,vli in vlan.items():
            for vlr,vlc in self._vlan_config.items():
                if int(vln) in self._get_vlan_ids(vlr):
                    vlan[vln] = dict(vlan[vln].items() + vlc.items())
        self._vlan = vlan


