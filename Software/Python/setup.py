#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2016 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md

import setuptools

setuptools.setup(
    name = "gopigo3",
    version = "1.0.0",

    description = "Drivers and Examples for using the GoPiGo3 in Python",
    long_description = " \
    Within this python package there 2 main modules we can develop with:\n \
    1. gopigo3 - This package is a low level module for controlling the GoPiGo3\n \
    2. easygopigo3 - This package is a higher-level module built on top of the gopigo3 module which is more user friendly. \n \
    \n \
    Among these 2 main modules, there is also a package which contains example programs",

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

    packages = ['Examples', 'Examples.Control_Panel', 'Examples.Line_Sensor'],
    py_modules = ['gopigo3','easygopigo3','I2C_mutex'],
    install_requires = ['spidev']
)
