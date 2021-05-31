#!/usr/bin/env python3
#
# https://www.dexterindustries.com
#
# Copyright (c) 2017 Dexter Industries
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

import time
import os
in_pin = 22
out_pin = 23

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(in_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    GPIO.setup(out_pin, GPIO.OUT)
    GPIO.output(out_pin, True)

    while True:
        if GPIO.input(in_pin):
            os.system("shutdown now -h")
        time.sleep(0.1)

except ModuleNotFoundError:
    import lgpio as LGPIO
    h = LGPIO.gpiochip_open(0)
    LGPIO.gpio_claim_input(h, in_pin, LGPIO.SET_ACTIVE_LOW)

    LGPIO.gpio_claim_output(h, out_pin)
    LGPIO.gpio_write(h, out_pin, 1)

    previous_state = LGPIO.gpio_read(h, in_pin)
    print(LGPIO.gpio_read(h, in_pin))

    while True:
        new_state = LGPIO.gpio_read(h, in_pin)
        if new_state != previous_state:
            print(LGPIO.gpio_read(h, in_pin))
            previous_state = new_state
        if new_state != 1:
            # print("fake shutdown")
            os.system("shutdown now -h")
        time.sleep(0.1)

except:
    pass



