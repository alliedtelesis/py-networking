#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import glob
from setuptools import setup, find_packages, Command
from setuptools.command.test import test as TestCommand
import versioneer

versioneer.versionfile_source = 'src/_version.py'
versioneer.versionfile_build = 'pynetworking/_version.py'
versioneer.tag_prefix = 'v' # tags are like v1.2.0
versioneer.parentdir_prefix = 'py-networking-' 

class ToxCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system ('rm -rf ./MANIFEST ./.tox ./build ./dist ./*.pyc ./*.tgz ./*.egg ./*.egg-info ./py-networking-* ./doc')

class DocCommand(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        from sphinx.application import Sphinx
        from sphinx.util.console import darkred, nocolor
        import subprocess

        self.source_dir = os.path.abspath('srcdoc')
        self.build_dir = os.path.join('./build', 'sphinx')
        self.mkpath(self.build_dir)
        self.doctree_dir = os.path.join(self.build_dir, 'doctrees')
        self.mkpath(self.doctree_dir)
        self.builder_target_dir = 'doc'
        self.mkpath(self.builder_target_dir)
        confoverrides = {
                            'version': versioneer.get_version(),
                            'release': versioneer.get_version(),
                        }

        app = Sphinx(self.source_dir, self.source_dir,
                     self.build_dir, self.doctree_dir,
                     'latex', confoverrides, sys.stdout,
                     freshenv=False)

        try:
            app.builder.build_update()
        except Exception, err:
            from docutils.utils import SystemMessage
            if isinstance(err, SystemMessage):
                sys.stderr, darkred('reST markup error:')
                print >>sys.stderr, err.args[0].encode('ascii', 'backslashreplace')
            else:
                raise
        print "Generating PDF"
        subprocess.check_output(
            "pushd {0} && make all-pdf && popd && cp {0}/*.pdf ./srcdoc".format(self.build_dir, self.build_dir),
            stderr=subprocess.STDOUT,
            shell=True)

        app = Sphinx(self.source_dir, self.source_dir,
                     'doc', self.doctree_dir,
                     'html', confoverrides, sys.stdout,
                     freshenv=True)

        try:
            app.builder.build_update()
        except Exception, err:
            from docutils.utils import SystemMessage
            if isinstance(err, SystemMessage):
                sys.stderr, darkred('reST markup error:')
                print >>sys.stderr, err.args[0].encode('ascii', 'backslashreplace')
            else:
                raise

setup(name             = 'py-networking',
      version          = versioneer.get_version(),
      cmdclass         = dict(versioneer.get_cmdclass().items() +
                         {
                            'test': ToxCommand,
                            'clean': CleanCommand,
                            'doc': DocCommand
                          }.items()),
      description      = 'Library for network programmability and automation',
      long_description = 'Library for network programmability and automation',
      author           = 'Francesco Salamida',
      author_email     = 'salamida.francesco@gmail.com',
      license          = 'Apache License 2.0',
      package_dir      = {
                            'pynetworking': 'src',
                            'pynetworking.features': 'src/features',
                            'pynetworking.facts': 'src/facts',
                            'pynetworking.system': 'src/system',
                         },
      packages         = [
                            'pynetworking',
                            'pynetworking.features',
                            'pynetworking.facts',
                            'pynetworking.system',
                         ],
      package_data     = {
                            'pynetworking': ['*.yaml']
                         },
      install_requires = [  
                            'paramiko',
                            'PyYAML',
                            'Jinja2',
                            'ply',
                            'twisted',
                            'pyasn1',
                            'pyzmq',
                         ],
      setup_requires   = [ 'sphinx'],
      tests_require    = [
                            'tox'
                         ],
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




