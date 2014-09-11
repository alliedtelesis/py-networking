MAC Feature
***********
This feature manages the static and dynamic entries of the device MAC address table.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the specific MAC information.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing MACs along with their parameters.


Methods
-------

**create(mac, interface, forward=True, vlan=1)**
""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Create a static entry in the MAC address table.
If *forward* is True, any incoming frame having *mac* as destination will be forwarded to the given *interface*.
If *forward* is False, any incoming frame having *mac* as source received from *interface* will be discarded.

**Parameters**:

    - *mac*: string
        MAC address in the forms 1234.1234.1234, 123412341234, 12:34:12:34:12:34, 12-34-12-34-12-34
        
    - *interface*: string
        Source or destination interface
        
    - *forward*: boolean
        Forward frames if True, discard them if False

    - *vlan*: integer
        Id of the VLAN to whom the MAC belongs to 

**update(mac, interface, forward=True, vlan=1)**
""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Update a static entry in the MAC address table.

**Parameters**:

    - *mac*: string
        MAC address in the form 1234.1234.1234, 123412341234, 12:34:12:34:12:34, 12-34-12-34-12-34

    - *interface*: string
        Source or destination interface

    - *forward*: boolean
        Forward frames if True, discard them if False

    - *vlan*: integer
        Id of the VLAN to whom the MAC belongs to

**delete(mac=None)**
""""""""""""""""""""
**Mandatory**

**Description**:
Remove an entry in the MAC address table.
If no entry is specified, the MAC address table will be cleaned.

**Parameters**:

    - *mac*: string
        MAC address in the form 1234.1234.1234, 123412341234, 12:34:12:34:12:34, 12-34-12-34-12-34

**keys**
""""""""
**Mandatory**

**Description**: Return the list of the available parameters.

**items**
"""""""""
**Mandatory**

**Description**: Select one of the available parameters.


Parameters
----------

interface
"""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Interface name.

forward
"""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: Forward if True, discard if False.

static
""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: Static entry if True, dynamic if False.

vlan
""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: VLAN id
