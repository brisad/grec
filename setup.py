#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import sys
from setuptools.command.test import test as TestCommand


class Tox(TestCommand):
    user_options = [('tox-args=', 'a', 'Arguments to pass to tox')]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = ""
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import tox
        import shlex
        errno = tox.cmdline(args=shlex.split(self.tox_args))
        sys.exit(errno)


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'termcolor'
]

test_requirements = [
    'pytest', 'tox'
]

setup(
    name='grec',
    version='0.2.0',
    description='Colorize terminal text with regular expressions.',
    long_description=readme + '\n\n' + history,
    author='Michael Brennan',
    author_email='brennan.brisad@gmail.com',
    url='https://github.com/brisad/grec',
    packages=[
        'grec',
    ],
    scripts=['scripts/grec'],
    package_dir={'grec':
                 'grec'},
    include_package_data=True,
    install_requires=requirements,
    license="GPL",
    zip_safe=False,
    keywords='grec',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    cmdclass={'test': Tox}
)
