# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
from pprint import pprint,pformat
import yaml
import re
import logging
import sys
import zmq
import socket
import json
import inspect
from os import listdir,unlink
from os.path import dirname, isfile, join
from jinja2 import Template
from pynetworking import Feature
from pynetworking import SSHProxy
from multiprocessing import Process
from time import sleep
from tempfile import NamedTemporaryFile

class DeviceException(Exception):
    pass

class Device(object):
    def __init__(self, host, username='manager', password='friend', protocol='ssh', port='auto', os='auto',
                 log_level='NOTSET', log_output='console:'):
        if protocol not in ('telnet','ssh','serial'):
            raise ValueError("Unsupported protocol "+protocol)
        self._proxy = None
        self._proxy_url = ""
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._port = port

        self._log_level = getattr(logging, log_level.upper())
        hdl = logging.StreamHandler()
        if log_output.startswith('file://'):
            hdl = logging.FileHandler(log_output.split('://')[1])
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)-6s - %(message)s')
        hdl.setFormatter(formatter)
        log = logging.getLogger(self._host)
        log.handlers = []
        log.setLevel(self._log_level)
        log.addHandler(hdl)
        log.propagate = False

        self.log_info("Device created")
        self.log_debug("\nHost: {0}\nusername: {1}\npassword:{2}\nprotocol: {3}:{4}\nos: {5}".format(host, username, password, protocol, port, os))
        self._config = ''
        self._os = os
        self._facts = {}
        if os != 'auto':
            self._facts['os'] = os
        if protocol == 'ssh':
            self._proxy_target = SSHProxy
        else:
            raise ValueError("Protocol {0} is not supported".format(protocol))

    @property
    def facts(self):
        return self._facts

    @property
    def config(self):
        return self.system.get_config()

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, log_level):
        self._log_level = getattr(logging, log_level.upper())
        log = logging.getLogger(self._host)
        log.setLevel(self._log_level)
        return

    def ping(self):
        try:
            self.cmd('')
            self.log_debug("ping up")
            return True
        except:
            self.log_debug("ping down")
            return False

    def open(self):
        self.log_info("open")
        if not self._proxy:
             self._proxy_ipc_file = NamedTemporaryFile().name
             self._proxy_url = "ipc://{0}".format(self._proxy_ipc_file)
             self.log_info("creating proxy process {0} with zmq url {1}".format('cq-{0}'.format(self._host), self._proxy_url))
             self._proxy = Process(name='cq-{0}'.format(self._host),
                                        target=self._proxy_target,
                                        args=(self,)
                                       )
             self._proxy.start()
             self.log_debug("proxy process started")
        self._load_core_facts()
        self._load_features()
        self.load_system()

    def close(self):
        self.log_info("close")
        if self._proxy and self._proxy.is_alive():
            self.log_debug("shutting down proxy process")
            self._proxy.terminate()
            self._proxy.join()
            self._proxy = None
            unlink(self._proxy_ipc_file)

    def cmd(self, cmd):
        if type(cmd) is str:
             self.log_info("executing command '{0}'".format(cmd))
             cmd = {'cmds':[{'cmd':cmd,'prompt':''}]}
        else:
             for c in cmd['cmds']:
                 self.log_info("executing command '{0}' and wait for {1}".format(c['cmd'],repr(c['prompt'])))

        self.log_info("adding shell initialization commands")
        try:
            cmd['cmds'] = self.system.shell_init()+cmd['cmds']
        except:
            self.log_info("no shell init {0}".format(sys.exc_info()[0]))

        try:
             context = zmq.Context()
             socket = context.socket(zmq.REQ)
             socket.RCVTIMEO = 8000
             socket.connect(self._proxy_url)
             socket.send_string(json.dumps(cmd),zmq.NOBLOCK)
             ret = json.loads(socket.recv())
             if ret['status'] == 'Success':
                 self.log_debug("command execution success")
                 self.log_debug("command execution output \n{0}".format(ret['output']))
                 return ret['output']
             else:
                 self.log_warn("command execution '{0}' 'error {1}".format(cmd, ret))
                 raise DeviceException(ret['output'])
        except zmq.core.error.ZMQError, e:
             self.log_warn("ZMQError {0}".format(repr(e)))
             raise DeviceException("cannot communicate with device")
        except:
             raise DeviceException(sys.exc_info()[0])

    def _load_core_facts(self):
        self.log_info("loading core facts")
        facts_dir = "{0}/facts/".format(dirname(__file__))
        cf_re = re.compile('^core_[^\.]+.py$')
        cfs = [f.split(".")[0] for f in listdir(facts_dir) if isfile(join(facts_dir,f)) and cf_re.search(f)]
        for cf in cfs:
            self.log_info("fact file {0}".format(cf))
            try:
                f = __import__('pynetworking.facts.{0}'.format(cf))
                for comp in ('facts',cf,cf):
                    f = getattr(f, comp)
                self._facts =  dict(self._facts.items() + f(self).items())
                self.log_info("core facts loaded \n{0}".format(pformat(self._facts)))
            except AttributeError:
                self.log_critical("Error executing core fact {0}".format(cf))

    def _load_features(self):
        self.log_info("loading features")
        self._features = {}
        with open("{0}/Device.yaml".format(dirname(__file__)), 'r') as f:
            self._models = yaml.load(Template(f.read()).render(self._facts))
        if self._models == None or self._models['features'] == None:
            self.log_warn("no features loaded")
            self._models = {'features':{}}
        for fname,fclass in self._models['features'].items():
            self.log_info("loading feature {0}/{1}".format(fname,fclass))
            try:
                m = __import__('pynetworking.features.{0}'.format(fclass))
                for comp in ('features',fclass,fclass):
                    m = getattr(m, comp)
                o = m(self)
                setattr(self, fname, o)
                self._features[fname] = o
            except:
                self.log_critical("Error loading class {1} for feature {0}".format(fname,fclass))
                raise

    def load_system(self):
        self.log_info("load system")
        if 'system' in self._models:
            try:
                self.log_info("loading system module {0}".format(self._models['system']))
                m = __import__('pynetworking.system.{0}'.format(self._models['system']))
                for comp in ('system',self._models['system'],self._models['system']):
                    m = getattr(m, comp)
                o = m(self)
                setattr(self, 'system', o)
            except:
                self.log_warn("Error loading class {0} for system management".format(self._models['system']))
                raise
        else:
            self.log_warn("missing system module")

        cfg = self.system.get_config()
        self.log_debug("device configuration\n{0}".format(cfg))
        for fname,fobj in self._features.items():
            fobj.load_config(cfg)

    def log_debug(self, msg):
        self._logger(msg,'debug')

    def log_info(self, msg):
        self._logger(msg,'info')

    def log_warn(self, msg):
        self._logger(msg,'warn')

    def log_error(self, msg):
        self._logger(msg,'error')

    def log_critical(self, msg):
        self._logger(msg,'critical')

    def _logger(self, msg, level):
        (frame, filename, lineno, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[2]
        filename = filename.split('pynetworking/')[1]
        msg = '{0:30} [{1:3}] {2}'.format(filename, lineno, msg)
        log = logging.getLogger(self._host)
        if self._log_level != 0:
            getattr(log, level)(msg)

