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
    name="gopigo3",
    description="Drivers and examples for using the GoPiGo3 in Python",
    author="Dexter Industries",
    url="http://www.dexterindustries.com/GoPiGo/",
    py_modules=['gopigo3','easygopigo3','I2C_mutex'],
    #install_requires=open('requirements.txt').readlines(),
)
