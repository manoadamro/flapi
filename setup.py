# coding: utf-8

import setuptools


NAME = 'flapi'
VERSION = '0.0.0'
REQUIRES = [
    'flask',
    'pyjwt',
    'jsonpointer'
]


setuptools.setup(
    name=NAME,
    version=VERSION,
    install_requires=REQUIRES,
    packages=setuptools.find_packages()
)
