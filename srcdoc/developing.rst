Developing Py-Networking
************************

Develop
-------
First of all, be sure to have python and PN installed and have cloned the PN repository.
Create your develop environment by typing::

    setup.py test

Two main directories are present: src and tests.
The first contains the PN library source files, the second a sequence of tests using PN.
You can either add new functionalities in src or new tests; just follow the guidelines of the already existing software.
The previous chapters also explain how to use the facts and the features offered and how to write new ones if required.

Debug
-----
Developing PN requires that, at a certain point, all the functionality and test you added have to be tried out.
In this case, a tool named 'tox' can help us.
Tox is able to manage virtual environments and automatize test activities.
The setup utility installs it automatically, but in any case check whether you have it or not::

    tox -h

If you do not have it, install it by typing::

    pip install tox

Now you can execute all the test suite, only the tests in a file, only the one you added.
You can specify on which networking device executing it and enable a log too.
Type::

    tox [-e venv] [test file] [--] [-k test function] [--dut-host=<IP address>] [--log=<log level>]

where::

    venv: virtual environment in which the test runs
    test file: the file containing the test functions to be tested
    test function: the test function to be tested
    dut-host: device IP address (if any)
    log: log level (debug, info, warning, error, critical)
    
Every test can perform basic operations either on an emulated environment or on a real device.
Let's focus on the first option for now.
Type::

    tox

and all the suite will be executed locally in every available virtual environment.
Each successful test produces a script like this:

    tests/test_interface.py:192: test_description PASSED

while otherwise an exception is raised.
In the latter case, python shows exactly in which part of the software the test failed, so that you can debug it.
Let's switch to the real device option now.
Type::

    tox -- -dut-host=<IP address>

and the suite should be executed on the device having that address.
The word 'should' could not be more appropriate, given that two conditions have to be met::

    - existing host:
        The host device must answer to a ping solicitation to prove it is existing.

    - SSH connection enabled:
        The host device must be reachable through SSH.

The first condition is automatically checked by opening a ping session toward the given device.
The second condition is explained in details in the introduction section, where it is described too how to overcome all the related issues.
Once these two conditions are met, the test functions can be invoked as requested.

.. note::

    During your test session, something could go wrong.
    It could be that the test is blocked indefinitely, or you want to start again just because you forgot something.
    Anyway, all you need is quitting immediately the test session.
    In this case::

        - type 'ctrl + c' to stop the execution and have the prompt back
        - type 'ps|grep python' to detect the running python processess
        - kill them with: kill -9 <PID>

    and start again.
    Be sure always to have removed all the running python processes before starting new tests, otherwise they could clash and give problems.
    