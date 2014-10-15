# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_ntp(Feature):
    """
    ntp feature implementation for ATS (note that ATS uses SNTP protocol)
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._sntp = {}
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")
        self._sntp = OrderedDict()

        # clock source sntp
        # sntp unicast client enable
        # sntp server 193.204.114.233
        ifre = re.compile('sntp\s+server\s+(?P<address>[^\n]+)')

        for line in config.split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = m.group('address')
                self._sntp[key] = {'polltime': 60,
                                   'status'  : 'Unknown'
                                  }
        self._d.log_info(self._sntp)


    def create(self, address, poll=60):
        self._d.log_info("add SNTP server {0}".format(address))
        self._update_sntp()

        if address in self._sntp.keys():
            raise KeyError('SNTP server {0} already added'.format(address))

        set_cmd = 'sntp server {0}'.format(address)
        poll_cmd = 'sntp client poll timer {0}'.format(poll)
        source_cmd = 'clock source sntp'
        enable_cmd = 'sntp unicast client enable'
        cmds = {'cmds': [{'cmd': 'conf'    , 'prompt': '\(config\)\#'},
                         {'cmd': set_cmd   , 'prompt': '\(config\)\#'},
                         {'cmd': poll_cmd  , 'prompt': '\(config\)\#'},
                         {'cmd': source_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': enable_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': chr(26)   , 'prompt': '\#'}
                        ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_sntp()


    def update(self, address, poll=60):
        self._d.log_info("add SNTP server {0}".format(address))
        self._update_sntp()

        if address not in self._sntp.keys():
            raise KeyError('SNTP server {0} not present'.format(address))

        poll_cmd = 'sntp client poll timer {0}'.format(poll)
        cmds = {'cmds': [{'cmd': 'conf'  , 'prompt': '\(config\)\#'},
                         {'cmd': poll_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': chr(26) , 'prompt': '\#'}
                        ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_sntp()


    def delete(self, address=''):
        self._d.log_info("remove SNTP server {0}".format(address))
        self._update_sntp()

        if address != '' and address not in self._sntp.keys():
            raise KeyError('SNTP server {0} not present'.format(address))

        cmds = {'cmds': [{'cmd': 'conf', 'prompt': '\(config\)\#'}]}

        if address == '':
            sntp_list = self._sntp.keys()
            for i in range(len(sntp_list)):
                del_cmd = 'no sntp server {0}'.format(sntp_list[i])
                cmds['cmds'].append({'cmd': del_cmd, 'prompt': '\(config\)\#'})
        else:
            del_cmd = 'no sntp server {0}'.format(address)
            cmds['cmds'].append({'cmd': del_cmd, 'prompt': '\(config\)\#'})

        cmds['cmds'].append({'cmd': chr(26), 'prompt': '\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_sntp()

        if self._sntp.keys() == []:
            cmds = {'cmds': [{'cmd': 'conf'   , 'prompt': '\(config\)\#'},
                             {'cmd': 'no c so', 'prompt': '\(config\)\#'},
                             {'cmd': chr(26)  , 'prompt': '\#'}
                            ]}
            self._device.cmd(cmds, cache=False, flush_cache=True)


    def items(self):
        self._update_sntp()
        return self._sntp.items()


    def keys(self):
        self._update_sntp()
        return self._sntp.keys()


    def __getitem__(self, address):
        self._update_sntp()
        if address not in self._sntp.keys():
            raise KeyError('SNTP server {0} does not exist'.format(address))
        return self._sntp[address]


    def _update_sntp(self):
        self._d.log_info("_update_sntp")
        self._sntp = OrderedDict()

        # Polling interval: 60 seconds.
        # No MD5 authentication keys.
        # Authentication is not required for synchronization.
        # No trusted keys.
        #
        # Unicast Clients: Enabled
        # Unicast Clients Polling: Enabled
        #
        #            Server              Polling   Encryption Key
        # ----------------------------- ---------- --------------
        #        193.204.114.233         Enabled      Disabled
        #
        # Broadcast Clients: disabled
        # Anycast Clients: disabled
        # No Broadcast Interfaces.
        polltime = 60
        ifre1 = re.compile('(\r|'')Polling\s+interval:\s+(?P<polltime>\d+)\s+seconds.')
        for line in self._device.cmd("show sntp config").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre1.match(line)
            if m:
                polltime = m.group('polltime')
                break

        # Clock is synchronized, stratum 1, reference is 193.204.114.233, unicast
        # Reference time is d7d4ebeb.a56f54e 08:44:27.0 UTC Sep 30 2014
        #
        # Unicast servers:
        #
        #     Server       Status      Last Response     Offset   Delay
        #                                                [mSec]   [mSec]
        # --------------- --------- ------------------- --------- -------
        #  83.64.124.251     up     08:44:27.0 UTC Sep  252398668    0
        #                           30 2014             689
        # 193.204.114.233    up     08:44:27.0 UTC Sep  252398668    0
        #                           30 2014             629
        #........
        ifre2 = re.compile('(\s+|'')(?P<address>[^\s]+)\s+(?P<status>[^\s]+)\s+')
        for line in self._device.cmd("show sntp status").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre2.match(line)
            if m and '.' in m.group('address'):
                key = m.group('address')
                self._sntp[key] = {'polltime': polltime,
                                   'status': m.group('status')
                                  }

        self._d.log_debug("ntp {0}".format(pformat(json.dumps(self._sntp))))
