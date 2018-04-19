#!/usr/bin/env python3
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


install_requires = [
    'multidict',
]

tests_require = [
    'pytest',
]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(name='ursine',
      version='0.1',
      description='libarary for SIP url handling/maninupation',
      author='Terry Kerr',
      author_email='t@xnr.ca',
      license='Apache 2',
      packages=['ursine'],
      keywords=['sip', 'voip', 'url'],
      install_requires=install_requires,
      classifiers=[
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Communications :: Telephony',
          'Topic :: Communications :: Internet Phone',
          'License :: OSI Approved :: Apache Software License',
      ],
      tests_require=tests_require,
      cmdclass={'test': PyTest},
      )
