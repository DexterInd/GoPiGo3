#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo3/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license
# (http://choosealicense.com/licenses/mit/).
#
# For more information see
# https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for controlling the GoPiGo3 blinkers.  This uses
# the EasyGoPiGo3 library.  You can find more information on the library
# here:  http://gopigo3.readthedocs.io/en/latest/api-basic.html#easygopigo3
# These "Blinkers" are the LED's are located under the I2C ports on the GoPiGo3
#
# Results:  The GoPiGo3 will turn the LED's on, then the left LED off, and then
# the right LED off.


# import the time library for the sleep function
import time
# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()

left = 0
right = 1

while True:
    # Turn both LEDs on
    # These LED's are located under the I2C ports on the GoPiGo3
    gpg.led_on("left")
    gpg.led_on("right")
    time.sleep(1)

    # Turn the left LED off
    gpg.led_off("left")
    time.sleep(1)

    # Turn the right LED Off
    gpg.led_off("right")
    time.sleep(1)
