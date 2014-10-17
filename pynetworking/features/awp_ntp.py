# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
from time import sleep
import re
import json
try:
    from collections import OrderedDict
except ImportError:  # pragma: no cover
    from ordereddict import OrderedDict


class awp_ntp(Feature):
    """
    ntp feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._ntp = {}
        self._d = device
        self._d.log_debug("loading feature")

    def load_config(self, config):
        self._d.log_info("loading config")
        self._ntp = OrderedDict()

        # ntp peer ntp.inrim.it
        ifre = re.compile('ntp\s+peer\s+(?P<address>[^\s]+)')

        for line in config.split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                key = m.group('address')
                self._ntp[key] = {'polltime': 64,
                                  'status': False
                                  }
        self._d.log_info(self._ntp)

    def create(self, address):
        self._d.log_info("add NTP server {0}".format(address))
        self._update_ntp()

        if address in self._ntp.keys():
            raise KeyError('NTP server {0} already added'.format(address))

        set_cmd = 'ntp peer {0}'.format(address)
        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\(config\)\#'},
                         {'cmd': set_cmd, 'prompt': '\(config\)\#'},
                         {'cmd': chr(26), 'prompt': '\#'}
                         ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        sleep(1)
        self._update_ntp()

    def delete(self, address=''):
        self._d.log_info("remove NTP server {0}".format(address))
        self._update_ntp()

        if address != '' and address not in self._ntp.keys():
            raise KeyError('NTP server {0} is not present'.format(address))

        cmds = {'cmds': [{'cmd': 'enable', 'prompt': '\#'},
                         {'cmd': 'conf t', 'prompt': '\(config\)\#'}
                         ]}

        if address == '':
            ntp_list = self._ntp.keys()
            for i in range(len(ntp_list)):
                del_cmd = 'no ntp peer {0}'.format(ntp_list[i])
                cmds['cmds'].append({'cmd': del_cmd, 'prompt': '\(config\)\#'})
        else:
            del_cmd = 'no ntp peer {0}'.format(address)
            cmds['cmds'].append({'cmd': del_cmd, 'prompt': '\(config\)\#'})

        cmds['cmds'].append({'cmd': chr(26), 'prompt': '\#'})
        self._device.cmd(cmds, cache=False, flush_cache=True)
        sleep(1)
        self._update_ntp()

    def items(self):
        self._update_ntp()
        return self._ntp.items()

    def keys(self):
        self._update_ntp()
        return self._ntp.keys()

    def __getitem__(self, address):
        self._update_ntp()
        if address not in self._ntp.keys():
            raise KeyError('NTP server {0} is not present'.format(address))
        return self._ntp[address]

    def _update_ntp(self):
        self._d.log_info("_update_ntp")
        self._ntp = OrderedDict()

        # awplus#show ntp status
        # Clock is synchronized, stratum 2, reference is 193.204.114.233
        # actual frequency is 0.0000 PPM, precision is 2**-16
        # reference time is d7ceaad8.b79b55c1 (16:53:12.717 CET Thu Sep 25 2014)
        # clock offset is 9.382 msec, root delay is 21.749 msec
        # root dispersion is 7947.402 msec

        # awplus#show ntp associations
        #   address          ref clock       st  when  poll reach   delay  offset    disp
        # *~193.204.114.233  CTD              1     2    64   001    21.8    11.2  7937.5
        # -~193.204.114.105  CTD              1    39    64   077    20.2    20.7     4.3
        #  ~193.204.114.106  INIT            16     -    64   000     0.0     0.0 15937.5
        #  * master (synced), # master (unsynced), + selected, - candidate, ~ configured
        ifre = re.compile('(\s+|\*+|\-+)~+(?P<address>[^\s]+)\s+'
                          '\s+(?P<refclock>[^\s]+)\s+'
                          '\s+(?P<st>\d+)\s+'
                          '\s+(?P<when>[^\s]+)\s+'
                          '\s+(?P<polltime>\d+)')
        for line in self._device.cmd("show ntp associations").split('\n'):
            self._d.log_debug("line is {0}".format(line))
            m = ifre.match(line)
            if m:
                status = False
                if (line[0] == '*'):
                    status = True
                key = m.group('address')
                self._ntp[key] = {'polltime': m.group('polltime'),
                                  'status': status
                                  }
        self._d.log_debug("ntp {0}".format(pformat(json.dumps(self._ntp))))
