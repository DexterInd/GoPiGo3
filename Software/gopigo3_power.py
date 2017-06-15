#!/usr/bin/env python
#
# https://www.dexterindustries.com
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is for power management on a Raspberry Pi
# GPIO 23 needs to remain low impedance (output) set to a HIGH state. If GPIO 23 gets left floating (high impedance) the GoPiGo3 assumes the RPi has shut down fully. SW should never write GPIO 23 to LOW or set it as an INPUT.



import RPi.GPIO as GPIO
import time
import os
import atexit

atexit.register(GPIO.cleanup)


GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)

GPIO.setup(23, GPIO.OUT)
GPIO.output(23, True)

while True:
    if GPIO.input(22):
        os.system("shutdown now -h")
    time.sleep(0.1)
