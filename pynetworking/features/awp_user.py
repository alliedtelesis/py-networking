# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict

class awp_user(Feature):
    """
    User account feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._user_config={}
        self._user={}
        self._d = device
        self._d.log_debug("loading feature")

    def load_config(self, config):
        self._d.log_info("loading config")
        self._user_config = OrderedDict()

        # username manager privilege 15 password 8 $1$bJoVec4D$JwOJGPr7YqoExA0GVasdE0
        ifre = re.compile('username\s+'
                          '(?P<user_name>[^\s]+)\s+'
                          'privilege\s+'
                          '(?P<privilege_level>\d+)\s+'
                          'password\s+8\s+'
                          '(?P<password>[^\s]+)\s+')
        for line in self._device.cmd("show running-config").split('\n'):
            m = ifre.match(line)
            if m:
                self._user_config[m.group('user_name')] = {'privilege_level': m.group('privilege_level'),
                                                           'encryption': True,
                                                           'password': m.group('password')
                                                          }

        # username testuser privilege 5 password enemy
        ifre = re.compile('username\s+'
                          '(?P<user_name>[^\s]+)\s+'
                          'privilege\s+'
                          '(?P<privilege_level>\d+)\s+'
                          'password\s+'
                          '(?P<password>[^\s]+)\s+')
        for line in self._device.cmd("show running-config").split('\n'):
            m = ifre.match(line)
            if m:
                if m.group('password') != '8':
                    self._user_config[m.group('user_name')] = {'privilege_level': m.group('privilege_level'),
                                                               'encryption': False,
                                                               'password': m.group('password')
                                                              }
        self._d.log_info(self._user_config)


    def create(self, user_name, password, privilege_level):
        self._d.log_info("add {0} {1} {2}".format(user_name, password, privilege_level))

        enc_pwd = False
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': 'conf t', 'prompt':'\(config\)\#'}
                       ]}

        if enc_pwd == False:
            create_cmd = 'username {0} privilege {1} password {2}'.format(user_name, privilege_level, password)
        else:
            create_cmd = 'username {0} privilege {1} password 8 {2}'.format(user_name, privilege_level, password)
        cmds['cmds'].append({'cmd': create_cmd, 'prompt':'\#'})
        cmds['cmds'].append({'cmd': chr(26)   , 'prompt':'\#'})

        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()


    def delete(self, user_name):
        self._d.log_info("remove {0}".format(user_name))
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': 'conf t', 'prompt':'\(config\)\#'}
                       ]}
        delete_cmd = 'no username {0}'.format(user_name)
        cmds['cmds'].append({'cmd': delete_cmd, 'prompt':'\#'})
        cmds['cmds'].append({'cmd': chr(26)   , 'prompt':'\#'})

        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()


    def update(self, user_name, **kwargs):
        self._d.log_info("update {0} {1}".format(user_name,pformat(kwargs)))

        enc_pwd = False
        run_cmd = False
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': 'conf t', 'prompt':'\(config\)\#'}
                       ]}

        if 'password' in kwargs:
            pwd = kwargs['password']
            if enc_pwd == False:
                pwd_cmd = 'username {0} password {1}'.format(user_name, pwd)
            else:
                pwd_cmd = 'username {0} password 8 {1}'.format(user_name, pwd)
            cmds['cmds'].append({'cmd': pwd_cmd, 'prompt':'\#'})
            run_cmd=True

        if 'privilege_level' in kwargs:
            level = kwargs['privilege_level']
            priv_cmd = 'username {0} privilege {1}'.format(user_name, level)
            cmds['cmds'].append({'cmd': priv_cmd, 'prompt':'\#'})
            run_cmd=True

        if run_cmd:
            cmds['cmds'].append({'cmd': chr(26)   , 'prompt':'\#'})
            # self._device.cmd(cmds, cache=False, flush_cache=True)
            # self._device.load_system()
