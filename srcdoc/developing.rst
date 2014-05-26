Developing Py-Networking
************************

Setup your develop environment
------------------------------
Create an account on Github and fork the PN repository.
Clone the newly forked repository on your PC::

    git clone https://github.com/<your_user>/py-networking

to verify that your environment is correctly setup and all the requirements are fulfilled you can try to
execute the tests that comes with PN::

    cd py-networking
    ./setup tests

Create a branch for your changes
--------------------------------
Whenever you want to fix a bug or add/expand support for a device you should create a new git branch::

    git checkout -b fix-issue-found

Keep your repository in sync
----------------------------
Since your fork of PN repository is just a snapshot you will need to manually keep it in sync with the master
repository and avoid that you make changes starting form a codebase which is too outdated.
Start adding the master PN repository::

    git remote add upstream https://github.com/alliedtelesis/py-networking.git

when you want to synchronize your repository::

    git fetch upstream
    git merge upstream/develop

Add support for a new device
----------------------------
PN source code is in the *pynetworking* directory. Adding the support for new device or class of devices usually
requires the following steps:

* Pick a short **<name>** that identify the device(s). For examples for all Allied Telesis switches that runs AlliedWare
  Plus Operating System we have picked **awp**.
* Add a the source file core_<name>.py (core_awp.py in our example) in the directory *pynetworking/facts*
* Add the function core_<name> in core_<name>.py source file. PN will try to invoke the function when Device open is
  invoked to determine what the kind of device it is. The function should query the device and determine if it's of the kind
  it support and should return a dictionary with information relevant to the device. Among all, it must add the key 'os'
  with <name>::

    def core_awp(dev):
        '''
        Pseudo code for an AlliedWare Plus core facts function
        '''

        ret = dict()
        # if this is an AlliedWare plus device
        ret['os'] = 'awp'

        # add more facts like OS version

        return ret

  The execution of all core facts will generate a single dictionary with a list of key value pairs that will be
  became the environment of the execution of a Jinja template, *pynetworking/Device.yaml* that will finally produce
  a YAML file::

    {% if os == 'awp' %}
    system: awp_system
    {% elif os == 'ats' %}
    system: ats_system
    {% endif %}

    features:
    {% if os == 'awp' %}
      vlan: awp_vlan
      interface: awp_interface
    {% elif os == 'ats' %}
      interface: ats_interface
      vlan: ats_vlan
    {% endif %}

  the expected yaml file will need to have two main sections *system* and *features*

* Add in *pynetworking/system* directory a file with a name associated with the section system (in our example
  awp_system.py). PN expects to find a class with same name of the file (awp_system) that implements a number of methods
  as described in system section (TBD). An instance of this class will be created at runtime in the device open method.

* Add in *pynetworking/features* directory one source file for each feature that the device has. The filename is
  the value of the keyword associated with the feature. For example for awp the filename will be awp_interface
  based on the above mentioned Device.yaml file.
  PN expects to find in the feature source code a class with same name derived from Feature class.
  As with the system class, an instance of the feature class will be created at runtime and will be accessible throughout
  the feature name.

Add unit and integration tests
------------------------------
Any code you add should come with a number of unit and integration tests that guarantee a good level of coverage and quality.
The test framework used by PN is pytest.
A test case is a simple function with the prefix *test_* in a source code file with same prefix in directory tests.
The test case is automatically discovered by pytest.
PN testing framework provides a device emulator that helps to run the tests without the actual device.
To access to this emulated device the test need to have a parameter called *dut*.
Dut is a object that implement an ssh server running on a random free port taken when the test is run::

    def test_my_test(dut):
        dut.host # host where server is running, usually localhost
        dut.port # port where server is running
        dut.protocol # protocol implement by dut. At the moment only ssh

Dut has a number of methods that allow customizing its behaviour. The most important one is *add_cmd* and allows adding
new CLI command::

    # add a command that emulate 'show version'
    dut.add({
            'cmd':'show version', # the command string
            'state':-1,           # the state in which the command is applicable
            'action':  'PRINT',   # the action that will be taken
                       'args':    # the arguments of the action
                    ["""
    AlliedWare Plus (TM) 5.4.2 09/25/13 12:57:26

    Build name : x600-5.4.2-3.14.rel
    Build date : Wed Sep 25 12:57:26 NZST 2013
    Build type : RELEASE
                     """]
            })

In addition to the action **PRINT** of the example above the other currently supported actions are **SET_PROMPT** and
**SET_STATE**.

**SET_PROMPT** allows changing the prompt so to simulate entering in the interface configuration::

    # add a command that emulate 'show version'
    dut.add({
            'cmd':'interface port1.0.10',        # the command string
            'state': 0,                          # the state in which the command is applicable
            'action': 'SET_PROMPT',              # the action that will be taken
                      'args': ['(config-if)#']   # the arguments of the action
            })

**SET_STATE** allows changing the internal state of the emulator. States are numbered from 0 to 9 while -1 identify all
states.

You can run all test with the command::

    ./setup.py tests

but during the development it's convenient to execute single test, increase the logging level or execute tests on a real
device. In this case the tool *tox* comes handy::

       tox -e dev tests/<test_file>.py -- [-k <test_function>] [--dut-host=<device>] [--log=<log_level>]

where::

    test_file:     the file containing the test functions to execute
    test_function: the test function within test_file to be executed. If omitted all test function within the fill will
                   be executed form the top to the bottom
    device:        the ip address or hostname of the real device on which tests will be executed. If omitted the device
                   under test will the emulated one
    log_level:     log level (debug, info, warning, error, critical)

The log level is injected into the test function with the paramter log_level that should be passed to the device as shown
below::

    def test_my_test(dut, log_level):
    d=Device(host=dut.host,port=dut.port,protocol=dut.protocol, log_level=log_level)

Commit your changes
-------------------
During the development make commits of your work to your repository::

    git commit -am "some meaningful message"
    git push --set-upstream origin fix-issue-found

and when you are happy generate a pull request form *Github*.
Make sure your changes haven't broken anything running all the tests as described above.
Anyway all tests will be executed on `travis-ci <https://travis-ci.org/alliedtelesis/py-networking/pull_requests>`_ on
your pull request and the associated test coverage will be visible on `coveralls <https://coveralls.io/r/alliedtelesis/py-networking>`_.