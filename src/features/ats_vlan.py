# -*- coding: utf-8 -*-
from pynetworking import Feature
from pynetworking.features.ats_vlan_config_lexer import VlanConfigLexer
from pynetworking.features.ats_vlan_config_interface_lexer import VlanInterfaceConfigLexer
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
        self._d.log_debug("vlan configuration {0}".format(self._vlan_config))
        l = VlanInterfaceConfigLexer()
        self._interface_config = {}
        for ifr, ifc in l.run(config).items():
            for ifn in self._expand_interface_list(ifr):
                self._interface_config[ifn] = ifc
        self._d.log_info("vlan interface configuration {0}".format(self._interface_config))

    def create(self, vlan_id, **kwargs):
        self._d.log_info("create {0} {1}".format(vlan_id,pformat(kwargs)))
        self._update_vlan()
        cmds = {'cmds':[{'cmd': 'conf',                 'prompt':'\(config\)\#'},
                        {'cmd': 'vlan database',        'prompt':'\(config-vlan\)\#'},
                       ]}
        vlan_cmd = 'vlan {0}'.format(vlan_id)

        cmds['cmds'].append({'cmd': vlan_cmd,            'prompt':'\(config-vlan\)\#'})
        cmds['cmds'].append({'cmd': chr(26),             'prompt':'\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

        if len(self._get_vlan_ids(vlan_id)) == 1:
            if 'name' in kwargs:
                self.update(vlan_id,**kwargs)

    def delete(self, vlan_id):
        self._d.log_info("delete {0}".format(vlan_id))
        self._update_vlan()
        self._get_vlan_ids(vlan_id)
        cmds = {'cmds':[{'cmd': 'conf',                       'prompt':'\(config\)\#'},
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
            if 'name' in kwargs:
                cmds = {'cmds':[{'cmd': 'conf',                              'prompt':'\(config\)\#'},
                                {'cmd': 'interface vlan {0}'.format(vlan_id),'prompt':'\(config-if\)\#'},
                                ]}
                if ' ' in kwargs['name']:
                    vlan_cmd = 'name "{0}"'.format(kwargs['name'])
                else:
                    vlan_cmd = "name {0}".format(kwargs['name'])
                cmds['cmds'].append({'cmd': vlan_cmd,            'prompt':'\(config-if\)\#'})
                cmds['cmds'].append({'cmd': chr(26),             'prompt':'\#'})
                self._device.cmd(cmds, cache=False, flush_cache=True)
                self._device.load_system()
        else:
            raise KeyError('{0} vlans do not exist'.format(non_existing_ids))

    def add_interface(self, vid, ifn, tagged=False):
        self._d.log_info("add_interface {0} ifn={1} tagged={2}".format(vid, ifn, tagged))
        self._update_vlan()
        vid = str(vid)
        if vid not in self._vlan:
            raise ValueError('{0} is not a valid vlan id'.format(vid))

        if ifn in self._interface_config:
            mode = self._interface_config[ifn].get('switchport mode', 'access')
        else:
            mode = 'access'

        cmds = {'cmds':[{'cmd': 'conf',                                                                'prompt':'\(config\)\#'},
                        {'cmd': 'interface ethernet {0}'.format(self._d.interface._to_ifn_native(ifn)),'prompt':'\(config-if\)\#'},
                       ]}

        if mode == 'access' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport access vlan {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif mode == 'access' and tagged == True:
            ## should copy access vlan to native
            cmds['cmds'].append({'cmd': 'switchport mode trunk'                             ,'prompt':'\(config-if\)\#'})
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif mode == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'switchport trunk native vlan {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        elif mode == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan add {0}'.format(vid) ,'prompt':'\(config-if\)\#'})

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
        elif 'untagged' in self._vlan[vid] and ifn in self._vlan[vid]['untagged']:
                tagged = False
        else:
            raise ValueError('interface {0} does not belong to vlan {1}'.format(ifn,vid))

        if ifn in self._interface_config:
            mode = self._interface_config[ifn].get('switchport mode', 'access')
        else:
            mode = 'access'
    

        cmds = {'cmds':[{'cmd': 'conf',                                                                'prompt':'\(config\)\#'},
                        {'cmd': 'interface ethernet {0}'.format(self._d.interface._to_ifn_native(ifn)),'prompt':'\(config-if\)\#'},
                       ]}

        if mode == 'access' and vid != '1':
            # this actually move port back to vlan 1
            cmds['cmds'].append({'cmd': 'no switchport access vlan','prompt':'\(config-if\)\#'})
        elif mode == 'trunk' and tagged == False:
            cmds['cmds'].append({'cmd': 'no switchport trunk native vlan' ,'prompt':'\(config-if\)\#'})
        elif mode == 'trunk' and tagged == True:
            cmds['cmds'].append({'cmd': 'switchport trunk allowed vlan remove {0}'.format(vid) ,'prompt':'\(config-if\)\#'})
        else:
            raise ValueError('interface {0} cannot be delete from vlan {1}'.format(ifn,vid))

        cmds['cmds'].append({'cmd': chr(26),                               'prompt':'\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
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

    __repr__ = __str__  #pragma: no cover

    def __getitem__(self, vid):
        if isinstance(vid, str) or isinstance(vid, int) or isinstance(vid, unicode):
            self._update_vlan()
            vid = str(vid)
            if vid in self._vlan:
                return self._vlan[vid]
            raise KeyError('vlan id {0} does not exist'.format(vid))
        else:
            raise TypeError, "Invalid argument type."

    def __iter__(self):
        self._update_vlan()
        for vlan in self._vlan:
            yield vlan

    def _get_vlan_ids(self, vlan_id):
        vlan_id = str(vlan_id)
        vlan_ids = []
        for r in vlan_id.split(','):
            m = re.search('^(?P<start>\d+)\-(?P<end>\d+)$',r)
            if m:
                vlan_ids.extend(range(int(m.group('start')),int(m.group('end'))+1))
                continue
            m  = re.match('\s*(?P<id>\d+)\s*',r)
            if m:
                vlan_ids.append(int(m.group('id')))
                continue
            raise ValueError('{0} is not a valid vlan id, range or list'.format(vlan_id))
        return vlan_ids

    def _update_vlan(self):
        self._d.log_info("_update_vlan")

        cvid = ''
        vlan = {}
        for line in self._device.cmd("show vlan").split('\n'):
            m = re.match('\s?(?P<vid>\d+)\s', line)
            if m:
                vlan[m.group('vid')] = {'type': line[52:64].strip(), 'ports': line[23:51].strip()}
                if vlan[m.group('vid')]['ports'].endswith(','):
                    cvid = m.group('vid')
            elif cvid != '':
                self._d.log_debug(vlan)
                vlan[cvid]['ports'] += line[23:51].strip()
                if not vlan[cvid]['ports'].endswith(','):
                    cvid = ''

        for vln,vli in vlan.items():
            vlan[vln]['tagged'] = []
            vlan[vln]['untagged'] = []
            if vln == '1':
                vlan[vln]['untagged'] = self._expand_interface_list(vlan[vln]['ports'])
            else:
                for ifn in self._expand_interface_list(vlan[vln]['ports']):
                    if ifn in self._interface_config:
                        mode = self._interface_config[ifn].get('switchport mode', 'access')
                        if mode == 'trunk':
                            if 'switchport trunk native' in self._interface_config[ifn] and self._interface_config[ifn]['switchport trunk native'] == vln:
                                vlan[vln]['untagged'].append(ifn)
                            elif 'switchport trunk allowed' in self._interface_config[ifn] and vln in self._interface_config[ifn]['switchport trunk allowed']:
                                vlan[vln]['tagged'].append(ifn)
                        elif 'switchport access' in self._interface_config[ifn] and self._interface_config[ifn]['switchport access'] == vln:
                            vlan[vln]['untagged'].append(ifn)
                    else:
                        vlan[vln]['untagged'].append(ifn)
            del vlan[vln]['ports']
            for vlr,vlc in self._vlan_config.items():
                vlan[vln] = dict(vlan[vln].items() + self._vlan_config[vln].items())
        self._vlan = vlan
        self._d.log_debug(pformat(json.dumps(self._vlan)))

    def _expand_interface_list(self, ifranges):
        ret = []
        self._d.log_info("_expand_interface_list {0}".format(ifranges))
        if ifranges == '':
            return ret

        m = re.search('{0}/e(?P<single>\d+)'.format(self._d.facts['unit_number']), ifranges)
        if m:
            ret.append('{0}.0.{1}'.format(self._d.facts['unit_number'], m.group('single')))
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
            r = int(m.group('single'))
            if r <= 2:
                if self._d.facts['model'] == 'AT-8000S/24':
                    r += 24
                else:
                    r += 48
                ret.append('{0}.0.{1}'.format(self._d.facts['unit_number'], r))
        else:
            m = re.search('{0}/g\((?P<ranges>[^\)]+)'.format(self._d.facts['unit_number']), ifranges)
            if m:
                for r in m.group('ranges').split(','):
                    m = re.match('(?P<start_no>\d+)\-(?P<end_no>\d+)', r)
                    if m:
                        start_no = int(m.group('start_no'))
                        end_no = int(m.group('end_no'))
                        if start_no > 2:
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
                        if r > 2:
                            continue
                        if self._d.facts['model'] == 'AT-8000S/24':
                            r += 24
                        else:
                            r += 48
                        ret.append('{0}.0.{1}'.format(self._d.facts['unit_number'],r))

        self._d.log_debug("_expand_interface_list return {0}".format(ret))
        return ret
