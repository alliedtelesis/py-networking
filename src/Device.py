# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
from pprint import pprint
import yaml
import re
import logging
import sys
import zmq
import socket
import json
from os import listdir,unlink
from os.path import dirname, isfile, join
from jinja2 import Template
from pynetworking import Feature
from pynetworking import SSHProxy
from multiprocessing import Process
from time import sleep
from tempfile import NamedTemporaryFile

log = logging.getLogger(__name__)
#log.setLevel(logging.DEBUG)

class Device(object):
    def __init__(self, host, username='manager', password='friend', protocol='ssh', port='auto', os='auto'):
        if protocol not in ('telnet','ssh','serial'):
            raise ValueError("Unsupported protocol "+protocol)
        self._proxy = None
        self._proxy_url = ""
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._port = port
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
        return self.cfg.get_config()

    def ping(self):
        try:
            self.cmd('')
            return True
        except:
            return False

    def open(self):
        if not self._proxy:
             self._proxy_ipc_file = NamedTemporaryFile().name
             self._proxy_url = "ipc://{0}".format(self._proxy_ipc_file)
             log.debug("Creating process {0} with zmq url {1}".format('cq-{0}'.format(self._host), self._proxy_url))
             self._proxy = Process(name='cq-{0}'.format(self._host),
                                        target=self._proxy_target,
                                        args=(self._proxy_url, self._host, self._port,self._username, self._password)
                                       )
             self._proxy.start()
        self._load_core_facts()
        self._load_features()
        self.load_config()

    def close(self):
        if self._proxy and self._proxy.is_alive():
            self._proxy.terminate()
            self._proxy.join()
            self._proxy = None
            unlink(self._proxy_ipc_file)

    def cmd(self, cmd):
        log.debug("Executing command {0}".format(cmd))
        if type(cmd) is str:
             cmd = {'cmds':[{'cmd':cmd,'prompt':''}]}
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.RCVTIMEO = 3000
        socket.connect(self._proxy_url)
        socket.send_string(json.dumps(cmd),zmq.NOBLOCK)
        return socket.recv()

    def _load_core_facts(self):
        facts_dir = "{0}/facts/".format(dirname(__file__))
        cf_re = re.compile('^core_[^\.]+.py$')
        cfs = [f.split(".")[0] for f in listdir(facts_dir) if isfile(join(facts_dir,f)) and cf_re.search(f)]
        for cf in cfs:
            try:
                f = __import__('pynetworking.facts.{0}'.format(cf))
                for comp in ('facts',cf,cf):
                    f = getattr(f, comp)
                self._facts =  dict(self._facts.items() + f(self).items())
            except AttributeError:
                print "Error executing core fact {0}".format(cf)

    def _load_features(self):
        self._features = {}
        with open("{0}/Device.yaml".format(dirname(__file__)), 'r') as f:
            self._models = yaml.load(Template(f.read()).render(self._facts))
        if self._models == None or self._models['features'] == None:
            self._models = {'features':{}}
        for fname,fclass in self._models['features'].items():
            try:
                m = __import__('pynetworking.features.{0}'.format(fclass))
                for comp in ('features',fclass,fclass):
                    m = getattr(m, comp)
                o = m(self)
                setattr(self, fname, o)
                self._features[fname] = o
            except:
                print "Error loading class {1} for feature {0}".format(fname,fclass)
                raise

    def load_config(self):
        if 'config' in self._models:
            try:
                m = __import__('pynetworking.config.{0}'.format(self._models['config']))
                for comp in ('config',self._models['config'],self._models['config']):
                    m = getattr(m, comp)
                o = m(self)
                setattr(self, 'cfg', o)
            except:
                print "Error loading class {0} for configuration management".format(self._models['config'])
                raise

        cfg = self.cfg.get_config()
        for fname,fobj in self._features.items():
            fobj.load_config(cfg)

