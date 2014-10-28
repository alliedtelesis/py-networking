# -*- coding: utf-8 -*-
from pprint import pformat
import yaml
import re
import logging
import sys
import zmq
import json
import inspect
import traceback
from os import listdir
from os.path import dirname, isfile, join
from jinja2 import Template
from pynetworking.Proxy import SSHProxy
from multiprocessing import Process
from time import sleep
from tempfile import NamedTemporaryFile
from mock import MagicMock
from mock import patch


class DeviceException(Exception):
    pass


class Device(object):
    """ test doc
    """
    def __init__(self, host, username='manager', password='friend', protocol='ssh', port='auto', os='auto',
                 log_level='NOTSET', log_output='console:', connection_timeout=20, mock='n'):
        if protocol not in ('telnet', 'ssh', 'serial'):
            raise ValueError("Unsupported protocol " + protocol)
        self._proxy = None
        self._proxy_ipc_file = NamedTemporaryFile().name
        self._proxy_url = "ipc://{0}".format(self._proxy_ipc_file)
        self._proxy_connection_timeout = connection_timeout * 1000
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._port = port

        self._mock_test = self._get_mock_opt(mock.lower())

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

    @property
    def host(self):
        return self._host

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def ping(self):
        try:
            self.system.ping()
            self.log_debug("ping up")
            return True
        except:
            self.log_debug("ping down")
            return False

    def open(self):
        self.log_info("open")
        if self._mock_test is False:
            self._open()
        else:
            self._mocked_open()  # pragma: no cover

    def close(self):
        self.log_info("close")
        if isinstance(self._proxy, Process) and (isinstance(self._proxy, Process) and self._proxy.is_alive()):
            self.cmd({'cmds': [{'cmd': '_exit', 'prompt': ''}]})
            self._proxy.join(10)

    def cmd(self, cmd, use_cache=True, cache=False, flush_cache=False):
        timeout = 12000
        if type(cmd) is str:
            self.log_info("executing command '{0}'".format(cmd))
            cmd = {'cmds': [{'cmd': cmd, 'prompt': self.system.shell_prompt()}]}
        else:
            for c in cmd['cmds']:
                self.log_info("executing command '{0}' and wait for {1}".format(c['cmd'], repr(c['prompt'])))
                if ('timeout' in c.keys()):
                    timeout += c['timeout']

        if not cmd['cmds'][0]['cmd'].startswith('_'):
            self.log_info("adding shell initialization commands")
            try:
                cmd['cmds'] = self.system.shell_init() + cmd['cmds']
            except:
                self.log_info("no shell init {0}".format(sys.exc_info()[0]))

        cmd['cache'] = use_cache
        cmd['flush_cache'] = flush_cache

        self._start_proxy()
        try:
            context = zmq.Context()
            skt = context.socket(zmq.REQ)
            skt.setsockopt(zmq.LINGER, 1000)
            skt.connect(self._proxy_url)
            skt.send_string(json.dumps(cmd), zmq.NOBLOCK)

            poller = zmq.Poller()
            poller.register(skt, zmq.POLLIN)
            if len(poller.poll(timeout)) == 0:
                self.log_warn("timeout on cmd ({0})".format(self._proxy.exitcode))
                raise DeviceException('proxy exited with error ({0})'.format(self._proxy.exitcode))

            ret = json.loads(skt.recv(zmq.NOBLOCK))
            if ret['status'] == 'Success':
                self.log_debug("command execution success")
                self.log_debug("command execution output \n{0}".format(ret['output']))
                return ret['output']
            else:
                self.log_warn("command execution '{0}' 'error {1}".format(cmd, ret))
                raise DeviceException(ret['output'])
        except zmq.error.ZMQError, e:
            self.log_warn("ZMQError {0}".format(repr(e)))
            raise DeviceException("ZMQError {0}".format(repr(e)))

    def _get_mock_opt(self, mock):
        ret = True
        if self._host != '127.0.0.1' or (mock != 'y' and mock != 'yes'):
            ret = False
        return ret

    def _load_core_facts(self):
        self.log_info("loading core facts")
        facts_dir = "{0}/facts/".format(dirname(__file__))
        cf_re = re.compile('^core_[^\.]+.py$')
        cfs = [f.split(".")[0] for f in listdir(facts_dir) if isfile(join(facts_dir, f)) and cf_re.search(f)]
        for cf in cfs:
            self.log_info("fact file {0}".format(cf))
            try:
                f = __import__('pynetworking.facts.{0}'.format(cf))
                for comp in ('facts', cf, cf):
                    f = getattr(f, comp)
                self._facts = dict(self._facts.items() + f(self).items())
                self.log_info("core facts loaded \n{0}".format(pformat(self._facts)))
                if 'os' in self._facts:
                    break
            except:
                self.log_info("error executing core fact {0} ({1})".format(cf, sys.exc_info()[0]))
                self.log_debug(traceback.format_exc())
                self.close()
        else:
            if 'os' not in self._facts:
                self.close()
                raise DeviceException("device not supported")

    def _load_features(self):
        self.log_info("loading features")
        self._features = {}
        with open("{0}/Device.yaml".format(dirname(__file__)), 'r') as f:
            self._models = yaml.load(Template(f.read()).render(self._facts))
            self.log_debug("models {0}".format(self._models))
        if self._models is None:
            self.log_warn("no features loaded")
            self._models = {'features': {}}
        elif self._models['features'] is None:
            self.log_warn("no features loaded")
            self._models['features'] = {}
        for fname, fclass in self._models['features'].items():
            self.log_info("loading feature {0}/{1}".format(fname, fclass))
            try:
                m = __import__('pynetworking.features.{0}'.format(fclass))
                for comp in ('features', fclass, fclass):
                    m = getattr(m, comp)
                o = m(self)
                setattr(self, fname, o)
                self._features[fname] = o
            except:
                self.log_critical("Error loading class {1} for feature {0}".format(fname, fclass))
                raise

    def load_system(self):
        self.log_info("load system")
        self.log_debug("models {0}".format(self._models))
        if 'system' in self._models:
            try:
                self.log_info("loading system module {0}".format(self._models['system']))
                m = __import__('pynetworking.system.{0}'.format(self._models['system']))
                for comp in ('system', self._models['system'], self._models['system']):
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
        for fname, fobj in self._features.items():
            fobj.load_config(cfg)

    def log_debug(self, msg):
        self._logger(msg, 'debug')

    def log_info(self, msg):
        self._logger(msg, 'info')

    def log_warn(self, msg):
        self._logger(msg, 'warn')

    def log_error(self, msg):
        self._logger(msg, 'error')

    def log_critical(self, msg):
        self._logger(msg, 'critical')

    def _logger(self, msg, level):
        (frame, filename, lineno, function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[2]
        filename = filename.split('pynetworking/')[1]
        msg = '{0:30} [{1:3}] {2}'.format(filename, lineno, msg)
        log = logging.getLogger(self._host)
        if self._log_level != 0:
            getattr(log, level)(msg)

    def _start_proxy(self):
        self.log_debug("_start_proxy")
        if not isinstance(self._proxy, Process) or (isinstance(self._proxy, Process) and not self._proxy.is_alive()):
            self.log_info("creating proxy process {0} with zmq url {1}".format('cq-{0}'.format(self._host), self._proxy_url))
            self._proxy = Process(name='cq-{0}'.format(self._host), target=self._proxy_target, args=(self,))
            self._proxy.start()
            sleep(1)
            self.log_debug("proxy process started")

    def _open(self):
        self.cmd({'cmds': [{'cmd': '_status', 'prompt': ''}]})
        self._load_core_facts()
        self._load_features()
        self.load_system()

    def _mocked_open(self):
        # use 2 because is a second level nesting (test_...(dut, log_level) - open() - _mocked_open())
        frm = inspect.stack()[2]           # pragma: no cover
        mod = inspect.getmodule(frm[0])    # pragma: no cover
        feat = mod.__name__.split('_')[1]  # pragma: no cover
        os = mod.__name__.split('_')[-1]   # pragma: no cover
        if feat == os:                     # pragma: no cover
            os = 'awp'                     # pragma: no cover
        if os == 'coverage':               # pragma: no cover
            self._open()                   # pragma: no cover
            return                         # pragma: no cover

        yaml_load_mocked = MagicMock()                                                      # pragma: no cover
        load_facts_mocked = MagicMock()                                                     # pragma: no cover
        with patch('pynetworking.Device._load_core_facts', load_facts_mocked):              # pragma: no cover
            with patch('yaml.load', yaml_load_mocked):                                      # pragma: no cover
                yaml_load_mocked.return_value = self._mock_load_features(os=os, feat=feat)  # pragma: no cover
                load_facts_mocked.side_effect = self._mock_load_facts(os)                   # pragma: no cover
                self.cmd({'cmds': [{'cmd': '_status', 'prompt': ''}]})                      # pragma: no cover
                self._load_core_facts()                                                     # pragma: no cover
                self._load_features()                                                       # pragma: no cover
                self.load_system()                                                          # pragma: no cover

    def _mock_load_features(self, os, feat):
        if feat == 'device':                                                                                       # pragma: no cover
            return {'system': os + '_system', 'features': {'file': os + '_file', 'vlan': os + '_vlan'}}            # pragma: no cover
        if feat == 'license':                                                                                      # pragma: no cover
            return {'system': os + '_system', 'features': {'license': os + '_license', 'file': os + '_file'}}      # pragma: no cover
        if feat == 'ntp':                                                                                          # pragma: no cover
            return {'system': os + '_system', 'features': {'dns': os + '_dns', 'ntp': os + '_ntp'}}                # pragma: no cover
        if feat == 'vlan' and os == 'ats':                                                                         # pragma: no cover
            return {'system': os + '_system', 'features': {'interface': os + '_interface', 'vlan': os + '_vlan'}}  # pragma: no cover
        return {'system': os + '_system', 'features': {feat: os + '_' + feat}}                                     # pragma: no cover

    def _mock_load_facts(self, os):
        if (os == 'ats'):                                                                                                # pragma: no cover
            self._facts = {'model': u'AT-8000S/24', 'version': u'3.0.0.44', 'unit_number': u'1', 'os': 'ats',            # pragma: no cover
                           'serial_number': u'1122334455', 'boot version': u'1.0.1.07', 'hardware_rev': u'00.01.00'}     # pragma: no cover
            return                                                                                                       # pragma: no cover
        if (os == 'awp'):                                                                                                # pragma: no cover
            self._facts = {'build_date': u'Wed Sep 25 12:57:26 NZST 2013', 'version': u'5.4.2', 'sw_release': u'5.4.2',  # pragma: no cover
                           'build_name': u'x600-5.4.2-3.14.rel', 'os': 'awp', 'build_type': u'RELEASE'}                  # pragma: no cover
            return                                                                                                       # pragma: no cover
        self._facts = {}                                                                                                 # pragma: no cover
