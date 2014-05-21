# -*- coding: utf-8 -*-
from pynetworking import Feature
from pynetworking.features.awp_vlan_config_lexer import VlanConfigLexer
from pynetworking.features.awp_vlan_status_lexer import VlanStatusLexer
from pynetworking.features.awp_vlan_config_interface_lexer import VlanInterfaceConfigLexer
from pprint import pformat
import re
import json

class awp_vlan(Feature):
    """
    Vlan feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._vlan_config={}
        self._vlan={}
        self._d = device
        self._d.log_debug("loading feature")

    def load_config(self, config):
        self._d.log_info("loading config")
        l = VlanConfigLexer()
        self._vlan_config = l.run(config)
        l = VlanInterfaceConfigLexer()
        self._interface_config = l.run(config)

    def create(self, vlan_id, **kwargs):
        self._d.log_info("create {0} {1}".format(vlan_id,pformat(kwargs)))
        self._update_vlan()
        cmds = {'cmds':[{'cmd': 'enable',               'prompt':'\#'},
                        {'cmd': 'conf t',               'prompt':'\(config\)\#'},
                        {'cmd': 'vlan database',        'prompt':'\(config-vlan\)\#'},
                       ]}
        vlan_cmd = 'vlan {0}'.format(vlan_id)

        if len(self._get_vlan_ids(vlan_id)) == 1:
            if 'name' in kwargs:
                if ' ' in kwargs['name']:
                    vlan_cmd += ' name "{0}"'.format(kwargs['name'])
                else:
                    vlan_cmd += " name {0}".format(kwargs['name'])
        if 'state' in kwargs:
            if kwargs['state'] == 'enable' or kwargs['state'] == 'disable':
                vlan_cmd += " state {0}".format(kwargs['state'])
            else:
                raise ValueError("{0} is and invalid vlan state".format(kwargs['state'])) 
        
        cmds['cmds'].append({'cmd': vlan_cmd,             'prompt':'\(config-vlan\)\#'})
        if 'mtu' in kwargs:
            cmds['cmds'].append({'cmd': "vlan {0} mtu {1}".format(vlan_id, int(kwargs['mtu'])), 'prompt':'\(config-vlan\)\#'})
        cmds['cmds'].append({'cmd': chr(26),              'prompt':'\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

    def delete(self, vlan_id):
        self._d.log_info("delete {0}".format(vlan_id))
        self._update_vlan()
        self._get_vlan_ids(vlan_id)
        cmds = {'cmds':[{'cmd': 'enable',                     'prompt':'\#'},
                        {'cmd': 'conf t',                     'prompt':'\(config\)\#'},
                        {'cmd': 'vlan database',              'prompt':'\(config-vlan\)\#'},
                        {'cmd': 'no vlan {0}'.format(vlan_id),'prompt':'\(config-vlan\)\#'},
                        {'cmd': chr(26),                      'prompt':'\#'},
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

    def update(self, vlan_id, **kwargs):
        self._d.log_info("update {0} {1}".format(vlan_id,pformat(kwargs)))
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
        self._d.log_info("add_interface {0} ifn={1} tagged={2}".format(vid, ifn, tagged))
        self._update_vlan()
        vid = str(vid)
        if vid not in self._vlan:
            raise ValueError('{0} is not a valid vlan id'.format(vid))

        ifi = self._get_interface_config(ifn)
        if not ifi:    
            raise ValueError('{0} is not a valid interface'.format(ifn))
    
        if 'switchport mode' not in ifi:
            raise ValueError('{0} interface does not support vlan'.format(ifn))

        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\#'},
                        {'cmd': 'conf t',                    'prompt':'\(config\)\#'},
                        {'cmd': 'interface port{0}'.format(ifn), 'prompt':'\(config-if\)\#'},
                       ]}

        if ifi['switchport mode'] == 'access' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport access vlan {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif ifi['switchport mode'] == 'access' and tagged == True:
            ## should copy access vlan to native
            cmds['cmds'].append({'cmd': 'switchport mode trunk'                             ,'prompt':'\(config-if\)\#'})
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport trunk native vlan {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        else:
            raise ValueError('interface {0} cannot be added to vlan {1}'.format(ifn,vid))

        cmds['cmds'].append({'cmd': chr(26),                               'prompt':'\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()


    def delete_interface(self, vid, ifn):
        self._d.log_info("delete_interface {0} ifn={1}".format(vid, ifn))
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
    
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\#'},
                        {'cmd': 'conf t',                    'prompt':'\(config\)\#'},
                        {'cmd': 'interface port{0}'.format(ifn), 'prompt':'\(config-if\)\#'},
                       ]}

        if ifi['switchport mode'] == 'access':
            # this actually move port back to vlan 1
            cmds['cmds'].append({'cmd': 'no switchport access vlan {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport trunk native vlan none' ,'prompt':'\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan remove {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        else:
            raise ValueError('interface {0} cannot be delete from vlan {1}'.format(ifn,vid))

        cmds['cmds'].append({'cmd': chr(26),                               'prompt':'\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

    def items(self):
        self._update_vlan()
        return self._vlan.items()

    def __str__(self):
        self._update_vlan()
        return json.dumps(self._vlan)

    __repr__ = __str__ #pragma: no cover

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
        self._d.log_info("_update_vlan")
        l = VlanStatusLexer()
        vlan_cfg = self._device.cmd("show vlan all")
        vlan = l.run(vlan_cfg)
        for vln,vli in vlan.items():
            for vlr,vlc in self._vlan_config.items():
                if int(vln) in self._get_vlan_ids(vlr):
                    vlan[vln] = dict(vlan[vln].items() + vlc.items())
        self._vlan = vlan
        self._d.log_debug(pformat(json.dumps(self._vlan)))

    def _get_interface_config(self, ifn):
        ret = {}
        for ifr,ifi in self._interface_config.items():
            m  = re.match('^(?P<prefix>\d+\.\d+\.)(?P<start_no>\d+)\-\d+\.\d+\.(?P<end_no>\d+)$', ifr)
            if m:
                ifr = ['{0}{1}'.format(m.group('prefix'),n) for n in range(int(m.group('start_no')),1+int(m.group('end_no')))]
            else:
                ifr = [ifr]

            if ifn in ifr:
               ret = dict(ret.items() + ifi.items())
        return ret 
