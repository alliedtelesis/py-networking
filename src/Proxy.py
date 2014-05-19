# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy, SSHException, Transport
from pprint import pprint
import yaml
import re
import logging
import sys
import socket
from os import listdir
from os.path import dirname, isfile, join
from multiprocessing import Process
from time import sleep
import zmq
import json
from pynetworking.utils import Cache, CacheMissException

class ProxyException(Exception):
    pass

def SSHProxy(device):
    device.log_info("starting SSHProxy on {0} for device {1}:{2}".format(device._proxy_url, device._host,device._port))
    context = zmq.Context()
    zmq_s = context.socket(zmq.REP)
    zmq_s.bind(device._proxy_url)
    zmq_p = zmq.Poller()
    zmq_p.register(zmq_s, zmq.POLLIN)
    cache = Cache()
    if device._port=='auto':
        port = 22
    else:
        port = device._port

    # connect to host
    try:
        device.log_info("connecting to {0}:{1}".format(device.host, port))
        device_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        device_s.connect((device.host, port))
    except:
        device.log_warn("cannot connecting to {0}:{1} ({2})".format(device.host, port, sys.exc_info()[0]))
        ret = {'status': 'Error', 'output': 'Cannot connect to host'}
        exit(1)

    # open a transport
    try:
        device.log_debug("opening transport to {0}:{1}".format(device.host, port))
        t = Transport(device_s)
        t.start_client()
    except SSHException:
        device.log_warn("cannot open an ssh  trasport to {0}:{1}".format(device.host, port))
        ret = {'status': 'Error', 'output': 'Cannot connect ssh to host'}
        exit(1)

        # try to authenticate with username and password
    try:
        t.auth_password(device.username, device.password)
    except:
        device.log_debug("username/password authentication failed...trying in session auth")

    # try in session authentication
    if not t.is_authenticated():
        try:
            t.auth_none(device.username)
            device.log_debug("none authentication succeed")
        except:
            device.log_warn("authentication failed")
            ret = {'status': 'Error', 'output': 'Cannot authenticate to the device'}
            exit(1)

    try:
        device.log_debug("getting a shell to the device")
        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()
        chan.settimeout(5)
        sleep(1)
        if 'User Name:' in chan.recv(999):
            chan.send(device.username + '\n')
            sleep(1)
            if 'Password:' in chan.recv(999):
                chan.send(device.password + '\n')
            _get_reply(device, chan,r'\n[\w\_]+\#')
    except SSHException:
        device.log_warn("SSHException")
        ret = {'status':'Error','output':'SSHException'}
        exit(1)
    except ProxyException:
        device.log_warn("ProxyException")
        ret = {'status':'Error','output':'ProxyException'}
        exit(1)

    device.log_info("ready to accept commands")
    while True:
        # getting command to execute
        if len(zmq_p.poll(device._proxy_connection_timeout)) == 0:
             device.log_info("shutting down proxy")
             chan.close()
             exit(0)

        cmd = json.loads(zmq_s.recv(zmq.NOBLOCK))
        device.log_debug("execute commands {0}".format(cmd))

        if 'cmds' not in cmd and 'cmd' not in cmd['cmds'][0]:
            device.log_warn("commands missing in zmq message")
            ret = {'status':'Error','output':'missing cmd'}
            zmq_s.send_string(json.dumps(ret))
            continue

        if 'cmd' in cmd['cmds'][0] and cmd['cmds'][0]['cmd'].startswith('_'):
            pcmd = cmd['cmds'][0]['cmd']
            device.log_debug("executing internal command {0}".format(pcmd))
            if pcmd == '_exit':
                device.log_info("shutting down proxy")
                chan.close()
                ret = {'status':'Success','output':'shutting down proxy'}
                zmq_s.send_string(json.dumps(ret))
                exit(0)
            elif pcmd == '_ping':
                device.log_info("ping proxy")
                ret = {'status':'Success','output':'pong'}
            else:
                device.log_warn("unknown internal command {0}".format(pcmd))
                ret = {'status':'Error','output':'unknown command {0}'.format(pcmd)}
        else:
            try:
                out=''
                ret={'status':'Error','output':'Unknown Error'}
                for c in cmd['cmds']:
                    device.log_info("sending command '{0}' to device".format(c['cmd']))
                    try:
                        if device.system.enter_config(c['cmd']):
                            cache.invalidate()
                            device.log_debug("cache invalidated")
                    except AttributeError:
                        device.log_warn("device configuration without system object")

                    try:
                        if not cmd['cache']:
                            device.log_debug("cache disabled")
                            raise CacheMissException
                        co = cache.get(c['cmd'])
                        device.log_debug("cache hit")
                    except CacheMissException:
                        device.log_debug("cache miss")
                        chan.send(c['cmd']+'\n')
                        co = _get_reply(device, chan, c['prompt'])
                    out += co
                ret = {'status':'Success','output':out}
            except ProxyException:
                device.log_warn("ProxyException")
                ret = {'status':'Error','output':'ProxyException'}
        zmq_s.send_string(json.dumps(ret))

def _get_reply(device, chan, prompt=''):
    if prompt == '':
        return
    prompt = '[\n\r]\w*' + prompt
    try:
         device.log_debug("waiting for {0}".format(repr(prompt)))
         buff = ''
         while True:
             buff += chan.recv(999)
             if re.search(prompt,buff):
                 device.log_debug("got prompt")
                 break
    except socket.timeout:
        device.log_debug("received >{0}<".format(buff))
        device.log_warn("timeout waiting a reply or a prompt")
        raise ProxyException("Timeout")
    except:
        device.log_debug("received >{0}<".format(buff))
        device.log_warn("exception waiting a reply or a prompt")
        raise ProxyException("")

    if re.search(prompt,buff):
        return '\n'.join(buff.split('\n')[1:-1])
    else:
        device.log_debug("received >{0}<".format(buff))
        device.log_warn("Not seen any prompt")
        raise ProxyException("Not seen any prompt")
