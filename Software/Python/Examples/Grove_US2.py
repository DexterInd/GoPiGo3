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
# Hardware: Connect a grove ultrasonic sensor to port AD1 and another to port AD2 of the GoPiGo3.
#
# Results: When you run this program, the distance measured with the ultrasonic sensors should be printed.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

sensor1 = 0
sensor2 = 0

try:
    # configure both ultrasonic sensors
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.US)
    GPG.set_grove_type(GPG.GROVE_2, GPG.GROVE_TYPE.US)
    
    # wait for the sensors to get configured
    time.sleep(0.05)
    
    while(True):
        # try reading sensor 1
        try:
            sensor1 = GPG.get_grove_value(GPG.GROVE_1)
        except gopigo3.SensorError as error:
            pass
        
        # try reading sensor 2
        try:
            sensor2 = GPG.get_grove_value(GPG.GROVE_2)
        except gopigo3.SensorError as error:
            pass
        
        # print the sensor values
        print("Sensor 1: %4dmm   Sensor 2: %4dmm" % (sensor1, sensor2))
        
        # slow down a little
        time.sleep(0.05)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()       # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.

except Exception, e:
    print(e)
    GPG.reset_all()
