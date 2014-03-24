# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
from pprint import pprint
import yaml
import re
from os import listdir
from os.path import dirname, isfile, join
from jinja2 import Template

class Device(object):
    def __init__(self, host, username='manager', password='friend', protocol='ssh', port='auto', type='auto'):
        if protocol not in ('telnet','ssh','serial'):
            raise ValueError("Unsupported protocol "+protocol)
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        if protocol == 'ssh':
            self._conn = SSHClient()
            self._conn.set_missing_host_key_policy(AutoAddPolicy())
            if port == 'auto':
                self._port = 22
            else:
                self._port = port
        else:
            self._conn = None
        self._type = type
        self._facts = {}
        if type != 'auto':
            self._facts['type'] = type

    @property
    def facts(self):
        return self._facts

    def ping(self):
        if self._protocol == 'ssh':
            if self._conn.get_transport() != None and self._conn.get_transport().is_active():
                return True
        return False

    def open(self):
        if self._protocol == 'ssh':
            if self._conn.get_transport() == None or not self._conn.get_transport().is_active():
                self._conn.connect(self._host, self._port,self._username, self._password)
        else:
            raise IOError("Open failed on {0} with protocol {1}".format(self._host,self._protocol))
            return
        self._load_core_facts()
        self._load_features()

    def close(self):
        if self._protocol == 'ssh':
            self._conn.close()

    def cmd(self, cmd):
        if self._protocol == 'ssh':
            stdin, stdout, stderr = self._conn.exec_command(cmd)
            return stdout.read()
        return ""

    def config(self):
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
                self._features['fname'] = o
            except:
                print "Error loading class {1} for feature {0}".format(fname,fclass)

