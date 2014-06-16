File Feature
************
File feature manages files on the device.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the file parameters using its name as index.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing files along with their parameters.


Methods
-------

**create(name, text=None, filename=None)**
""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Create a new file on the device.
The file content can either come from a file or a string.
If neither the file nor the string is given, the file will be empty.
The *text* and *filename* parameters are alternative and if both are given an exception
will be risen. 

**Parameters**:

    - *name*: string
        Name of the file on the device that will be created

    - *text*: string
        String bearing the content of the file to be created

    - *filename*: string
        Path and name of the file where the content will be taken from

**update(name, new_name=None, text=None, filename=None)**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Changes an existing file on the device.
The *text* and *filename* parameters are alternative and if both are given an exception
will be risen.
An exception will also be risen if a *new_name* file already exists.

**Parameters**:

    - *name*: string
        Name of the file on the device that will be updated

    - *new_name*: string
        The new name of the file on the device

    - *text*: string
        String bearing the new content of the file

    - *filename*: string
        Path and name of the file where the new content will be taken from

**delete**
""""""""""
**Mandatory**

**Description**:
Remove a file on the device.

**Parameters**:

    - *name*: string
        Name of the file to be removed.

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

size
""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: File size in bytes.

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
