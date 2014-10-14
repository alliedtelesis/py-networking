# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class awp_dns(Feature):
    """
    DNS feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._dns = {}
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")
        self._d.log_info(self._dns)


    def create(self, name_servers='', default_domain=''):
        self._d.log_info("add address {0} and domain {0}".format(name_servers, default_domain))
        self._update_dns()

        if name_servers == '' and default_domain == '':
            raise KeyError('at least one parameter is mandatory')
        if name_servers != '' and name_servers in self._dns['name_servers']:
            raise KeyError('DNS server {0} already added'.format(name_servers))
        if default_domain != '' and default_domain in self._dns['default_domain']:
            raise KeyError('default domain {0} already added'.format(default_domain))

        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\(config\)\#'}
                        ]}
        if name_servers != '':
            set_cmd = 'ip name-server {0}'.format(name_servers)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        if default_domain != '':
            set_cmd = 'ip domain-list {0}'.format(default_domain)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        cmds['cmds'].append({'cmd': chr(26) , 'prompt': '\#'})

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_dns()


    def delete(self, name_servers='', default_domain=''):
        self._d.log_info("remove address {0} and domain {0}".format(name_servers, default_domain))
        self._update_dns()

        if name_servers == '' and default_domain == '':
            raise KeyError('at least one parameter is mandatory')
        if name_servers != '' and name_servers not in self._dns['name_servers']:
            raise KeyError('DNS server {0} not configured'.format(name_servers))
        if default_domain != '' and default_domain not in self._dns['default_domain']:
            raise KeyError('default domain {0} not configured'.format(default_domain))

        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\(config\)\#'}
                        ]}
        if name_servers != '':
            set_cmd = 'no ip name-server {0}'.format(name_servers)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        if default_domain != '':
            set_cmd = 'no ip domain-list {0}'.format(default_domain)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        cmds['cmds'].append({'cmd': chr(26) , 'prompt': '\#'})

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_dns()


    def items(self):
        self._update_dns()
        return self._dns.items()


    def keys(self):
        self._update_dns()
        return self._dns.keys()


    def __getitem__(self, id):
        self._update_dns()
        if id not in self._dns.keys():
            raise KeyError('Entry {0} does not exist'.format(id))
        return self._dns[id]


    def _update_dns(self):
        self._d.log_info("_update_dns")
        def_dom = ''
        nam_srv = ''

        # ip domain-list com
        # ip name-server 10.17.39.11
        ifreList = re.compile('ip\s+domain-list\s(?P<domains>(\w+))')
        ifreServ = re.compile('ip\s+name-server\s(?P<names>(\d+\.+\d+\.+\d+\.+\d+))')
        for line in self._device.cmd("show running-config").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifreList.match(line)
            if m:
                if def_dom == '':
                    def_dom = m.group('domains')
                    # else:
                    #     def_dom = def_dom + ',' + m.group('domains')
            m = ifreServ.match(line)
            if m:
                if nam_srv == '':
                    nam_srv = m.group('names')
                else:
                    nam_srv = nam_srv + ',' + m.group('names')

        self._dns = {'name_servers': nam_srv, 'default_domain': def_dom}

        self._d.log_debug("dns {0}".format(pformat(json.dumps(self._dns))))
