#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for using the grove buzzer with the GoPiGo3.
# 
# Hardware: Connect a grove buzzer to AD1 port.
#
# Results: When you run this program, the buzzer should repeat the scale of middle C through tenor C.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time    # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]

try:
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.CUSTOM)  # set AD1 as custom
    GPG.set_grove_mode(GPG.GROVE_1_1, GPG.GROVE_OUTPUT_PWM) # enable PWM output on AD1 pin 1
    
    GPG.set_grove_pwm_duty(GPG.GROVE_1_1, 50) # set the duty cycle to 50%. 10-90 should work, and changing it will effect the sound.
    
    note = 0
    while(True):
        GPG.set_grove_pwm_frequency(GPG.GROVE_1, scale[note]) # set the frequency.
        note += 1
        if note >= 8:
            note = 0
        time.sleep(0.5)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()       # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
