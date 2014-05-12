Getting Started
###############

What is Py-Networking?
----------------------

Py-Networking (PN) is a python library that provides a new way to interact and configure your networking devices.
PN abstract the physical device and provides to the user an uniform API that does not depends from the specific device configuration or configuration syntax.
PN does not emulate features that device maybe missing but if two different devices implement a specific feature, this is exposed to the user in the same way.

Notice
------
Py-Networking is at early stages of development. You are free to look around but we do not provide support at the moment
and the library can go throughout a significant changes and backward compatibility cannot be guaranteed.

Install
-------
Installation of Py-Networking can be done from pypi repository (recommended method) or from source code.

Assuming that your system has python and pip command installed::

    sudo pip install py-networking

Pypi repository contains the latest stable version so if you want to work with a newer version and or want to do development
on the library you need to install from source.

Assuming you have python and git command installed::

    git clone https://github.com/alliedtelesis/py-networking.git
    cd py-networking
    sudo ./setup.py install

For further information on how to develop and contribute to py-networking refer to Developing Py-Networking chapter.

License
-------
Apache 2.0


