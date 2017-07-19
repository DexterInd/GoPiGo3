#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license
# (http://choosealicense.com/licenses/mit/).
#
# For more information see
# https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for controlling the GoPiGo3 LED.
#
# Results:  When you run this program, the GoPiGo3 will take
# readings from a Grove light sensor connected to its
# port Analog/Digital 1
#


# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()

# Create an instance of the Light sensor
my_light_sensor = gpg.init_light_sensor("AD1")
my_led = gpg.init_led("AD2")

# loop forever while polling the sensor
while(True):
    # get absolute value
    reading = my_light_sensor.read()
    # scale the reading to a 0-100 scale
    percent_reading = my_light_sensor.percent_read()

    # check if the light's intensity is above 50%
    if percent_read >= 50:
        my_led.light_off()
    else:
        my_led.light_max()
    print("{}, {:.1f}%".format(reading, percent_reading))

    time.sleep(0.05)
