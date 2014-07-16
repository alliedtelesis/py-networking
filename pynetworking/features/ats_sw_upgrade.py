# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
import getpass
import socket
import threading
import tftpy
import ats_file

from tempfile import mkstemp
from time import sleep
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_sw_upgrade(Feature):
    """
    ATS software upgrade feature
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._d = device
        self._d.log_debug("loading feature")
        self._image_config={}
        self._image={}
        self._file = ats_file

    def load_config(self, config):
        self._d.log_info("loading config")
        self._image_config = OrderedDict()
        #
        # # starts                  rw       524288      982     01-Oct-2006 01:12:44
        # ifre = re.compile('(?P<file_name>[^\s]+)\s+'
        #                   '(?P<permission>[^\s]+)\s+'
        #                   '(?P<flash_size>\d+)\s+'
        #                   '(?P<data_size>\d+)\s+'
        #                   '(?P<date>[^\s]+)\s+'
        #                   '(?P<time>[^\s]+)\s+')
        # for line in self._device.cmd("dir").split('\n'):
        #     m = ifre.match(line)
        #     self._d.log_info("read {0}".format(line))
        #     if m:
        #         self._file_config[m.group('file_name')] = {'size': m.group('data_size'),
        #                                                    'permission': m.group('permission'),
        #                                                    'mdate': m.group('date'),
        #                                                    'mtime': m.group('time')
        #                                                   }
        # self._d.log_info(self._file_config)


    def create(self, name, server='', filename=''):
        self._d.log_info("create image {0}".format(name))
        self._update_image_dict()

        if (os.path.exists(name) == False):
            raise KeyError('image {0} not available on server'.format(name))
        if name in self._d.file.keys():
            raise KeyError('image {0} is already existing'.format(name))

        # if (filename == ''):
        #     filename = name
        #     myfile = open(filename, 'w')
        #
        #     # TFTP doesn't allow empty file creation
        #     if (text == ''):
        #         myfile.write('\n')
        #     else:
        #         myfile.write(text)
        #     myfile.close()
        #
        # # upload on TFTP server
        # if (server == ''):
        #     server = socket.gethostbyname(socket.getfqdn())
        # tftp_client = tftpy.TftpClient(server, port)
        # tftp_client.upload(filename, filename)
        # self._update_port(port)
        #
        # # device commands
        # create_cmd = 'copy tftp://{0}/{1} {2}'.format(server, filename, name)
        # cmds = {'cmds':[{'cmd': create_cmd  , 'prompt':'\#'}]}
        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()


    def update(self, name, port=69, server='', filename=''):
        self._d.log_info("upgrading image {0}".format(name))
        self._update_image_dict()

        if (os.path.exists(name) == False):
            raise KeyError('image {0} not available'.format(name))

        self._file.create(self, 'image', port=port, filename=name, server=server)
        boot_cmd = 'boot system image-{0}'.format(self._get_stand_by_bank())
        cmds = {'cmds': [{'cmd': boot_cmd, 'prompt': '\#'}
                        ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

        # # upload on TFTP server
        # if (server == ''):
        #     server = socket.gethostbyname(socket.getfqdn())
        # tftp_client = tftpy.TftpClient(server, port)
        # tftp_client.upload(name, name)
        #
        # # device commands
        # stand_by_bank = 1 #FIXME
        # update_cmd = 'copy tftp://{0}/{1} image'.format(server, name)
        # boot_cmd = 'boot system image-{0}'.format(stand_by_bank)
        # cmds = {'cmds': [{'cmd': update_cmd, 'prompt': '\#'},
        #                  {'cmd': boot_cmd  , 'prompt': '\#'}
        #                 ]}
        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()


    def delete(self, name):
        self._d.log_info("remove image {0}".format(name))
        self._update_image_dict()

        if name not in self._d.file.keys():
            raise KeyError('image {0} is not existing'.format(name))

        # delete_cmd = 'delete {0}'.format(file_name)
        # cmds = {'cmds':[{'cmd': delete_cmd, 'prompt':''  },
        #                 {'cmd': 'y'       , 'prompt':'\#'}
        #                ]}
        #
        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()


    def items(self):
        self._update_image_dict()
        return self._file.items()


    def keys(self):
        self._update_image_dict()
        return self._file.keys()


    def __getitem__(self, filename):
        self._update_image_dict()
        if filename in self._file.keys():
            self._file[filename]['content'] = self._update_image_content(filename)
            return self._file[filename]
        raise KeyError('image {0} does not exist'.format(filename))


    def _update_image_content(self, filename):
        self._d.log_info("Read image {0} content".format(filename))
        # read_cmd = 'copy {0} tftp://{1}/{0}'.format(filename, socket.gethostbyname(socket.getfqdn()))
        # cmds = {'cmds':[{'cmd': read_cmd, 'prompt':'\#'}]}
        # self._device.cmd(cmds, cache=False, flush_cache=True)
        # self._device.load_system()
        # temp, temp_file_name = mkstemp()
        #
        # client = tftpy.TftpClient(socket.gethostbyname(socket.getfqdn()), self._get_port())
        # client.download(filename, temp_file_name)
        #
        # read_output = ''
        # myfile = open(temp_file_name, 'r')
        # read_output = myfile.read()
        # myfile.close()
        # os.remove(temp_file_name)
        # return read_output


    def _update_image_dict(self):
        self._d.log_info("_update_image_dict")
        self._image = OrderedDict()
        # # starts                  rw       524288      982     01-Oct-2006 01:12:44
        # ifre = re.compile('(?P<file_name>[^\s]+)\s+'
        #                   '(?P<permission>[^\s]+)\s+'
        #                   '(?P<flash_size>\d+)\s+'
        #                   '(?P<data_size>\d+)\s+'
        #                   '(?P<date>[^\s]+)\s+'
        #                   '(?P<time>[^\s]+)\s+')
        # for line in self._device.cmd("dir").split('\n'):
        #     m = ifre.match(line)
        #     self._d.log_info("read {0}".format(line))
        #     if m:
        #         key = m.group('file_name')
        #         self._file[key] = {'size': m.group('data_size'),
        #                            'permission': m.group('permission'),
        #                            'mdate': m.group('date'),
        #                            'mtime': m.group('time')
        #                           }
        #         self._file[key] = dict(self._file[key].items() + self._file_config[key].items())
        # self._d.log_debug("File {0}".format(pformat(json.dumps(self._file))))


    def _get_stand_by_bank(self):
        stand_by_bank = 1 #FIXME
        return stand_by_bank
