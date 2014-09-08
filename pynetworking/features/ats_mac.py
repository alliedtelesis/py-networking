# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_mac(Feature):
    """
    mac feature implementation for ATS
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._mac={}
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")
        self._mac = OrderedDict()

        #   1       00:00:cd:24:04:8b    1/e1   dynamic
        ifre = re.compile('\s+(?P<vlan>\d+)\s+'
                          '(?P<mac>[^\s]+)\s+'
                          '(?P<interface>[^\s]+)\s+'
                          '(?P<type>[^\s]+)')

        for line in config.split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = self._get_dotted_mac(m.group('mac'))
                self._mac[key] = {'vlan': m.group('vlan'),
                                  'interface': m.group('interface'),
                                  'action': 'forward',
                                  'type': m.group('type')
                                 }
        self._d.log_info(self._mac)


    def create(self, mac, interface, forward=True, vlan=1):
        self._d.log_info("create MAC address {0} entry".format(mac))
        self._update_mac()

        mac = self._get_dotted_mac(mac)
        if mac in self._d.mac.keys():
            raise KeyError('MAC address {0} is already existing'.format(mac))
        if forward == False:
            raise KeyError('Discard option not supported')

        vlan_cmd = 'interface vlan {0}'.format(vlan)
        set_cmd = 'bridge address {0} ethernet {1} permanent'.format(mac, interface)
        cmds = {'cmds':[{'cmd': 'conf'  , 'prompt':'\(config\)\#'},
                        {'cmd': vlan_cmd, 'prompt':'\(config-if\)\#'},
                        {'cmd': set_cmd , 'prompt':'\(config-if\)\#'},
                        {'cmd': chr(26) , 'prompt':'\#'},
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_mac()


    def update(self, mac, interface, forward=True, vlan=1):
        self._d.log_info("update MAC address {0} entry".format(mac))
        self._update_mac()

        mac = self._get_dotted_mac(mac)
        if mac not in self._d.mac.keys():
            raise KeyError('MAC address {0} is not existing'.format(mac))
        if forward == False:
            raise KeyError('Discard option not supported')

        vlan_cmd = 'interface vlan {0}'.format(vlan)
        set_cmd = 'bridge address {0} ethernet {1} permanent'.format(mac, interface)
        cmds = {'cmds':[{'cmd': 'conf'  , 'prompt':'\(config\)\#'},
                        {'cmd': vlan_cmd, 'prompt':'\(config-if\)\#'},
                        {'cmd': set_cmd , 'prompt':'\(config-if\)\#'},
                        {'cmd': chr(26) , 'prompt':'\#'},
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_mac()


    def delete(self, mac=''):
        self._update_mac()

        if (mac == ''):
            # In spite the dynamic entries are removed, the device will learn them again.
            # Indeed the MAC address table is left empty for a very short time.
            self._d.log_info("remove all the dynamic entries")
            del_cmd = 'clear bridge'
            cmds = {'cmds':[{'cmd': del_cmd , 'prompt':'\#'}]}
            self._device.cmd(cmds, cache=False, flush_cache=True)

            # The static entries have to be removed one by one, given that there is no global command.
            self._d.log_info("remove all the static entries")
            cmds = {'cmds':[{'cmd': 'conf'  , 'prompt':'\(config\)\#'}]}
            keys = self._mac.keys()
            for key in keys:
                mac_item = self._mac[key]
                if mac_item['type'] == 'static':
                    vlan_cmd = 'interface vlan {0}'.format(mac_item['vlan'])
                    del_cmd = 'no bridge address {0}'.format(key)
                    cmds['cmds'].append({'cmd': vlan_cmd, 'prompt':'\(config-if\)\#'})
                    cmds['cmds'].append({'cmd': del_cmd , 'prompt':'\(config-if\)\#'})
            cmds['cmds'].append({'cmd': chr(26) , 'prompt':'\#'})
            self._device.cmd(cmds, cache=False, flush_cache=True)
        else:
            self._d.log_info("remove {0}".format(mac))
            mac = self._get_dotted_mac(mac)
            if mac not in self._d.mac.keys():
                raise KeyError('mac {0} is not existing'.format(mac))
            if self._d.mac[mac]['type'] == 'dynamic':
                raise KeyError('cannot remove a dynamic entry')
            vlan = self._d.mac[mac]['vlan']
            vlan_cmd = 'interface vlan {0}'.format(vlan)
            del_cmd = 'no bridge address {0}'.format(mac)
            cmds = {'cmds':[{'cmd': 'conf'  , 'prompt':'\(config\)\#'},
                            {'cmd': vlan_cmd, 'prompt':'\(config-if\)\#'},
                            {'cmd': del_cmd , 'prompt':'\(config-if\)\#'},
                            {'cmd': chr(26) , 'prompt':'\#'},
                           ]}
            self._device.cmd(cmds, cache=False, flush_cache=True)

        self._update_mac()


    def items(self):
        self._update_mac()
        return self._mac.items()


    def keys(self):
        self._update_mac()
        return self._mac.keys()


    def __getitem__(self, mac):
        self._update_mac()
        dotted_mac = self._get_dotted_mac(mac)
        if dotted_mac not in self._mac.keys():
            raise KeyError('MAC address {0} does not exist'.format(mac))
        return self._mac[dotted_mac]


    def _get_dotted_mac(self, mac):
        if (re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()) or
            re.match("[0-9a-f]{4}([.])[0-9a-f]{4}([.])[0-9a-f]{4}", mac.lower())  or
            re.match("[0-9a-f]{12}", mac.lower())):
            mac = mac.replace('-', '')
            mac = mac.replace(':', '')
            mac = mac.replace('.', '')
            mac = mac[0:4] + '.' + mac[4:8] + '.' + mac[8:12]
        else:
            raise KeyError('MAC address {0} is not valid'.format(mac))
        return mac


    def _update_mac(self):
        self._d.log_info("_update_mac")
        self._mac = OrderedDict()

        #   1       00:00:cd:24:04:8b    1/e1   dynamic
        ifre = re.compile('\s+(?P<vlan>\d+)\s+'
                          '(?P<mac>[^\s]+)\s+'
                          '(?P<interface>[^\s]+)\s+'
                          '(?P<type>[^\s]+)')
        for line in self._device.cmd("show bridge address-table").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = self._get_dotted_mac(m.group('mac'))
                self._mac[key] = {'vlan': m.group('vlan'),
                                  'interface': m.group('interface'),
                                  'action': 'forward',
                                  'type': m.group('type')
                                 }
        self._d.log_debug("mac {0}".format(pformat(json.dumps(self._mac))))


    def _check_static_entry_presence(self):
        self._d.log_info("_check_static_entry_presence")

        keys = self._d.mac.keys()
        for key in keys:
            if self._d.mac[key]['type'] == 'static':
                return True

        return False
