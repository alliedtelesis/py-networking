Getting Started
###############

What is Py-Networking?
----------------------

Py-Networking (PN) is a python library that provides a new way to interact and configure your networking devices.
PN abstracts the physical device and provides to the user an uniform API that does not depend on the specific device configuration or configuration syntax.
PN does not emulate features that device maybe missing but if two different devices implement a specific feature, this is exposed to the user in the same way.

Notice
------
Py-Networking is at early stages of development. You are free to look around but we do not provide support at the moment
and the library can go throughout a significant changes and backward compatibility cannot be guaranteed.

Install
-------
Installation of Py-Networking can be done from pypi repository (recommended method) or from source code.

Assuming that your system has python and pip command installed::

    pip install py-networking

Pypi repository contains the latest stable version so if you want to work with a newer version and or want to do development
on the library you need to install from source.

Assuming you have python and git command installed::

    git clone https://github.com/alliedtelesis/py-networking.git
    cd py-networking
    python setup.py install

For further information on how to develop and contribute to py-networking refer to Developing Py-Networking chapter.

.. note::

    On Mac OS X follow the following steps before invoking pip

    Check if gcc is already installed.
    If trying to run gcc on the terminal you get the following output::

        $ gcc
        clang: error: no input files

    gcc is already installed. Otherwise you will have a dialog box asking you if you want to **Get Xcode** or **Install**.

    **PRESS INSTALL and not Get Xcode unless you want to install the full development environment**

    Install Homebrew::

        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/mxcl/homebrew/go)"

    and then::

        brew install python
        brew install zmq


Run
---
Now that you have python and you have downloaded PN, you can use it.
Write your python script using the available test functions exported by the library and try it out on your networking device, so to interact with it and configure it properly.
At this time, things could not be working as expected, in spite the device is connected to your network and the board software is perfectly running.
What is going wrong?

The answer is clear.
The device must be reachable through SSH protocol.
Indeed a SSH session toward the device is opened by PN and all the interaction and configuration commands are sent through it.
Unfortunately, this is not always possible; some devices, if not all, have SSH disabled as default.
Therefore a previous step is necessary: connect manually the board through telnet, that is always enabled, and enable SSH protocol.
On AW+ devices, once logged in type::

    enable
    configure terminal
    service ssh ip
    
and on ATS ones instead::

    configure
    ip ssh server
        
Once sure that SSH connection is enabled, your script can be executed correctly.

Communication between PN and the device is guaranteed by a proxy process, that creates an SSH link between them and manage it.
CLI commands are sent to the device through it and CLI output is returned if any.
Next evolutions of PN will overcome the above explained problem by enabling the SSH session automatically if necessary.

Now that your script can run as expected, two things can occur: either the test function is successful or it fails. 
Each successful test produces a print like this:

    tests/test_interface.py:192: test_description PASSED

while otherwise an exception is raised.
In the latter case, python shows exactly in which part of the software the test has failed.


License
-------
Apache 2.0


