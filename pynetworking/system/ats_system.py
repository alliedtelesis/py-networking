# -*- coding: utf-8 -*-
import re
import logging
import os


log = logging.getLogger(__name__)


class ats_system(object):
    """
    System for ATS
    """
    def __init__(self, device):
        self._d = device
        self._old_boot_bank = 0
        self._new_boot_bank = 0
        self._stand_by_bank = 0

    def get_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        for line in self._d.cmd('show running-config').replace('\r', '').split('\n'):
            config += line + '\n'
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def get_startup_config(self):
        self._d.log_info('getting device configuration')
        config = ''
        for line in self._d.cmd('show startup-config').replace('\r', '').split('\n'):
            config += line + '\n'
        self._d.log_debug('got device configuration \n{0}'.format(config))
        return config

    def save_config(self):
        self._d.log_info('save running configuration')
        cmds = {'cmds': [{'cmd': 'copy r s', 'prompt': ''},
                         {'cmd': 'y', 'prompt': '\#'}
                         ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)
        self._d.load_system()

    def shell_init(self):
        self._d.log_info('shell_init')
        return [{'cmd': 'terminal datadump', 'prompt': '\#'}, ]

    def shell_prompt(self):
        self._d.log_info('shell_prompt')
        return r'[\>\#]'

    def ping(self):
        self._d.log_info('ping')
        self._d.cmd('show version', use_cache=False)

    def update_firmware(self, filename, protocol='http', server='', port=69, dontwait=True):
        # Port and dontwait parameters are used only to get emulation working.
        # They are ignored by a normal PN user.
        self._d.log_info("firmware upgrade with {0}".format(filename))

        if (os.path.exists(filename) is False):
            raise KeyError('firmware {0} not available'.format(filename))
        if (protocol != 'tftp'):
            raise KeyError('protocol {0} not supported'.format(protocol))

        self._update_bank_data()
        boot_cmd = 'boot system image-{0}'.format(self._get_stand_by_bank())
        self._d.file.create(name='image', protocol=protocol, filename=filename, server=server, port=port)
        cmds = {'cmds': [{'cmd': boot_cmd, 'prompt': '\#'},
                         {'cmd': 'reload', 'prompt': ''},
                         {'cmd': 'y', 'prompt': '', 'dontwait': dontwait}
                         ]}
        self._d.cmd(cmds, cache=False, flush_cache=True)

    def _update_bank_data(self):
        # 1     1      image-1    3.0.0.44   02-Oct-2011  13:29:54   Not active
        ifre = re.compile('(?P<unit>\d+)\s+'
                          '(?P<image>\d+)\s+'
                          '(?P<file_name>[^\s]+)\s+'
                          '(?P<version>[^\s]+)\s+'
                          '(?P<date>[^\s]+)\s+'
                          '(?P<time>[^\s]+)\s+'
                          '(?P<status>[^\s]+)\s+')
        for line in self._d.cmd("show bootvar").split('\n'):
            m = ifre.match(line)
            self._d.log_debug("read {0}".format(line))
            if m:
                if (m.group('status')[:6] == 'Active'):
                    self._d.log_debug("active bank is {0}".format(m.group('image')))
                else:
                    self._stand_by_bank = m.group('image')
                if (line.find('*') > 0):
                    self._old_boot_bank = self._new_boot_bank
                    self._new_boot_bank = m.group('image')

    def _get_stand_by_bank(self):
        self._d.log_debug("stand by bank is {0}".format(self._stand_by_bank))
        return self._stand_by_bank

    def _is_boot_bank_changed(self):
        is_changed = False
        self._update_bank_data()
        self._d.log_debug("old boot bank is {0}".format(self._old_boot_bank))
        self._d.log_debug("new boot bank is {0}".format(self._new_boot_bank))
        if (self._old_boot_bank != self._new_boot_bank):
            is_changed = True
        return is_changed
