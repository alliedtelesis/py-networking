# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_dns(Feature):
    """
    DNS feature implementation for ATS
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
        if name_servers != '' and name_servers in self._dns.keys():
            raise KeyError('DNS server {0} already added'.format(name_servers))
        if default_domain != '' and default_domain in self._dns.keys():
            raise KeyError('default domain {0} already added'.format(default_domain))

        cmds = {'cmds': [{'cmd': 'conf', 'prompt': '\(config\)\#'}]}
        if name_servers != '':
            set_cmd = 'ip name-server {0}'.format(name_servers)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        if default_domain != '':
            set_cmd = 'ip domain-name {0}'.format(default_domain)
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
            raise KeyError('domain {0} not configured'.format(default_domain))

        cmds = {'cmds': [{'cmd': 'conf', 'prompt': '\(config\)\#'}]}
        if name_servers != '':
            set_cmd = 'no ip name-server {0}'.format(name_servers)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        if default_domain != '':
            set_cmd = 'no ip domain-name'
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


    def __getitem__(self, address):
        self._update_dns()
        if address not in self._dns.keys():
            raise KeyError('Entry {0} does not exist'.format(address))
        return self._dns[address]


    def _update_dns(self):
        self._d.log_info("_update_dns")
        self._dns = OrderedDict()

        # System Name:  nac_dev
        # Default domain:  net
        #
        #
        # Name/address lookup is enable
        #
        #
        # Name servers (Preference order): 10.17.39.11 10.16.48.11
        #.................
        #
        ifreDomain = re.compile('Default\s+domain:\s+(?P<dom>\w+)')
        ifreList = re.compile('Name\s+servers\s+\(Preference\s+order\):(?P<servers>(\s\d+\.+\d+\.+\d+\.+\d+){1,8})')
        for line in self._device.cmd("show hosts").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifreDomain.match(line)
            if m:
                self._dns[m.group('dom')] = {'static': False}
            m = ifreList.match(line)
            if m:
                ll = m.group('servers')
                self._d.log_debug("servers are {0}".format(ll))
                for name in ll.split(' '):
                    if name != '':
                        self._dns[name] = {'static': False}

        #ip domain-name com
        #ip name-server 10.17.39.11 10.16.48.11
        ifreDomain = re.compile('ip\s+domain-name\s+(?P<dom>\w+)')
        ifreList = re.compile('ip\s+name-server(?P<servers>(\s+\d+\.+\d+\.+\d+\.+\d+){1,8})')
        for line in self._device.cmd("show running-config").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifreDomain.match(line)
            if m:
                cfg_dom = m.group('dom')
                for i in self._dns.keys():
                    if i == cfg_dom:
                        self._dns[i]['static'] = True
                        break
            m = ifreList.match(line)
            if m:
                cfg_srv = m.group('servers')
                for name in cfg_srv.split(' '):
                    if name != '':
                        for i in self._dns.keys():
                            if i == name:
                                self._dns[i]['static'] = True
                                break

        self._d.log_debug("dns {0}".format(pformat(json.dumps(self._dns))))
