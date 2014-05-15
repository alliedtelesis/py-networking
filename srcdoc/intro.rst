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
Now that you have PN installed, you can use it.
Here is an example of python script using the PN library::

    from pynetworking import Device

        d=Device('<your device IP address>')
        d.open()
        print(d.facts)
        d.close()
 
Save it in 'myscript.py' and run it::

    python myscript.py

An output like this will be produced::

    {'boot version': u'1.0.1.07', 'model': u'AT-8000S/24', 'version': u'3.0.0.44', 'serial_number': '123456789', 'hardware_rev': u'00.01.00', 'os': 'ats', 'unit_number': u'1'}

Alternatively you can run python and execute each command separately in the python shell.
The final result is the same::

    (your_virtual_env)user:your_virtual_env name.surname$ python
    Python 2.7.6 (default, Apr  9 2014, 11:48:52) 
    [GCC 4.2.1 Compatible Apple LLVM 5.1 (clang-503.0.38)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pynetworking import Device
    >>> d=Device('<your device address>')
    >>> d.open()
    >>> print(d.facts)
    {'boot version': u'1.0.1.07', 'model': u'AT-8000S/24', 'version': u'3.0.0.44', 'serial_number': 'not found', 'hardware_rev': u'00.01.00', 'os': 'ats', 'unit_number': u'1'}
    >>> d.close()

In spite all, things could not be working good as explained above.
Strange to say, the device is connected to your network and the board software is perfectly running.
What is going wrong?

The answer is: the device must be reachable through SSH protocol.
Indeed the communication toward the device is managed by a proxy process creating an SSH protocol session.
This permits to send CLI commands to the device and to receive CLI output if any.
Unfortunately, this is not always possible; some devices, if not all, have SSH disabled as default.
Therefore a previous step is necessary: connect manually the device through telnet, that is always enabled, and enable SSH protocol.

.. note::

    On AW+ devices, once logged in, type::

        enable
        configure terminal
        service ssh ip
        exit
        write
    
    On ATS devices instead type::

        configure
        ip ssh server
        exit
        copy running-config startup-config

Once sure that SSH connection is enabled, your script can be executed correctly.
Next evolutions of PN will overcome the above explained problem by enabling the SSH session automatically when necessary.


License
-------
Apache 2.0


