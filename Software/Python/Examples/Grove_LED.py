#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for using a grove LED with GoPiGo3.
#
# Hardware: Connect a grove LED to port AD2 of the GoPiGo3.
#
# Results: When you run this program, the grove LED should turn on for two seconds.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

try:
    GPG.set_grove_type(GPG.GROVE_2, GPG.GROVE_TYPE.CUSTOM)
    GPG.set_grove_mode(GPG.GROVE_2_1, GPG.GROVE_OUTPUT_DIGITAL)
    GPG.set_grove_state(GPG.GROVE_2_1, True)
    #GPG.set_grove_mode(GPG.GROVE_2_1, GPG.GROVE_OUTPUT_PWM)
    #GPG.set_grove_pwm_duty(GPG.GROVE_2_1, 50)
    
    time.sleep(2)
    GPG.reset_all()

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
