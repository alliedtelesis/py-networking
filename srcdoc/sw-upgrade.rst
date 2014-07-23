Software upgrade feature
************************
This feature allows to upgrade the device software.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the software parameters using its name as index.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing software along with their parameters.


Methods
-------

**update(name, port, server=None)**
""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
It allows to upload a new software release on the device.
The *name* parameter is the software name.
It cannot be the current running software.
The *port* parameter is the port used for the upload.
The *server* parameter is the address of the host where the server is running.
If not given it's the library host one.
Once the upload has terminated, the device is rebooted and the new software will be run.

**Parameters**:

    - *name*: string
        Software release name

    - *port*: integer
        Upload port

    - *server*: string
        Server IP address

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

active
""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: True if current running image.

nextboot
""""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: True if image will be running at reboot.

version
"""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Image software release.

size
""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: Image size in bytes.

mdate
"""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Last modification date.

mtime
"""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Last modification time.
