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

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ProxyException(Exception):
    pass

def SSHProxy(url, host, port, username, password):
    log.debug("Starting SSHProxy for {0}:{1} on {2}".format(url, host,port))
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(url)
    conn = SSHClient()
    conn.set_missing_host_key_policy(AutoAddPolicy())
    if port=='auto':
        port = 22
    conn.connect(host, port,username, password)
    while True:
        cmd = json.loads(socket.recv())
        log.debug("Commands {0}".format(cmd))
        if 'cmds' not in cmd and 'cmd' not in cmd['cmds'][0]:
            log.debug("Commands missing")
            continue
        try:
            chan = conn.invoke_shell()
            chan.settimeout(5)
            chan.recv(999)
            ###################################################
            ## this should be moved in a device specific module
            chan.send("terminal length 0\n")
            _get_reply(chan, "terminal length 0\n")
            ###################################################
            out=''
            ret={'status':'Error','output':'Unknown Error'}
            for c in cmd['cmds']:
               log.debug("Sending command '{0}'".format(c['cmd']))
               chan.send(c['cmd']+'\n')
               out += _get_reply(chan, c['cmd'],c['prompt'])
            ret = {'status':'Success','output':out}
            chan.close()
        except SSHException:
            log.debug("Connecting to {0}".format(host))
            conn.connect(host, port,username, password)
            ret = {'status':'Error','output':'SSHException'}
        except ProxyException:
            log.debug("ProxyException")
            ret = {'status':'Error','output':'ProxyException'}
        socket.send_string(json.dumps(ret))
    return

def _get_reply(chan, cmd, prompt=''):
    if not prompt:
        prompt=r'\n\w+[\>\#]{1}'
    try:
         buff = ''
         while True:
             buff += chan.recv(999)
             log.debug("Buffer >{0}<".format(buff))
             if re.search(prompt,buff):
                 log.debug("Got prompt")
                 break
    except socket.timeout:
         log.debug("Timeout")
         raise ProxyException("Timeout")
    except:
         raise ProxyException("")

    if re.search(prompt,buff):
        return '\n'.join(buff.split('\n')[1:-1])
    else:
         raise ProxyException("Not seen any prompt")
