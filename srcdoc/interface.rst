Interface Feature
*****************
Interface feature provide access to all physical and virtual network interface of the device.

Interface Naming Convention
---------------------------
Since there isn't a common industry standard to name interfaces, PN define a flexible convention that should be mapped by
the individual implementation of this module to the actual device.

Each interface is identified by three digits separated by dots, for example *1.2.10*

The first digit identify the physical units within a set of devices, for example connected with a stacking technology,
but seen from the library throughout a single IP address or hostname.
The second digit represent the slot within the physical device. The digit **0** identify interfaces that belong to the
main board and are not on a separated card.
The last digit is a number uniquely identify the interface on the main board or card.


Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with specific interface information

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the interfaces information


Methods
-------

**update**
""""""""""
**Mandatory**

**Description**: *TBD*

**items**
"""""""""
**Mandatory**

**Description**: *TBD*

**keys**
""""""""
**Mandatory**

**Description**: *TBD*


Parameters
----------

**configured_duplex**
"""""""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**configured_polarity**
"""""""""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**configured_speed**
""""""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**current_duplex**
""""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**current_polarity**
""""""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**current_speed**
"""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: *TBD*

**description**
"""""""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: A description string for the the interface

**enable**
""""""""""
**Mandatory**

**ReadWrite**

**Type:** Boolean

**Description**: True means that the interface is enabled

**hardware**
""""""""""""
**Mandatory**

**ReadWrite**

**Type:** String

**Description**: The interface hardware that is make the interface

Supported hardware are:

- Ethernet

- Vlan

**link**
""""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: True means that the interface is up or running state
