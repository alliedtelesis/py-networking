from pynetworking import Device, DeviceException
from pprint import pprint
import re

def core_ats(dev):
    dev.log_info("core_ats")
    ret = {}

    out = dev.cmd({'cmds':[{'cmd': 'show version', 'prompt':'\#'}]})

    dev.log_debug("show version\n{0}".format(out))

    #
    #       Unit             SW version         Boot version         HW version      
    #------------------- ------------------- ------------------- ------------------- 
    #        1               3.0.0.44            1.0.1.07            00.01.00 

    m = re.search("Unit\s+SW\sversion\s+Boot\sversion\s+HW\sversion\s*\n[^\n]+\n\s+(?P<unit>\d)\s+(?P<version>[\d\.]+)\s+(?P<boot_version>[\d\.]+)\s+(?P<hardware_rev>[\d\.]+)", out)

    if m:
        ret['os'] = 'ats'
        ret['version'] = m.group('version')
        ret['boot version'] = m.group('boot_version')
        ret['hardware_rev'] = m.group('hardware_rev')
    else:
        return ret

    dev.sw_version = ret['version']
    dev.boot_version = ret['boot version']

    out = dev.cmd({'cmds':[{'cmd': 'show system', 'prompt':'\#'}]})
    dev.log_debug("show system\n{0}".format(out))

    #
    #Unit        Type         
    #---- ------------------- 
    # 1     AT-8000S/24       
    #
    #
    #Unit     Up time     
    #---- --------------- 
    # 1     00,04:56:34   
    #
    #Unit Number:   1
    #Serial number:  

    m = re.search("\nUnit\s+Type\s*\n[^\n]+\n\s+\d\s+(?P<model>[^\s]+)\s*\n", out)
    if m:
        ret['model'] = m.group('model')
        dev.model = ret['model']
    else:
        ret['model'] = 'not found'
        dev.log_warn("cannot capture model")
    
    m = re.search("\nUnit\s+Number:\s+(?P<unit_number>[^\s]+)\s*\n", out)
    if m:
        ret['unit_number'] = m.group('unit_number')
    else:
        ret['unit_number'] = 'not found'
        dev.log_warn("cannot capture unit number")

    m = re.search("\nSerial\s+Number:\s+(?P<unit_number>[^\s]*)\s*\n", out)
    if m:
        ret['serial_number'] = m.group('serial_number')
    else:
        ret['serial_number'] = 'not found'
        dev.log_warn("cannot capture serial number")

    return ret

