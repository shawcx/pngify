#!/usr/bin/env python

import os

from setuptools import setup

#exec(compile(open('_/py/version.py').read(),'version.py','exec'))

setup(
    name               = 'pngify',
    author             = 'Matthew Oertle',
    author_email       = 'moertle@gmail.com',
    version            = '0.1',
    license            = 'MIT',
    url                = 'http://oertle.org/pngify',
    description        = 'Inject and extract data from PNG files',
    long_description   = open('README.rst').read(),
    scripts = [
        'bin/pngify',
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ]
    )
