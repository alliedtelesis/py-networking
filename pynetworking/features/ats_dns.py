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
        self._d.log_info("add address {0} and domain {1}".format(name_servers, default_domain))
        self._update_dns()
        name_list = []

        if name_servers == '' and default_domain == '':
            raise KeyError('at least one parameter is mandatory')
        if default_domain != '' and default_domain in self._dns['default_domain']:
            raise KeyError('default domain {0} already added'.format(default_domain))
        if name_servers != '':
            if (type(name_servers) == str):
                name_list = [name_servers]
            else:
                name_list = name_servers
            for i in range(len(name_list)):
                if name_list[i] in self._dns['name_servers']:
                    raise KeyError('DNS server {0} already added'.format(name_list[i]))

        cmds = {'cmds': [{'cmd': 'conf', 'prompt': '\(config\)\#'}]}
        for i in range(len(name_list)):
            set_cmd = 'ip name-server {0}'.format(name_list[i])
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        if default_domain != '':
            set_cmd = 'ip domain-name {0}'.format(default_domain)
            cmds['cmds'].append({'cmd': set_cmd ,'prompt':'\(config\)\#'})
        cmds['cmds'].append({'cmd': chr(26) , 'prompt': '\#'})

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_dns()


    def read(self, hostname, wait_time=20000):
        if hostname == '':
            raise KeyError('hostname parameter is mandatory')
        ping_cmd = 'ping {0}'.format(hostname)

        # Pinging ntp.inrim.it. (193.204.114.105) with 56 bytes of data:
        regex = '(\r|'')Pinging\s{0}\.\s\((?P<ip>(\d+\.+\d+\.+\d+\.+\d+))\)'.format(hostname)
        ifre = re.compile(regex)
        cmds = {'cmds': [{'cmd': ping_cmd, 'prompt': '\#', 'timeout': wait_time}]}
        output = self._device.cmd(cmds, cache=False, flush_cache=True)
        for line in output.split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                ret = m.group('ip')
                return ret


    def delete(self, name_servers='', default_domain=''):
        self._d.log_info("remove address {0} and domain {1}".format(name_servers, default_domain))
        self._update_dns()
        name_list = []

        if name_servers == '' and default_domain == '':
            raise KeyError('at least one parameter is mandatory')
        if default_domain != '' and default_domain not in self._dns['default_domain']:
            raise KeyError('default domain {0} not configured'.format(default_domain))
        if name_servers != '':
            if (type(name_servers) == str):
                name_list = [name_servers]
            else:
                name_list = name_servers
            for i in range(len(name_list)):
                if name_list[i] not in self._dns['name_servers']:
                    raise KeyError('DNS server {0} already deleted'.format(name_list[i]))

        cmds = {'cmds': [{'cmd': 'conf', 'prompt': '\(config\)\#'}]}
        for i in range(len(name_list)):
            set_cmd = 'no ip name-server {0}'.format(name_list[i])
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
        self._dns = {}
        def_dom = ''
        nam_srv = ''

        #ip domain-name com
        #ip name-server  10.17.39.11 10.16.48.11
        ifreDomain = re.compile('ip\s+domain-name\s+(?P<dom>\w+)')
        ifreList = re.compile('ip\s+name-server\s(?P<servers>(\s\d+\.+\d+\.+\d+\.+\d+){1,8})')
        for line in self._device.cmd("show running-config").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifreDomain.match(line)
            if m:
                def_dom = m.group('dom')
            m = ifreList.match(line)
            if m:
                cfg_srv = m.group('servers')
                for name in cfg_srv.split(' '):
                    if nam_srv == '':
                        nam_srv = name
                    else:
                        nam_srv = nam_srv + ',' + name

        self._dns = {'name_servers': nam_srv, 'default_domain': def_dom}

        self._d.log_debug("dns {0}".format(pformat(json.dumps(self._dns))))
