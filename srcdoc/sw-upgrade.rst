Software upgrade feature
************************
This feature allows the running image upgrade.

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

**create(name, server=None, filename=None)**
""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Create a new image on the device.
The *server* parameter is the address of the host where the server is running.
If not given it's the library host one.
The *filename* parameter is the image name on the device.
If not given it's *name*.

**Parameters**:

    - *name*: string
        Image name

    - *server*: string
        Server IP address

    - *filename*: string
        New image name on the device

**update(name, server=None, filename=None)**
""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Update an existing image on the device.
The *server* parameter is the address of the host where the server is running.
If not given it's the library host one.
The *filename* parameter is the image name on the server.
If not given it's *name*.

**Parameters**:

    - *name*: string
        Image name

    - *server*: string
        Server IP address

    - *filename*: string
        New image name on the device

**delete**
""""""""""
**Mandatory**

**Description**:
Remove an existing image on the device.

**Parameters**:

    - *name*: string
        Name of the image to be removed.

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

boot
""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: True if current boot image.

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
