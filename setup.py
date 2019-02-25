#!/usr/bin/env python3

import os

from setuptools import setup

setup(
    name              = 'pngify',
    version           = '0.4',
    author            = 'Matthew Oertle',
    author_email      = 'moertle@gmail.com',
    license           = 'MIT',
    description       = 'Inject and extract data from PNG files',
    long_description  = open('README.rst').read(),
    url               = 'https://github.com/moertle/pngify',
    py_modules   = ['pngify'],
    entry_points = {
        'console_scripts': [
            'pngify = pngify:main',
            ]
        },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        ]
    )
