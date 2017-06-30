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
    version = "0.0.1",
    description = "Drivers and examples for using the GoPiGo3 in Python",
    long_description = " \
    Within this python package there 2 main modules we can develop with:\n \
    1. gopigo3 - low-level module for controlling the GPG3\n \
    2. easygopigo3 - higher-level module built on top of gopigo3 module which\
    is more user-friendly - allows the user to easily control a GPG3.\n \
    Updated on 29th of June 2017.\
    ",
    author = "Dexter Industries",
    author_email = "contact@dexterindustries.com",
    license = 'MIT',
    url = "http://www.dexterindustries.com/GoPiGo/",
    py_modules = ['gopigo3','easygopigo3','I2C_mutex'],
    install_requires = ['spidev', 'fcntl']
)
