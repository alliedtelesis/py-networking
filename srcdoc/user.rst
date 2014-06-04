User Feature
************
User feature permits to add and remove user accounts and change user password and privilege level.


Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with specific user account information.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the user account information.


Methods
-------

**create**
""""""""""
**Mandatory**

**Description**: Create an user account.

**delete**
""""""""""
**Mandatory**

**Description**: Remove an user account.

**update**
""""""""""
**Mandatory**

**Description**: Update one of the writable parameters listed below by sending the corresponding CLI command to the device through the SSH connection opened.

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

password
""""""""
**Optional**

**ReadWrite**

**Type:** String

**Description**: User password.

encrypted
"""""""""
**Optional**

**ReadWrite**

**Type:** Boolean

**Description**: True if the password is encrypted, false if it is in clear text.

privilege_level
"""""""""""""""
**Optional**

**ReadWrite**

**Type:** Integer

**Description**: User privilege level.

