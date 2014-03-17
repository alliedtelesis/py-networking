#!/usr/bin/python

import sys
import os
import glob
import unittest
from setuptools import setup, find_packages, Command
import versioneer

versioneer.versionfile_source = 'src/_version.py'
versioneer.versionfile_build = '_version.py'
versioneer.tag_prefix = 'v' # tags are like v1.2.0
versioneer.parentdir_prefix = 'py-networking-' 

class TestCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Change to project root to run tests
        project_root = os.path.dirname(__file__)
        if project_root:
            os.chdir(project_root)

        # Run each .py file found under tests.
        args = [unittest.__file__]
        for root, dirs, files in os.walk('tests'):
            for fn in files:
                if fn.startswith('test') and fn.endswith('.py'):
                    args.append(fn[:-3])

        # Inject tests dir into beginning of sys.path before we run the tests
        sys.path.insert(0, os.path.join(os.getcwd(), 'tests'))
        unittest.main(None, None, args)

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system ('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')

setup(name             = 'py-networking',
      version          = versioneer.get_version(),
      cmdclass         = dict(versioneer.get_cmdclass().items() +
                         {
                            'test': TestCommand,
                            'clean': CleanCommand
                          }.items()),
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




