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

        if name_servers == '' and domain == '':
            raise KeyError('at least one parameter is mandatory')
        if name_servers != '' and name_servers in self._dns.keys():
            raise KeyError('DNS server {0} already added'.format(name_servers))
        if default_domain != '' and default_domain in self._dns.keys():
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
        if name_servers != '' and name_servers not in self._dns.keys():
            raise KeyError('DNS server {0} not configured'.format(name_servers))
        if default_domain != '' and default_domain not in self._dns.keys():
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


    def __getitem__(self, domain):
        self._update_dns()
        if domain not in self._dns.keys():
            raise KeyError('Entry {0} does not exist'.format(domain))
        return self._dns[domain]


    def _update_dns(self):
        self._d.log_info("_update_dns")
        self._dns = {}

        # Default domain is .org
        # Domain list: .net .it
        # Name/address lookup uses domain service
        # Name servers are
        # 10.17.39.11
        # 10.16.48.11
        ifreList = re.compile('Domain\s+list:(?P<domains>(\s\w+){1,8})')
        ifreServ = re.compile('\d+\.+\d+\.+\d+\.+\d')
        for line in self._device.cmd("show hosts").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifreList.match(line)
            if m:
                ll = m.group('domains')
                if self._dns[default_domain] == '':
                    self._dns[default_domain] = ll
                for token in ll.split(' '):
                    self._dns[default_domain] = self._dns[default_domain] + ',' + token
            m = ifreServ.match(line)
            if m:
                line = line.replace('\n', '')
                line = line.replace('\r', '')
                if self._dns[name_servers] == '':
                    self._dns[name_servers] = line.split(' ')[0]
                for token in line.split(' '):
                    self._dns[name_servers] = self._dns[name_servers] + ',' + token

        self._d.log_debug("dns {0}".format(pformat(json.dumps(self._dns))))
