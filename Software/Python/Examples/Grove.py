#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for demonstrating grove devices with the GoPiGo3.
#
# Hardware: Connect a grove buzzer to port AD1, and a grove potentiometer to port AD2.
#
# Results: When you run this program, the position of the potentiometer will determine the tone of the buzzer.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

try:
    GPG.set_grove_type(GPG.GROVE_1, GPG.GROVE_TYPE.CUSTOM)
    GPG.set_grove_type(GPG.GROVE_2, GPG.GROVE_TYPE.CUSTOM)
    
    GPG.set_grove_mode(GPG.GROVE_1_1, GPG.GROVE_OUTPUT_PWM)
    GPG.set_grove_mode(GPG.GROVE_2, GPG.GROVE_INPUT_ANALOG)
    
    duty = 10
    #freq = 0
    while(True):
        try:
            print("Battery: %6.3fv   5v: %5.3fv   State: %d   Voltage: %4.2fv   ADC: %4d" % (GPG.get_voltage_battery(), GPG.get_voltage_5v(), GPG.get_grove_state(GPG.GROVE_2_1), GPG.get_grove_voltage(GPG.GROVE_2_1), GPG.get_grove_analog(GPG.GROVE_2_1)))
            duty = duty + 1
            if duty > 90:
                duty = 10
            GPG.set_grove_pwm_duty(GPG.GROVE_1_1, duty)
            
            GPG.set_grove_pwm_frequency(GPG.GROVE_1, GPG.get_grove_analog(GPG.GROVE_2_1))
            time.sleep(0.1)
        except gopigo3.ValueError as error:
            pass

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
