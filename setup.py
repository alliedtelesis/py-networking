#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import glob
import unittest
from setuptools import setup, find_packages, Command
import versioneer

versioneer.versionfile_source = 'src/_version.py'
versioneer.versionfile_build = 'pynetworking/_version.py'
versioneer.tag_prefix = 'v' # tags are like v1.2.0
versioneer.parentdir_prefix = 'py-networking-' 

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system ('rm -rf ./.tox ./build ./dist ./*.pyc ./*.tgz ./*.egg-info ./py-networking-*')

setup(name             = 'py-networking',
      version          = versioneer.get_version(),
      cmdclass         = dict(versioneer.get_cmdclass().items() +
                         {
                            'clean': CleanCommand
                          }.items()),
      description      = 'Library for network programmability and automation',
      long_description = 'Library for network programmability and automation',
      author           = 'Francesco Salamida',
      author_email     = 'salamida.francesco@gmail.com',
      license          = 'Apache License 2.0',
      package_dir      = {'pynetworking': 'src'},
      packages         = ['pynetworking'],
      install_requires = ['paramiko'],
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




