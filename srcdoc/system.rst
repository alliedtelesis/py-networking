.. _system-section:

System
******
System class implements device dependent functions and it's used by the Device class to do device specific
operations. This chapter is not intended for the library user but for developer that want to add support for new devices.

Methods
-------

**get_config**
""""""""""""""
**Mandatory**

**Description**: Returns a string representing the full device configuration.

**ping**
""""""""""""""
**Mandatory**

**Description**: Returns True if the device is online.

**save_config**
"""""""""""""""
**Mandatory**

**Description**: Allows to save the running configuration in the flash memory, so to survive in case of reboot.

**shell_init**
""""""""""""""
**Optional**

**Description**: Returns a list of dictionaries representing the commands that need to be executed on the device when a
shell is opened. For example the command output pagination should be disable to avoid that commands that generate long
output stop waiting user input.

**shell_prompt**
""""""""""""""""
**Optional**

**Description**: Returns a regular expression for the default prompt of the device.

**update(name, port=None, server=None)**
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**: Allows to upgrade the device software.
The *name* parameter is the software name.
It cannot be the current running software.
The *port* parameter is the port used to upload the software on the device (if required).
The *server* parameter is the address of the host where the server is running.
If not given it's the library host one.
Once the upload has terminated, the device is rebooted and the new software will be running.

**Parameters**:

    - *name*: string
        Software release name

    - *port*: integer
        Upload port

    - *server*: string
        Server IP address

