# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy, SSHException
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
    socket = context.socket(zmq.REP)
    socket.bind(device._proxy_url)
    conn = SSHClient()
    conn.set_missing_host_key_policy(AutoAddPolicy())
    if device._port=='auto':
        port = 22
    else:
        port = device._port
    conn.connect(device._host, port,device._username, device._password)
    while True:
        cmd = json.loads(socket.recv())
        device.log_debug("execute ommands {0}".format(cmd))
        if 'cmds' not in cmd and 'cmd' not in cmd['cmds'][0]:
            device.log_warn("Commands missing in zmq message")
            continue
        try:
            chan = conn.invoke_shell()
            chan.settimeout(5)
            chan.recv(999)
            ###################################################
            ## this should be moved in a device specific module
            chan.send("terminal length 0\n")
            _get_reply(device, chan, "terminal length 0\n")
            ###################################################
            out=''
            ret={'status':'Error','output':'Unknown Error'}
            for c in cmd['cmds']:
               device.log_info("sending command '{0}' to device".format(c['cmd']))
               chan.send(c['cmd']+'\n')
               out += _get_reply(device, chan, c['cmd'],c['prompt'])
            ret = {'status':'Success','output':out}
            chan.close()
        except SSHException:
            device.log_info("Connecting to {0}".format(host))
            conn.connect(device._host, port,device._username, device._password)
            ret = {'status':'Error','output':'SSHException'}
        except ProxyException:
            device.log_warn("ProxyException")
            ret = {'status':'Error','output':'ProxyException'}
        socket.send_string(json.dumps(ret))
    return

def _get_reply(device, chan, cmd, prompt=''):
    if not prompt:
        prompt=r'\n\w+[\>\#]{1}'
    try:
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
         device.log_warn("timeout waiting a reply or a prompt")
         raise ProxyException("Not seen any prompt")
