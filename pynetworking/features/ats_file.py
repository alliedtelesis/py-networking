# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
import socket
import threading
import tftpy

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
        self._file_config={}
        self._file={}
        self._d = device
        self._d.log_debug("loading feature")

    def load_config(self, config):
        self._d.log_info("loading config")
        self._file_config = OrderedDict()

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
                self._file_config[m.group('file_name')] = {'size': m.group('data_size'),
                                                           'permission': m.group('permission'),
                                                           'mdate': m.group('date'),
                                                           'mtime': m.group('time')
                                                          }
        self._d.log_info(self._file_config)


    def create(self, name, text='', filename=''):
        self._d.log_info("create file {0}".format(name))
        self._update_file()

        if name in self._d.file.keys():
            raise KeyError('file {0} is already existing'.format(name))
        if (filename != '' and text != ''):
            raise KeyError('Cannot have both source device file name and host string not empty')

        if (filename == ''):
            filename = name
            myfile = open(filename, 'w')
            myfile.write(text)
            myfile.close()

        # device commands
        host_ip_address = socket.gethostbyname(socket.getfqdn())

        create_cmd = 'copy tftp://{0}/{1} {2}'.format(host_ip_address, filename, name)
        cmds = {'cmds':[{'cmd': create_cmd  , 'prompt':'\#'}]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

        # host TFTP server
        tftpRoot = os.path.dirname(os.path.abspath(filename))
        server = tftpy.TftpServer(tftpRoot)
        server_timer = threading.Timer(10, self._shutdown_tftp_server(server))
        server_timer.start()
        server_thread = threading.Thread(target=server.listen(host_ip_address,20001))
        server_timer.cancel()

        if (text != ''):
            os.remove(filename)


    def update(self, name, filename='', text='', new_name=''):
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

        # data to be copied will always come from a local file named 'file_2_copy_from'
        if (filename == ''):
            file_2_copy_from = name
        else:
            file_2_copy_from = filename
        if (text != ''):
            myfile = open(file_2_copy_from, 'w')
            myfile.write(text)
            myfile.close()

        # host TFTP server thread
        server = Server(("", 0), TFTPHandler, self._d, filename)
        ip, port = server.server_address

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        self._d.log_info("server running on {0}:{1}".format(ip, port))

        # device commands
        host_ip_address = socket.gethostbyname(socket.getfqdn())

        if (new_name == ''):
            update_cmd = 'copy tftp://{0}/{1} {2}'.format(host_ip_address, file_2_copy_from, name)
            delete_cmd = 'delete {0}'.format(name)
            cmds = {'cmds': [{'cmd': delete_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#'},
                             {'cmd': update_cmd, 'prompt': '\#'}
                            ]}
        else:
            update_cmd = 'copy tftp://{0}/{1} {2}'.format(host_ip_address, file_2_copy_from, new_name)
            delete_cmd = 'delete {0}'.format(name)
            cmds = {'cmds': [{'cmd': update_cmd, 'prompt': '\#'},
                             {'cmd': delete_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#'}
                            ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()

        if (text != ''):
            os.remove(file_2_copy_from)


    def delete(self, file_name):
        self._d.log_info("remove {0}".format(file_name))
        self._update_file()

        if file_name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(file_name))

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': delete_cmd, 'prompt':''  },
                        {'cmd': 'y'       , 'prompt':'\#'}
                       ]}

        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._device.load_system()


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
        read_cmd = 'show file {0}'.format(filename)
        cmds = {'cmds':[{'cmd': read_cmd, 'prompt':'\#'}]}
        read_output = self._device.cmd(read_cmd)
        read_output = read_output.replace('\r', '')
        read_output = read_output.replace('\n\n', '\n')
        return read_output


    def _shutdown_tftp_server(self, server):
        server.shutdown_gracefully = True

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
                self._file[key] = dict(self._file[key].items() + self._file_config[key].items())
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._file))))
