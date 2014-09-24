#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'termcolor'
]

test_requirements = [
    'pytest'
]

setup(
    name='grec',
    version='0.1.0',
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
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
