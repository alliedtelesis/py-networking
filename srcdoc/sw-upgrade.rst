Software upgrade feature
************************
This feature allows to upgrade the device software (image).

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the image parameters using its name as index.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing images along with their parameters.


Methods
-------

**update(name, release)**
""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
It allows the software upgrade.
The *server* parameter is the address of the host where the server is running.
If not given it's the library host one.
The *release* parameter is the image name on the device.
It cannot be the current running image name.
Once the upload has terminated, the device is rebooted and the new image will be run.

**Parameters**:

    - *release*: string
        Image name

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

content
"""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Image content.
