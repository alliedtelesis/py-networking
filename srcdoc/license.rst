Software licensing feature
**************************
This feature allows to manage both feature and release licenses.


Operations
----------

**[String]**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with specific license information.

**(String)**
""""""""""""
**Mandatory**

**Description**: Return a dictionary with all the license information.


Methods
-------

**set_license(label=None, key=None, certificate=None)**
"""""""""""""""""""""""""""""""""""""""""""""""""""""""
**Mandatory**
	
**Description**: Set a license.
Either a label and key pair or a reference to a certificate file must be provided.

**Parameters**:

    - *label*: string
        License name.

    - *key*: string
        Encrypted license key.

    - *url*: string
        Certificate file name or url.

**delete(label)**
"""""""""""""""""
**Mandatory**

**Description**: Deactivate a license.

**Parameters**:

    - *label*: string
        License name.

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

license
"""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Feature or release license name.

customer
""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Customer name.

quantity
""""""""
**Mandatory**

**ReadOnly**

**Type:** Integer

**Description**: Quantity of licenses.

type
""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: License type (full or trial).

issue_date
""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Date the license was generated.

expire_date
"""""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Expiry date for trial licenses.

features
""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: List of software features in case of feature license.

releases
""""""""
**Mandatory**

**ReadOnly**

**Type:** String

**Description**: Software version supported in case of release license.
