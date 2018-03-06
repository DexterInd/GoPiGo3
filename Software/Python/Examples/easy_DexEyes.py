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

while True:
    # Set the eye color to blue.
    # Setting the eye color is a tuple of (R, G, B) values, greater than
    # zero and less than 255.
    gpg.set_left_eye_color((1,1,125))
    gpg.set_right_eye_color((1,1,125))
    time.sleep(1)

    # Open the left eye with the blue color
    gpg.open_left_eye()
    time.sleep(1)

    # Open the right eye with the blue color
    gpg.open_right_eye()
    time.sleep(1)

    # Set BOTH eye color to red.

    gpg.set_eye_color((125,1,1))

    # Change the left eye to red.
    gpg.open_left_eye()
    time.sleep(1)

    # Change the right eye to red.
    gpg.open_right_eye()
    time.sleep(2)

    # Close both eyes.
    gpg.close_eyes()
    time.sleep(1)

    # Set the left eye to red, the right eye to blue.
    gpg.set_left_eye_color((125,1,1))
    gpg.set_right_eye_color((1,1,125))

    # Open both eyes at once
    gpg.open_eyes()
    time.sleep(1)
