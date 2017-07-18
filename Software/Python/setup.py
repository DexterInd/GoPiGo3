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
    url="http://www.dexterindustries.com/GoPiGo3/",
    py_modules=['gopigo3','easygopigo3','I2C_mutex'],
    #install_requires=open('requirements.txt').readlines(),
    version='1.0.0',
    long_description=" \
    This python package includes two main modules for development: \n \
    1. gopigo3 - This package is a low level module for controlling the GoPiGo3. \n \
    2. easygopigo3 - This package is a higher-level module built on top of the gopigo3 module which is more user friendly.  \n \ ",
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Education',
        'Framework :: Robot Framework',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords=['robot', 'gopigo', 'gopigo3', 'dexter industries', 'raspberry pi'],
    packages=['Examples', 'Examples.Control_Panel', 'Examples.Line_Sensor'],
    install_requires=['spidev'],
)
