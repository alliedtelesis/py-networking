Clock Feature
*************
This feature manages the clock settings.

Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary of the clock parameters.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the existing entries along with their parameters.


Methods
-------

**update(datetime=None, timezone=None)**
""""""""""""""""""""""""""""""""""""""""
**Mandatory**

**Description**:
Allow to set the clock and define the timezone.
Use *datetime* to set time and date.
Use *timezone* to set the timezone.
If *datetime* is not given, only the timezone is set.
If *timezone* is not given, only time and date are set.
Summertime rules are implicit in the *timezone* specified.

**Parameters**:

    - *datetime*: datetime.datetime
        Date and time informations.

    - *timezone*: datetime.tzinfo
        Timezone informations.


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

local_time
""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Local time in format dd mmm yyyy hh:mm:ss.

utc_time
""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: UTC time in format dd mmm yyyy hh:mm:ss.

timezone_name
"""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Timezone name.

timezone_offset
"""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Timezone offset to UTC in format +hh:mm.

summertime_zone
"""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Timezone name when the DST is on.

summertime_start
""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Date and time set as the start of summer time.

summertime_end
""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Date and time set as the end of summer time.

summertime_offset
"""""""""""""""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: Summer time offset in minutes.
