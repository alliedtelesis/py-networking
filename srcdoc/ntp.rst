NTP
***
This feature allows to configure one or more NTP servers that the device will use to synchronize with.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the server parameters using its name as index.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing entries along with their parameters.


Methods
-------

**create(address, poll=60)**
""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Add a NTP server.
The device will try to synchronize to it every *poll* seconds.
If *poll* is not specified, its value defaults to 60 seconds.

**Parameters**:

    - *address*: string
        Server ip address or hostname

    - *poll*: integer
        Polling time in seconds
        

**update(address, poll=60)**
""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Update the polling time.
If *poll* is not specified, its value defaults to 60 seconds.

**Parameters**:

    - *address*: string
        Server ip address or hostname

    - *poll*: integer
        Polling time in seconds
      
        
**delete(address=None)**
""""""""""""""""""""""""
**Mandatory**

**Description**:
Remove an NTP server.
The device will not try to synchronize to that server anymore.
If no address is specified, all the NTP servers are removed.

**Parameters**:

    - *address*: string
        Server IP address or hostname


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

polltime
""""""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: Polling time in seconds.

status
""""""
**Mandatory**

**ReadOnly**

**Type:** Boolean

**Description**: True if the device is synchronized, False otherwise.
