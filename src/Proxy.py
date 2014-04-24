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

class ProxyException(Exception):
    pass

def SSHProxy(device):
    device.log_info("starting SSHProxy on {0} for device {1}:{2}".format(device._proxy_url, device._host,device._port))
    context = zmq.Context()
    zmq_s = context.socket(zmq.REP)
    zmq_s.bind(device._proxy_url)
    if device._port=='auto':
        port = 22
    else:
        port = device._port

    while True:
        # getting command to execute
        cmd = json.loads(zmq_s.recv())
        device.log_debug("execute commands {0}".format(cmd))
        if 'cmds' not in cmd and 'cmd' not in cmd['cmds'][0]:
            device.log_warn("commands missing in zmq message")
            continue

        # connect to host
        try:
            device.log_debug("connecting to {0}:{1}".format(device.host,port))
            device_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            device_s.connect((device.host, port))
        except:
            device.log_debug("cannot connecting to {0}:{1} ({2})".format(device.host, port, sys.exc_info()[0]))
            ret={'status':'Error','output':'Cannot connect to host'}
            zmq_s.send_string(json.dumps(ret))
            continue

        # open a transport
        try:
            device.log_debug("opening transport to {0}:{1}".format(device.host,port))
            t = Transport(device_s)
            t.start_client()
        except SSHException:
            device.log_debug("cannot open an ssh  trasport to {0}:{1}".format(device.host,port))
            ret={'status':'Error','output':'Cannot connect ssh to host'}
            zmq_s.send_string(json.dumps(ret))
            continue

        # try to authenticate with username and password
        try:
            t.auth_password(device.username, device.password)
        except:
            device.log_debug("username/password authentication failed")

        # try in session authentication
        try:
            if not t.is_authenticated():
                t.auth_none(device.username)
                device.log_debug("none authentication succeed")
        except:
            device.log_debug("none authentication failed")
            ret={'status':'Error','output':'Cannot autenticate to the device'}
            zmq_s.send_string(json.dumps(ret))
            continue

        try:
            device.log_debug("getting a shell to the device")
            chan = t.open_session()
            chan.get_pty()
            chan.invoke_shell()
            chan.settimeout(5)
            sleep(1)
            if 'User Name:' in chan.recv(999):
                chan.send(device.username+'\n')
                sleep(1)
                if 'Password:' in chan.recv(999):
                    chan.send(device.password+'\n')
                _get_reply(device,chan)
            out=''
            ret={'status':'Error','output':'Unknown Error'}
            for c in cmd['cmds']:
               device.log_info("sending command '{0}' to device".format(c['cmd']))
               chan.send(c['cmd']+'\n')
               out += _get_reply(device, chan, c['prompt'])
            ret = {'status':'Success','output':out}
            chan.close()
        except SSHException:
            device.log_info("Connecting to {0}".format(host))
            conn.connect(device._host, port,device._username, device._password)
            ret = {'status':'Error','output':'SSHException'}
        except ProxyException:
            device.log_warn("ProxyException")
            ret = {'status':'Error','output':'ProxyException'}
        zmq_s.send_string(json.dumps(ret))
    return

def _get_reply(device, chan, prompt=''):
    if not prompt:
        prompt=r'[\n\r]{1}[\w\_]*[\>\#]{1}'
    try:
         device.log_debug("waiting for {0}".format(repr(prompt)))
         buff = ''
         while True:
             buff += chan.recv(999)
             device.log_debug("received >{0}<".format(buff))
             if re.search(prompt,buff):
                 device.log_debug("got prompt")
                 break
    except socket.timeout:
         device.log_warn("timeout waiting a reply or a prompt")
         raise ProxyException("Timeout")
    except:
         device.log_warn("exception waiting a reply or a prompt")
         raise ProxyException("")

    if re.search(prompt,buff):
        return '\n'.join(buff.split('\n')[1:-1])
    else:
         device.log_warn("Not seen any prompt")
         raise ProxyException("Not seen any prompt")
