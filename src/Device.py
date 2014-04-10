# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
from pprint import pprint
import yaml
import re
from os import listdir
from os.path import dirname, isfile, join
from jinja2 import Template
from pynetworking import Feature
import logging

log = logging.getLogger(__name__)

class Device(object):
    def __init__(self, host, username='manager', password='friend', protocol='ssh', port='auto', os='auto'):
        if protocol not in ('telnet','ssh','serial'):
            raise ValueError("Unsupported protocol "+protocol)
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._config = ''
        if protocol == 'ssh':
            self._conn = SSHClient()
            self._conn.set_missing_host_key_policy(AutoAddPolicy())
            if port == 'auto':
                self._port = 22
            else:
                self._port = port
        else:
            self._conn = None
        self._os = os
        self._facts = {}
        if os != 'auto':
            self._facts['os'] = os

    @property
    def facts(self):
        return self._facts

    @property
    def config(self):
        return self.cfg.get_config()

    def ping(self):
        if self._protocol == 'ssh':
            try:
            	self._conn.connect(self._host, self._port,self._username, self._password)
                self._conn.close()
                return True
            except:
                pass
        return False

    def open(self):
#        if self._protocol == 'ssh':
#            if self._conn.get_transport() == None or not self._conn.get_transport().is_active():
#                self._conn.connect(self._host, self._port,self._username, self._password)
#                self._conn.get_transport().set_keepalive(1)
#        else:
#            raise IOError("Open failed on {0} with protocol {1}".format(self._host,self._protocol))
#            return
        self._load_core_facts()
        self._load_features()
        self.load_config()

    def close(self):
        if self._protocol == 'ssh':
            self._conn.close()

    def get_channel(self):
        if self._protocol == 'ssh':
            self._conn.connect(self._host, self._port,self._username, self._password)
            return self._conn.invoke_shell()
        return None

    def cmd(self, cmd):
        log.debug("Executing command {0}".format(cmd))
        if self._protocol == 'ssh':
            self._conn.connect(self._host, self._port,self._username, self._password)
            stdin, stdout, stderr = self._conn.exec_command(cmd)
            out = stdout.read()
            self._conn.close()
            log.debug("Return for command {0}: {1}".format(cmd,out))
            return out
        return ""

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
        


