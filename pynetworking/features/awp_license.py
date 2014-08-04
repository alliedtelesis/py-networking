# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class awp_license(Feature):
    """
    Software licensing feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._d = device


    def set_license(self, label='', key='', certificate=''):
        self._d.log_info("set license")
        self._update_license()

        if not ((label == '' and key == '' and certificate != "") or (label != '' and key != '' and certificate == "")):
            raise KeyError('Either label and key or certificate must be given')

        set_cmd = 'copy {0}://{1}:{2}/{3} {4}'.format(protocol, host_ip_address, port, filename, name)
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': set_cmd , 'prompt':'\#'}
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_license()


    def delete(self, label):
        self._d.log_info("remove license {0}".format(label))
        self._update_license()

        if file_name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(file_name))

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': 'enable'  , 'prompt':'\#'},
                        {'cmd': delete_cmd, 'prompt':''  },
                        {'cmd': 'y'       , 'prompt':'\#', 'timeout': 10000}
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_license()


    def items(self):
        self._update_license()
        return self._license.items()


    def keys(self):
        self._update_license()
        return self._license.keys()


    def __getitem__(self, label):
        self._update_license()
        if label in self._license.keys():
            return self._license[label]
        raise KeyError('license {0} does not exist'.format(label))


    def _update_license(self):
        self._d.log_info("_update_license")
        self._license = OrderedDict()

        # OEM Territory : ATI USA
        # Software Licenses
        # ------------------------------------------------------------------------
        # Index                         : 1
        # License name                  : Base License
        # Customer name                 : ABC Consulting
        # Quantity of licenses          : 1
        # Type of license               : Full
        # License issue date            : 10-Dec-2013
        # License expiry date           : N/A
        # Features included             : EPSR-MASTER, IPv6Basic, MLDSnoop, OSPF-64,
        #                                 RADIUS-100, RIP, VRRP
        #
        # Index                         : 2
        # License name                  : 5.4.4-rl
        # Customer name                 : ABC Consulting
        # Quantity of licenses          : -
        # Type of license               : Full
        # License issue date            : 01-Oct-2013
        # License expiry date           : N/A
        # Release                       : 5.4.4

        ifre = re.compile('\s+(?P<index>\d+)\s+'
                          '\s+License\s+name\s+:\s+(?P<license>[^\s]+)\s+'
                          '\s+Customer\s+name\s+:\s+(?P<customer>[^\s]+)\s+'
                          '\s+Quantity\s+of\s+licenses\s+:\s+(?P<quantity>[^\s]+)\s+'
                          '\s+Type\s+of\s+license\s+:\s+(?P<type>[^\s]+)\s+'
                          '\s+License\s+issue\s+date\s+:\s+(?P<issue>[^\s]+)\s+'
                          '\s+License\s+expiry\s+date\s+:\s+(?P<expire>[^\s]+)\s+'
                         )
        for line in self._device.cmd("show license").split('Index                         :'):
            m = ifre.match(line)
            self._d.log_debug("\nLine {0}".format(line))
            if m:
                key = m.group('index')
                self._license[key] = {'index': m.group('index'),
                                      'license': m.group('license'),
                                      'customer': m.group('customer'),
                                      'quantity': m.group('quantity'),
                                      'type': m.group('type'),
                                      'issue_date': m.group('issue'),
                                      'expire_date': m.group('expire'),
                                     }
        self._d.log_debug("License {0}".format(pformat(json.dumps(self._license))))
