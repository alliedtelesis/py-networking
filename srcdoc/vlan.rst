Vlan Feature
*****************
Vlan feature provides access to ethernet layer2 vlan of the device.


Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with specific vlan information

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the vlan information


Methods
-------

**add_interface**
"""""""""""""""""
**Mandatory**

**Description**: Add an interface to a vlan.

**delete_interface**
""""""""""""""""""""
**Mandatory**

**Description**: Remove an interface from a vlan.

**create**
""""""""""
**Mandatory**

**Description**: Create a vlan.

**delete**
""""""""""
**Mandatory**

**Description**: Delete a vlan.

**keys**
""""""""
**Mandatory**

**Description**: Return the list of available parameters.

**items**
"""""""""
**Mandatory**

**Description**: Select one of the available parameters.

**update**
""""""""""
**Mandatory**

**Description**: Update one of the writable parameters listed below by sending the 
corresponding CLI command to the device through the SSH connection opened.


Parameters
----------

mtu
""""
**Optional**

**ReadWrite**

**Type:** Integer

**Description**: Maximum transmit unit size in bytes.

**name**
""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: vlan name.

state
"""""
**Optional**

**ReadOnly**

**Type:** Boolean

**Description**: Enable if the vlan is enabled, disable if disabled.

**tagged**
""""""""""
**Mandatory**

**ReadOnly**

**Type:** List of Strings

**Description**: List of interfaces to which a tagged vlan is associated.

**type**
""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Supported type are:

- Static

- Dynamic

**untagged**
""""""""""""
**Mandatory**

**ReadOnly**

**Type:** List of Strings

**Description**: List of interfaces to which an untagged vlan is associated.
