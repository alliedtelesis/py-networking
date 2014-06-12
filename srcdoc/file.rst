File Feature
************
File feature permits to copy and delete files.


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

**copy**
""""""""
**Mandatory**

**Description**:
Copy a file:

- from a remote host source to the device.

- from the device to a remote host destination.

In the first case, if the file on device is already existing it will be overwritten.
The protocol used for file transfer must be specified.
In case the protocol is not supported the file won't be copied.

**dir**
"""""""
**Mandatory**

**Description**: List the current available files.

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

source IP address
"""""""""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: IP address where the source file is stored. If the file is on the device the IP address is 'localhost'.

destination IP address
""""""""""""""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: IP address where the source file will be copied. If the file is on the device the IP address is 'localhost'.

source path
"""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: Path of the file to be copied.

destination path
""""""""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: Path where the file will be copied.

protocol
""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: Protocol used for file transfer.
