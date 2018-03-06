#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for controlling the GoPiGo3 LED.
#
# Results:  When you run this program, the GoPiGo3 LEDs will fade up and down.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3 # import the GoPiGo3 drivers

GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.

try:
    while True:
        for i in range(11):                                # count from 0-10
            GPG.set_led(GPG.LED_EYE_LEFT, i, i, i)                # set the LED brightness (0 to 255)
            GPG.set_led(GPG.LED_EYE_RIGHT, 10 - i, 10 - i, 10 - i) # set the LED brightness (255 to 0)
            GPG.set_led(GPG.LED_BLINKER_LEFT, (i * 25))           # set the LED brightness (0 to 255)
            GPG.set_led(GPG.LED_BLINKER_RIGHT, ((10 - i) * 25))     # set the LED brightness (255 to 0)
            time.sleep(0.02)                               # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
        
        GPG.set_led(GPG.LED_WIFI, 0, 0, 10)
        
        for i in range(11):                                # count from 0-10
            GPG.set_led(GPG.LED_EYE_LEFT, 10 - i, 10 - i, 10 - i) # set the LED brightness (255 to 0)
            GPG.set_led(GPG.LED_EYE_RIGHT, i, i, i)                # set the LED brightness (0 to 255)
            GPG.set_led(GPG.LED_BLINKER_LEFT, ((10 - i) * 25))    # set the LED brightness (0 to 255)
            GPG.set_led(GPG.LED_BLINKER_RIGHT, (i * 25))            # set the LED brightness (255 to 0)
            time.sleep(0.02)                               # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load and give time to see the LED pulsing.
        
        GPG.set_led(GPG.LED_WIFI, 0, 0, 0)

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    GPG.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the GoPiGo3 firmware.
