#!/usr/bin/env python
#
# https://www.dexterindustries.com
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is for power management on a Raspberry Pi

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
