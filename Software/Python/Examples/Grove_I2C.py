#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for using the GoPiGo3 software I2C busses.
#
# Hardware: Connect an I2C device to port AD1.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

I2C_Slave_Address = 0x24 # the address of the I2C slave

try:
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.I2C)
    i = 0
    while(True):
        GPG.grove_i2c_transfer(GPG.GROVE_1, I2C_Slave_Address, [i])                     # write one byte
        #print(GPG.grove_i2c_transfer(GPG.GROVE_1, I2C_Slave_Address, [0, 1, 0, 1], 1)) # write four bytes and read one byte
        print(i, GPG.grove_i2c_transfer(GPG.GROVE_1, I2C_Slave_Address, [], 16))        # read sixteen bytes
        
        time.sleep(0.1)
        
        i += 1
        if i > 15:
            i = 0

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
