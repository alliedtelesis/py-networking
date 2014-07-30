# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
import socket
import SocketServer
import threading
import BaseHTTPServer
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.server.filename == self.path[1:]:
            try:
                with open(os.path.abspath(self.server.filename), 'rb') as f:
                    self.server._d.log_info('sending file {0}'.format(os.path.abspath(self.server.filename)))
                    self.send_response(200)
                    self.send_header('Content-type', 'application/octet-string')
                    self.end_headers()
                    self.wfile.write(f.read())
            except:                                                                 #pragma: no cover
                self.server._d.log_error('cannot open file {0}'.format(self.path))  #pragma: no cover
                self.send_response(404)                                             #pragma: no cover
                self.end_headers()                                                  #pragma: no cover
        else:                                                                       #pragma: no cover
            self.server._d.log_error('wrong file requested {0}'.format(self.path))  #pragma: no cover
            self.send_response(404)                                                 #pragma: no cover
            self.end_headers()                                                      #pragma: no cover


class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, address, handler, device, filename):
        self.filename = filename
        self._d = device
        SocketServer.TCPServer.__init__(self, address, handler)


class awp_file(Feature):
    """
    File feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._file={}
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")


    def create(self, name, protocol='http', text='', filename=''):
        self._d.log_info("create file {0}".format(name))
        self._update_file()

        if name in self._d.file.keys():
            raise KeyError('file {0} is already existing'.format(name))
        if (protocol != 'http'):
            raise KeyError('protocol {0} not supported'.format(protocol))
        if (filename != '' and text != ''):
            raise KeyError('Cannot have both source device file name and host string not empty')

        if (filename == ''):
            filename = name
            myfile = open(filename, 'w')
            myfile.write(text)
            myfile.close()

        # host HTTP server thread
        server = Server(("", 0), HTTPHandler, self._d, filename)
        ip, port = server.server_address

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        self._d.log_info("server running on {0}:{1}".format(ip, port))

        # device commands (timeout of 10 seconds for each MB)
        host_ip_address = socket.gethostbyname(socket.getfqdn())
        timeout = (os.path.getsize(filename)/1048576 + 1)*10000
        create_cmd = 'copy {0}://{1}:{2}/{3} {4}'.format(protocol, host_ip_address, port, filename, name)
        cmds = {'cmds':[{'cmd': 'enable'    , 'prompt':'\#'},
                        {'cmd': create_cmd  , 'prompt':'\#', 'timeout': timeout}
                       ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_file()

        server.shutdown()
        if (text != ''):
            os.remove(filename)


    def update(self, name, protocol='http', filename='', text='', new_name=''):
        self._d.log_info("copying {0} from host to device".format(name))
        self._update_file()

        if name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(name))
        if (protocol != 'http'):
            raise KeyError('protocol {0} not supported'.format(protocol))
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

        # host HTTP server thread
        server = Server(("", 0), HTTPHandler, self._d, file_2_copy_from)
        ip, port = server.server_address

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        self._d.log_info("server running on {0}:{1}".format(ip, port))

        # device commands
        host_ip_address = socket.gethostbyname(socket.getfqdn())

        if (new_name == ''):
            update_cmd = 'copy {0}://{1}:{2}/{3} {4}'.format(protocol, host_ip_address, port, file_2_copy_from, name)
            delete_cmd = 'delete {0}'.format(name)
            cmds = {'cmds': [{'cmd': 'enable'  , 'prompt': '\#'},
                             {'cmd': delete_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#'},
                             {'cmd': update_cmd, 'prompt': '\#'}
                            ]}
        else:
            update_cmd = 'copy http://{0}:{1}/{2} {3}'.format(host_ip_address, port, file_2_copy_from, new_name)
            delete_cmd = 'delete {0}'.format(name)
            cmds = {'cmds': [{'cmd': 'enable'  , 'prompt': '\#'},
                             {'cmd': update_cmd, 'prompt': '\#'},
                             {'cmd': delete_cmd, 'prompt': ''  },
                             {'cmd': 'y'       , 'prompt': '\#'}
                            ]}
        self._device.cmd(cmds, cache=False, flush_cache=True)
        self._update_file()

        server.shutdown()

        if (text != ''):
            os.remove(file_2_copy_from)


    def delete(self, file_name):
        self._d.log_info("remove {0}".format(file_name))
        self._update_file()

        if file_name not in self._d.file.keys():
            raise KeyError('file {0} is not existing'.format(file_name))

        delete_cmd = 'delete {0}'.format(file_name)
        cmds = {'cmds':[{'cmd': 'enable'  , 'prompt':'\#'},
                        {'cmd': delete_cmd, 'prompt':''  },
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
        read_cmd = 'show file {0}'.format(filename)
        cmds = {'cmds':[{'cmd': 'enable', 'prompt':'\#'},
                        {'cmd': read_cmd, 'prompt':'\#'}
                       ]}
        read_output = self._device.cmd(read_cmd)
        read_output = read_output.replace('\r', '')
        read_output = read_output.replace('\n\n', '\n')
        return read_output


    def _update_file(self):
        self._d.log_info("_update_file")
        self._file = OrderedDict()

        # 588 -rw- Jun 10 2014 12:38:10  michele.cfg
        ifre = re.compile('\s+(?P<size>\d+)\s+'
                          '(?P<permission>[^\s]+)\s+'
                          '(?P<month>[^\s]+)\s+'
                          '(?P<day>\d+)\s+'
                          '(?P<year>\d+)\s+'
                          '(?P<hhmmss>[^\s]+)\s+'
                          '(?P<file_name>[^\s]+)')
        for line in self._device.cmd("dir").split('\n'):
            m = ifre.match(line)
            if m:
                key = m.group('file_name')
                self._file[key] = {'size': m.group('size'),
                                   'permission': m.group('permission'),
                                   'mdate': m.group('day') + '-' + m.group('month') + '-' + m.group('year'),
                                   'mtime': m.group('hhmmss')
                                  }
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._file))))
