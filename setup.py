#!/usr/bin/python

import sys
import os
from setuptools import setup, find_packages
import versioneer

versioneer.versionfile_source = 'src/_version.py'
versioneer.versionfile_build = '_version.py'
versioneer.tag_prefix = 'v' # tags are like v1.2.0
versioneer.parentdir_prefix = 'py-networking-' 

setup(name             = 'py-networking',
      version          = versioneer.get_version(),
      cmdclass         = versioneer.get_cmdclass(),
      description      = 'Library for network programmability and automation',
      long_description = 'Library for network programmability and automation',
      author           = 'Francesco Salamida',
      author_email     = 'salamida.francesco@gmail.com',
      license          = 'Apache License 2.0',
      package_dir      = {'': 'src'},
      packages         = find_packages('src'),
      install_requires = ['exscript'],
      url              = 'https://github.com/alliedtelesis/py-networking/',
      classifiers      = [
         'Development Status :: 1 - Planning',
         'Intended Audience :: System Administrators',
         'Intended Audience :: Telecommunications Industry',
         'License :: OSI Approved :: Apache Software License',
         'Operating System :: POSIX :: Linux',
         'Programming Language :: Python',
         'Topic :: Software Development :: Libraries :: Python Modules',
         'Topic :: System :: Networking'
       ]
      )




