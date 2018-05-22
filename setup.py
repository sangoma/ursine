#!/usr/bin/env python3
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


install_requires = [
    'multidict',
]

tests_require = [
    'pytest',
    'pytest-benchmark',
]


def readme():
    with open('README.md') as fp:
        return fp.read()


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
      version='0.3.1',
      description='library for SIP url handling/maninupation',
      long_description=readme(),
      long_description_content_type='text/markdown',
      author='Terry Kerr',
      author_email='t@xnr.ca',
      license='Apache 2',
      packages=['ursine'],
      keywords=['sip', 'voip', 'url'],
      url='https://github.com/sangoma/ursine',
      install_requires=install_requires,
      python_requires='>=3.6',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
          'Topic :: Communications :: Telephony',
          'Topic :: Communications :: Internet Phone',
          'License :: OSI Approved :: Apache Software License',
      ],
      tests_require=tests_require,
      cmdclass={'test': PyTest},
      )
