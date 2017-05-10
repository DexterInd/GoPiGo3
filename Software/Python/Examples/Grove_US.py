#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for using the grove ultrasonic sensor with the GoPiGo3.
#
# Hardware: Connect a grove ultrasonic sensor to port AD1 of the GoPiGo3.
#
# Results: When you run this program, the distance measured with the ultrasonic sensor should be printed.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

try:
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.US)
    
    while(True):
        value = GPG.get_grove_value(GPG.GROVE_1)
        if value is 0:
            print("   0mm Sensor not responding")
        elif value is 1:
            print("   0mm Object not detected within range")
        else:
            print("%4dmm" % value)
        time.sleep(0.05)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
