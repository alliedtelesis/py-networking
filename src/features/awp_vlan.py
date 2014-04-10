# -*- coding: utf-8 -*-
from pynetworking import Feature
from pynetworking.features.awp_vlan_config_lexer import VlanConfigLexer
from pynetworking.features.awp_vlan_status_lexer import VlanStatusLexer
from pynetworking.features.awp_vlan_config_interface_lexer import VlanInterfaceConfigLexer
import re
from pprint import pprint
import json

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
        l = VlanInterfaceConfigLexer()
        self._interface_config = l.run(config)

    def create(self, vlan_id, **kwargs):
        self._update_vlan()
        cmd = "vlan database\nvlan {0}".format(vlan_id)
        if len(self._get_vlan_ids(vlan_id)) == 1:
            if 'name' in kwargs:
                if ' ' in kwargs['name']:
                    cmd += ' name "{0}"'.format(kwargs['name'])
                else:
                    cmd += " name {0}".format(kwargs['name'])
        if 'mtu' in kwargs:
            cmd += " mtu {0}".format(int(kwargs['mtu']))
        if 'state' in kwargs:
            if kwargs['state'] == 'enable' or kwargs['state'] == 'disable':
                cmd += " state {0}".format(kwargs['state'])
            else:
                raise ValueError("{0} is and invalid vlan state".format(kwargs['state'])) 

        self._device.cfg.send_config(cmd)
        #self._device.load_config()

    def delete(self, vlan_id):
        self._update_vlan()
        self._get_vlan_ids(vlan_id)
        self._device.cfg.send_config("vlan database\nno vlan {0}".format(vlan_id))
        #self._device.load_config()

    def update(self, vlan_id, **kwargs):
        self._update_vlan()
        vlan_ids = self._get_vlan_ids(vlan_id)
        existing_vlan_ids = []
        for i in self._vlan_config.keys():
            existing_vlan_ids += self._get_vlan_ids(i)

        non_existing_ids = [i for i in vlan_ids if i not in existing_vlan_ids]

        if len(non_existing_ids) == 0:
            self.create(vlan_id, **kwargs)
        else:
            raise KeyError('{0} vlans do not exist'.format(non_existing_ids))

    def add_interface(self, vid, ifn, tagged=False):
        self._update_vlan()
        vid = str(vid)
        if vid not in self._vlan:
            raise ValueError('{0} is not a valid vlan id'.format(vid))

        ifi = self._get_interface_config(ifn)
        if not ifi:    
            raise ValueError('{0} is not a valid interface'.format(ifn))
    
        if 'switchport mode' not in ifi:
            raise ValueError('{0} interface does not support vlan'.format(ifn))

        if ifi['switchport mode'] == 'access' and tagged == False:
            self._device.cfg.send_config('interface {0}\nswitchport access vlan {1}'.format(ifn,vid))
        elif ifi['switchport mode'] == 'access' and tagged == True:
            ## should copy access vlan to native
            self._device.cfg.send_config('interface {0}\nswithport mode trunk\nswitchport trunk allowed vlan add {1}'.format(ifn,vid))
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            self._device.cfg.send_config('interface {0}\nswitchport trunk native vlan {1}'.format(ifn,vid))
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            self._device.cfg.send_config('interface {0}\nswitchport trunk allowed vlan add {1}'.format(ifn,vid))
        else:
            raise ValueError('interface {0} cannot be added to vlan {1}'.format(ifn,vid))

        #self._device.load_config()


    def delete_interface(self, vid, ifn):
        self._update_vlan()
        vid = str(vid)
        if vid not in self._vlan:
            raise ValueError('{0} is not a valid vlan id'.format(vid))

        if 'tagged' in self._vlan[vid] and ifn in self._vlan[vid]['tagged']:
                tagged = True
        if 'untagged' in self._vlan[vid] and ifn in self._vlan[vid]['untagged']:
                tagged = False
        else:
            raise ValueError('interface {0} does not belong to vlan {1}'.format(ifn,vid))

        ifi = self._get_interface_config(ifn)
        if not ifi:    
            raise ValueError('{0} is not a valid interface'.format(ifn))
    
        if ifi['switchport mode'] == 'access':
            # this actually move port back to vlan 1
            self._device.cfg.send_config('interface {0}\nno switchport access vlan'.format(ifn))
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            self._device.cfg.send_config('interface {0}\nswitchport trunk native vlan none'.format(ifn))
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            self._device.cfg.send_config('interface {0}\nswitchport trunk allowed vlan remove {1}'.format(ifn,vid))
        else:
            raise ValueError('interface {0} cannot be delete from vlan {1}'.format(ifn,vid))

        #self._device.load_config()

    def items(self):
        self._update_vlan()
        return self._vlan.items()

    def __str__(self):
        self._update_vlan()
        return json.dumps(self._vlan)

    __repr__ = __str__

    def __getitem__(self, vid):
        self._update_vlan()
        #print "getitem"
        #print self._vlan
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
        self.load_config(self._device.config)
        l = VlanStatusLexer()
        vlan_cfg = self._device.cmd("show vlan all")
        vlan = l.run(vlan_cfg)
        for vln,vli in vlan.items():
            for vlr,vlc in self._vlan_config.items():
                if int(vln) in self._get_vlan_ids(vlr):
                    vlan[vln] = dict(vlan[vln].items() + vlc.items())
        self._vlan = vlan

    def _get_interface_config(self, ifn):
        ret = {}
        for ifr,ifi in self._interface_config.items():
            m  = re.match('^port(?P<prefix>\d+\.\d+\.)(?P<start_no>\d+)\-\d+\.\d+\.(?P<end_no>\d+)$', ifr)
            if m:
                ifr = ['port{0}{1}'.format(m.group('prefix'),n) for n in range(int(m.group('start_no')),1+int(m.group('end_no')))]
            else:
                ifr = [ifr]

            if ifn in ifr:
               ret = dict(ret.items() + ifi.items())
        return ret 
