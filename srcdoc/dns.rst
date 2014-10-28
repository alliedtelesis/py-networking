DNS Feature
***********
This feature allows to define the available name servers and to provide a domain name.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the DNS parameters.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing entries along with their parameters.


Methods
-------

**create(name_servers=None,default_domain=None)**
"""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Add name servers and/or the default domain name.
At least one parameter is mandatory.

**Parameters**:

    - *name_servers*: list of strings
        List of name server IP addresses
        
    - *default_domain*: string
        Default domain name
        

**read(hostname)**
""""""""""""""""""
**Mandatory**

**Description**:
Return the list of IP addresses matching a hostname.
It implements the DNS lookup functionality.

**Parameters**:

    - *hostname*: string
        Hostname
      
        
**delete(name_servers=None,default_domain=None)**
"""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Remove name servers and/or the default domain name.
At least one parameter is mandatory.

**Parameters**:

    - *name_servers*: list of strings
        List of name server IP addresses
        
    - *default_domain*: string
        Default domain name


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

name_servers
""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Comma separated list of name server IP addresses.

default_domain
""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Default domain name.

