# -*- coding: utf-8 -*-
from pynetworking import Feature
from pynetworking.features.ats_vlan_config_lexer import VlanConfigLexer
#from pynetworking.features.awp_vlan_status_lexer import VlanStatusLexer
#from pynetworking.features.awp_vlan_config_interface_lexer import VlanInterfaceConfigLexer
from pprint import pformat
import re
import json

class ats_vlan(Feature):
    """
    Vlan feature implementation for ATS
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
#       l = VlanInterfaceConfigLexer()
#       self._interface_config = l.run(config)
        self._d.log_debug("vlan configuration {0}".format(self._vlan_config))

    def create(self, vlan_id, **kwargs):
        self._d.log_info("create {0} {1}".format(vlan_id,pformat(kwargs)))
        self._update_vlan()
        cmds = {'cmds':[{'cmd': 'enable',               'prompt':'\n\w+\#'},
                        {'cmd': 'conf t',               'prompt':'\n\w+\(config\)\#'},
                        {'cmd': 'vlan database',        'prompt':'\n\w+\(config-vlan\)\#'},
                       ]}
        vlan_cmd = 'vlan {0}'.format(vlan_id)

        if len(self._get_vlan_ids(vlan_id)) == 1:
            if 'name' in kwargs:
                if ' ' in kwargs['name']:
                    vlan_cmd += ' name "{0}"'.format(kwargs['name'])
                else:
                    vlan_cmd += " name {0}".format(kwargs['name'])
        if 'mtu' in kwargs:
            vlan_cmd += " mtu {0}".format(int(kwargs['mtu']))
        if 'state' in kwargs:
            if kwargs['state'] == 'enable' or kwargs['state'] == 'disable':
                vlan_cmd += " state {0}".format(kwargs['state'])
            else:
                raise ValueError("{0} is and invalid vlan state".format(kwargs['state'])) 
        
        cmds['cmds'].append({'cmd': vlan_cmd,'prompt':'\n\w+\(config-vlan\)\#'})
        self._device.cmd(cmds)
        self._device.load_system()

    def delete(self, vlan_id):
        self._d.log_info("delete {0}".format(vlan_id))
        self._update_vlan()
        self._get_vlan_ids(vlan_id)
        cmds = {'cmds':[{'cmd': 'enable',                     'prompt':'\n\w+\#'},
                        {'cmd': 'conf t',                     'prompt':'\n\w+\(config\)\#'},
                        {'cmd': 'vlan database',              'prompt':'\n\w+\(config-vlan\)\#'},
                        {'cmd': 'no vlan {0}'.format(vlan_id),'prompt':'\n\w+\(config-vlan\)\#'},
                       ]}
        self._device.cmd(cmds)
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

        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\n\w+\#'},
                        {'cmd': 'conf t',                    'prompt':'\n\w+\(config\)\#'},
                        {'cmd': 'interface port{0}'.format(ifn), 'prompt':'\n\w+\(config-if\)\#'},
                       ]}

        if ifi['switchport mode'] == 'access' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport access vlan {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        elif ifi['switchport mode'] == 'access' and tagged == True:
            ## should copy access vlan to native
            cmds['cmds'].append({'cmd': 'switchport mode trunk'                             ,'prompt':'\n\w+\(config-if\)\#'})
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport trunk native vlan {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        else:
            raise ValueError('interface {0} cannot be added to vlan {1}'.format(ifn,vid))

        self._device.cmd(cmds)
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
    
        cmds = {'cmds':[{'cmd': 'enable',                    'prompt':'\n\w+\#'},
                        {'cmd': 'conf t',                    'prompt':'\n\w+\(config\)\#'},
                        {'cmd': 'interface port{0}'.format(ifn), 'prompt':'\n\w+\(config-if\)\#'},
                       ]}

        if ifi['switchport mode'] == 'access':
            # this actually move port back to vlan 1
            cmds['cmds'].append({'cmd': 'no switchport access vlan {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport trunk native vlan none' ,'prompt':'\n\w+\(config-if\)\#'})
        elif ifi['switchport mode'] == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan remove {0}'.format(vid) ,'prompt':'\n\w+\(config-if\)\#'})
        else:
            raise ValueError('interface {0} cannot be delete from vlan {1}'.format(ifn,vid))

        self._device.cmd(cmds)
        self._device.load_system()

    def items(self):
        self._update_vlan()
        return self._vlan.items()

    def keys(self):
        self._update_vlan()
        return self._vlan.keys()

    def __str__(self):
        self._update_vlan()
        return json.dumps(self._vlan)

    __repr__ = __str__

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

        cvid = ''
        vlan = {}
        for line in self._device.cmd("show vlan").split('\n'):
            m = re.match('\s?(?P<vid>\d+)\s', line)
            print line
            if m:
                vlan[m.group('vid')] = {'type': line[52:64].strip(), 'ports': line[23:51].strip()}
                if vlan[m.group('vid')]['ports'].endswith(','):
                    cvid = m.group('vid')
            elif cvid != '':
                self._d.log_info(vlan)
                vlan[cvid]['ports'] += line[23:51].strip()
                if not vlan[cvid]['ports'].endswith(','):
                    cvid = ''

        for vln,vli in vlan.items():
            vlan[vln]['ports'] = self._expand_interface_list(vlan[vln]['ports'])
            for vlr,vlc in self._vlan_config.items():
                vlan[vln] = dict(vlan[vln].items() + vlc.items())
        self._vlan = vlan
        self._d.log_debug(pformat(json.dumps(self._vlan)))

    def _expand_interface_list(self, ifranges):
        ret = []
        self._d.log_info("_expand_interface_list {0}".format(ifranges))
        if ifranges == '':
            return ret

        m = re.search('{0}/e(?P<single>\d+)'.format(self._d.facts['unit_number']), ifranges)
        if m:
            ret = '{0}.0.{1}'.format(self._d.facts['unit_number'], m.group('single'))
        else:
            m = re.search('{0}/e\((?P<ranges>[^\)]+)'.format(self._d.facts['unit_number']), ifranges)
            if m:
                for r in m.group('ranges').split(','):
                    m = re.match('(?P<start_no>\d+)\-(?P<end_no>\d+)', r)
                    if m:
                        end_no = int(m.group('end_no'))
                        start_no = int(m.group('start_no'))
                        if self._d.facts['model'] == 'AT-8000S/24' and start_no > 24:
                            continue
                        if self._d.facts['model'] == 'AT-8000S/24' and end_no > 24:
                             end_no = 24
                        ret += ['{0}.0.{1}'.format(self._d.facts['unit_number'],n) for n in range(start_no,1+end_no)]
                    else:
                        r = int(r)
                        if self._d.facts['model'] == 'AT-8000S/24' and r > 24:
                            continue
                        ret.append('{0}.0.{1}'.format(self._d.facts['unit_number'],r))

        m = re.search('{0}/g(?P<single>\d+)'.format(self._d.facts['unit_number']), ifranges)
        if m:
            ret = '{0}.0.{1}'.format(self._d.facts['unit_number'], m.group('single'))
        else:
            m = re.search('{0}/g\((?P<ranges>[^\)]+)'.format(self._d.facts['unit_number']), ifranges)
            if m:
                for r in m.group('ranges').split(','):
                    m = re.match('(?P<start_no>\d+)\-(?P<end_no>\d+)', r)
                    if m:
                        start_no = int(m.group('start_no'))
                        end_no = int(m.group('end_no'))
                        if self._d.facts['model'] == 'AT-8000S/24' and start_no > 2:
                            continue
                        if self._d.facts['model'] == 'AT-8000S/24' and end_no > 2:
                             end_no = 2

                        if self._d.facts['model'] == 'AT-8000S/24':
                            start_no += 24
                            end_no += 24
                        else:
                            start_no += 48
                            end_no += 48
                        ret += ['{0}.0.{1}'.format(self._d.facts['unit_number'],n) for n in range(start_no,1+end_no)]
                    else:
                        r = int(r)
                        if self._d.facts['model'] == 'AT-8000S/24' and r > 2:
                            continue
                        if self._d.facts['model'] == 'AT-8000S/24':
                            r += 24
                        else:
                            r += 48
                        ret.append('{0}.0.{1}'.format(self._d.facts['unit_number'],r))

        self._d.log_info("_expand_interface_list return {0}".format(ret))
        return ret
