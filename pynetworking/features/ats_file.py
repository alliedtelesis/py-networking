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

from tempfile import mkstemp
from time import sleep
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_file(Feature):
    """
    File feature implementation for ATS
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._file={}
        self._tftp_port=69
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")


    def create(self, name, port=69, text='', filename='', server=''):
        self._d.log_debug("User: {0}".format(getpass.getuser()))
        self._d.log_debug("Local IP address: {0}".format(socket.gethostbyname(socket.getfqdn())))
        self._d.log_debug("TFTP server: {0} (local IP address if missing)".format(server))
        self._d.log_info("create file {0}".format(name))
        self._update_file()

        if name in self._d.file.keys():
            raise KeyError('file {0} is already existing'.format(name))
        if (filename != '' and text != ''):
            raise KeyError('Cannot have both source device file name and host string not empty')
        if (filename == '' and server != ''):
            raise KeyError('Remote file name missing')

        if (filename == ''):
            filename = name
            myfile = open(filename, 'w')

            # TFTP doesn't allow empty file creation
            if (text == ''):
                myfile.write('\n')
            else:
                myfile.write(text)
            myfile.close()

        # upload on TFTP server
        if (server == ''):
            server = socket.gethostbyname(socket.getfqdn())
        tftp_client = tftpy.TftpClient(server, port)
        tftp_client.upload(filename, filename)
        self._tftp_port = port

        # device commands (timeout of 10 seconds for each MB)
        timeout = (os.path.getsize(filename)/1048576 + 1)*10000
        create_cmd = 'copy tftp://{0}/{1} {2}'.format(server, filename, name)
        cmds = {'cmds':[{'cmd': create_cmd, 'prompt': '\#', 'timeout': timeout}]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_file()


    def update(self, name, port=69, filename='', text='', new_name='', server=''):
        self._d.log_info("copying {0} from host to device".format(name))
        self._update_file()

        if name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(name))
        if new_name in self._d.file.keys():
            raise KeyError('file {0} cannot be overwritten'.format(new_name))
        if (filename != '' and text != ''):
            raise KeyError('Cannot have both host file name and host string not empty')
        if (filename == '' and text == ''):
            raise KeyError('Cannot have both host file name and host string empty')
        if (filename == '' and server != ''):
            raise KeyError('Remote file name missing')

        # data to be copied will always come from a local file named 'file_2_copy_from'
        if (filename == ''):
            file_2_copy_from = name
        else:
            file_2_copy_from = filename
        if (text != ''):
            myfile = open(file_2_copy_from, 'w')
            myfile.write(text)
            myfile.close()

        # upload on TFTP server
        if (server == ''):
            server = socket.gethostbyname(socket.getfqdn())
        tftp_client = tftpy.TftpClient(server, port)
        tftp_client.upload(file_2_copy_from, file_2_copy_from)
        self._tftp_port = port

        # device commands (timeout of 30 seconds for each MB)
        timeout = (os.path.getsize(file_2_copy_from)/1048576 + 1)*30000
        if (new_name == ''):
            update_cmd = 'copy tftp://{0}/{1} {2}'.format(server, file_2_copy_from, name)
            cmds = {'cmds': [{'cmd': update_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#', 'timeout' : timeout}
                            ]}
        else:
            update_cmd = 'copy tftp://{0}/{1} {2}'.format(server, file_2_copy_from, new_name)
            delete_cmd = 'delete {0}'.format(name)
            cmds = {'cmds': [{'cmd': update_cmd, 'prompt': '\#', 'timeout': timeout},
                             {'cmd': delete_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#', 'timeout': timeout}
                             ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_file()

        if (text != ''):
            os.remove(file_2_copy_from)


    def delete(self, file_name):
        self._d.log_info("remove {0}".format(file_name))
        self._update_file()

        if file_name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(file_name))

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': delete_cmd, 'prompt':''  },
                        {'cmd': 'y'       , 'prompt':'\#', 'timeout': 10000}
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_file()


    def items(self):
        self._update_file()
        return self._file.items()


    def keys(self):
        self._update_file()
        return self._file.keys()


    def __getitem__(self, filename):
        self._update_file()
        if filename in self._file.keys():
            self._file[filename]['content'] = self._update_file_content(filename)
            return self._file[filename]
        raise KeyError('file {0} does not exist'.format(filename))


    def _update_file_content(self, filename):
        self._d.log_info("Read file {0} content".format(filename))
        read_cmd = 'copy {0} tftp://{1}/{0}'.format(filename, socket.gethostbyname(socket.getfqdn()))
        cmds = {'cmds':[{'cmd': read_cmd, 'prompt':'\#'}]}
        self._device.cmd(cmds, cache=False, flush_cache=True)

        temp, temp_file_name = mkstemp()
        client = tftpy.TftpClient(socket.gethostbyname(socket.getfqdn()), self._tftp_port)
        client.download(filename, temp_file_name)

        read_output = ''
        myfile = open(temp_file_name, 'r')
        read_output = myfile.read()
        myfile.close()
        os.remove(temp_file_name)
        return read_output


    def _update_file(self):
        self._d.log_info("_update_file")
        self._file = OrderedDict()

        # starts                  rw       524288      982     01-Oct-2006 01:12:44
        ifre = re.compile('(?P<file_name>[^\s]+)\s+'
                          '(?P<permission>[^\s]+)\s+'
                          '(?P<flash_size>\d+)\s+'
                          '(?P<data_size>\d+)\s+'
                          '(?P<date>[^\s]+)\s+'
                          '(?P<time>[^\s]+)\s+')
        for line in self._device.cmd("dir").split('\n'):
            m = ifre.match(line)
            self._d.log_info("read {0}".format(line))
            if m:
                key = m.group('file_name')
                self._file[key] = {'size': m.group('data_size'),
                                   'permission': m.group('permission'),
                                   'mdate': m.group('date'),
                                   'mtime': m.group('time')
                                  }
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._file))))


