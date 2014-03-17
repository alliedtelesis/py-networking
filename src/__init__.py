# Import python libs
import os
import sys
import warnings

# All salt related deprecation warnings should be shown once each!
warnings.filterwarnings(
     'once', # Show once
     '', # No deprecation message match
      DeprecationWarning, # This filter is for DeprecationWarnings
      r'^(py-networking|py-networking\.(.*))$' # Match module(s) 'py-networking' and 'py-networking.<whatever>'
)

# While we are supporting Python2.6, hide nested with-statements warnings
warnings.filterwarnings(
      'ignore',
      'With-statements now directly support multiple context managers',
      DeprecationWarning
)

class Device(object):
    pass


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
