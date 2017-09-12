#!/usr/bin/env python

"""
GoPiGo3 for the Raspberry Pi: an open source robotics platform for the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
"""

from __future__ import print_function
from __future__ import division

# module for interfacing with the GoPiGo3 from
# a terminal with a keyboard
from keyboarded_robot import GoPiGo3WithKeyboard
# module for capturing input events from the keyboard
from curtsies import Input
import signal

from time import sleep

def Main():
    # GoPiGo3WithKeyboard is used for mapping
    # keyboard keys to actual GoPiGo3 commands
    # the keys-to-gopigo3 bindings are defined inside the class
    gopigo3 = GoPiGo3WithKeyboard()

    # draws the GoPiGo3 logo
    gopigo3.drawLogo()
    # writes some description on the GoPiGo3
    gopigo3.drawDescription()
    # writes the menu for controlling the GoPiGo3 robot
    # key bindings are shown in here
    gopigo3.drawMenu()

    # result holds the exit string when we call a gopigo3 command
    # with the GoPiGo3WithKeyboard object
    result = "nothing"
    """
    result can take the following values:
    "nothing", "moving", "path", "static", "exit"
    """
    # if manual_mode is set to true, then the robot
    # moves for as long as the coresponding keys are pressed
    # if manual_mode is set to false, then a key needs
    # to be pressed once in order for the robot to start moving
    manual_mode = False
    successful_exit = True
    refresh_rate = 20.0

    with Input(keynames = "curtsies", sigint_event = True) as input_generator:
        while True:
            period = 1 / refresh_rate
            # if nothing is captured in [period] seconds
            # then send() function returns None
            key = input_generator.send(period)

            # if we've captured something from the keyboard
            if key is not None:
                result = gopigo3.executeKeyboardJob(key)

                if result == "exit":
                    break

            # if we haven't captured anything
            # and if the robot is set to manual_mode
            # then stop the robot from moving as soon as the key(s)
            # for moving (the robot around) are released
            elif manual_mode is True and result == "moving":
                gopigo3.executeKeyboardJob("x")


if __name__ == "__main__":
    # set up a handler for ignoring the Ctrl+Z commands
    signal.signal(signal.SIGTSTP, lambda signum, frame : print("Press the appropriate key for closing the app."))

    try:
        Main()
    except IOError as error:
        # if the GoPiGo3 is not reachable
        # then print the error and exit
        print(str(error))
        exit(1)

    exit(0)
