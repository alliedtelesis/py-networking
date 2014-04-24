from pynetworking import Device, DeviceOfflineException
from pprint import pprint
import re

def core_awp(dev):
    ret = {}
    cmds = {'cmds':[{'cmd': 'terminal length 0', 'prompt':'\n\w+\>'},
                    {'cmd': 'show version',      'prompt':'\n\w+\>'},
                   ]}
    try:
        out = dev.cmd(cmds)
    except DeviceOfflineException:
        return ret

    # AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26
    m = re.search('\s+AlliedWare Plus \(TM\)\s+([\d\.]+)\s+',out) 
    if m:
        ret['os'] = 'awp'
        ret['version'] = m.group(1)
    else:
        return ret

    # Build name : x600-5.4.2-3.14.rel
    m = re.search("Build\s+name\s+:\s+([^\r\n\s]+)",out)
    if m:
        ret['build_name'] = m.group(1)

    # Build date : Wed Sep 25 12:57:26 NZST 2013
    m = re.search('Build\s+date\s+:\s+([^\n\r]+)',out)
    if m:
        ret['build_date'] = m.group(1)

    # Build type : RELEASE
    m = re.search('Build\s+type\s+:\s+([^\r\n\s]+)',out)
    if m:
        ret['build_type'] = m.group(1)

    cmds = {'cmds':[{'cmd': 'terminal length 0', 'prompt':'\n\w+\>'},
                    {'cmd': 'show system',       'prompt':'\n\w+\>'},
                   ]}
    out = dev.cmd(cmds)

    m = re.search('\s+Board\s+ID\s+Bay[\w\s\-]+Base\s+\d+\s+([\w\-\/]+)\s+([\w\-\/]+)\s+([\w\-\/]+)\s+',out)
    if m:
        ret['model'] = m.group(1)
        ret['hardware_rev'] = m.group(2)
        ret['serial_number'] = m.group(3)

    return ret
