#!/usr/bin/env python3
#
# https://www.dexterindustries.com
#
# Copyright (c) 2017 Modular Robotics
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is for power management on a Raspberry Pi with GoPiGo3.
#
# GPIO 22 will be configured as input with pulldown. If pulled high, the RPi will halt.
#
# GPIO 23 needs to remain low impedance (output) set to a HIGH state. If GPIO 23 gets
# left floating (high impedance) the GoPiGo3 assumes the RPi has shut down fully.
# SW should never write GPIO 23 to LOW or set it as an INPUT.


import RPi.GPIO as GPIO
import time
import os
import signal
import sys


def _cleanup_and_exit(signum=None, frame=None):
    GPIO.cleanup()
    sys.exit(0)


signal.signal(signal.SIGTERM, _cleanup_and_exit)
signal.signal(signal.SIGINT, _cleanup_and_exit)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Under lgpio (used by RPi.GPIO on Debian Trixie) a GPIO pin stays claimed
# until the kernel releases it after a process exit. Retry briefly to allow a
# previous service instance to fully release the pins before failing.
for _attempt in range(10):
    try:
        GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, True)
        break
    except Exception:
        if _attempt == 9:
            raise
        time.sleep(0.5)

try:
    while True:
        if GPIO.input(22):
            os.system("shutdown now -h")
        time.sleep(0.1)
finally:
    GPIO.cleanup()
