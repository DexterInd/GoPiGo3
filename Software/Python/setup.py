#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md

try:
	with open('package_description.rst', 'r') as file_description:
		description = file_description.read()

except IOError:
	description = "Check more on https://pypi.python.org/pypi/gopigo3"

from setuptools import setup, find_packages

setup(
    name = "gopigo3",
    version = "1.1.1",

    description = "Drivers and Examples for using the GoPiGo3 in Python",
    long_description = description,

    author = "Dexter Industries",
    author_email = "contact@dexterindustries.com",

    license = 'MIT',
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = "https://github.com/DexterInd/GoPiGo3",

    keywords = ['robot', 'gopigo', 'gopigo3', 'dexter industries', 'learning', 'education'],

    packages=find_packages(),
    py_modules = ['gopigo3','easygopigo3','I2C_mutex'],
    install_requires = ['spidev']
)
