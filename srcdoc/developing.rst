Developing Py-Networking
************************

Develop
-------
Adding a test is easy.
Add a function named test_xxx() to one of the already present modules and follow the guidelines of the already existing functions.
The previous chapters also explain how to use the facts and the features offered and how to write new ones if required.

Debug
-----
Developing PN requires that, at a certain point, all the tests you added have to be tried out.
In this case, a tool named 'tox' can help us.
Tox is able to manage virtual environments and automatize test activities.
Check whether you have it or not by typing::

    tox -h

If you do not have it, install it by typing::

    pip install tox

Now tox can execute all the test functions test_xxx() encoded in PN.
You can execute all the test suite, only the tests in a module, only the one you added.
You can specify on which networking device execute it and enable a log too.
Just type::

    tox [py module] [py test function] [--] [--dut-host=<IP address>] [--log=<log level>]

Each test can perform basic operations either on an emulated environment or on a real device.
Let's focus on the first option for now.
Type::

    tox

and all the suite will be executed locally in every available virtual environment.
Each successful test produces a script like this:

    tests/test_interface.py:192: test_description PASSED

while otherwise an exception is raised.
In the latter case, python shows exactly in which part of the software the test failed.
Let's switch to the real device option now.
Type::

    tox -- -dut-host=<IP address>

and the suite should be executed on the device having that address.
The word 'should' could not be more appropriate, given that two conditions have to be met::

    - existing host:
        The host device must answer to a ping solicitation to prove it is existing.

    - SSH connection enabled:
        The host device must be reachable through SSH.

The first condition is automatically checked by PN, that opens a ping session toward the host.
The second condition is explained in details in the introduction section, where it is described how to overcome all the related issues.
Once these two conditions are met, the test functions can be invoked as requested.
