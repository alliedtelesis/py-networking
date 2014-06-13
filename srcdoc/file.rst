File Feature
************
File feature permits to copy and delete files.
Files can be copied from the host on which PN is running to the device and vice versa.
Instead only files on the device can be deleted.


Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with specific file information.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the file information.


Methods
-------

**upload**
""""""""""
**Mandatory**

**Description**:
Copy a file from the host to the device.
If the file on device is already existing it can be overwritten.

**download**
""""""""""""
**Mandatory**

**Description**:
Copy a file from the device to the host.

**delete**
""""""""""
**Mandatory**

**Description**: Remove a file.

**keys**
""""""""
**Mandatory**

**Description**: Return the list of available parameters.

**items**
"""""""""
**Mandatory**

**Description**: Select one of the available parameters.


Parameters
----------

host_path
"""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: File path on the host.

device_path
"""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: File path on the device.

overwrite
"""""""""
**Mandatory**

**ReadWrite**

**Type:** Boolean

**Description**: If true, when uploading, the file on device is overwritten if already present.
