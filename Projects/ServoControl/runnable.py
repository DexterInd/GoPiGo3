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

# modules for interfacing with the GoPiGo3 from
# a terminal with a keyboard
from keyboarded_robot import LiveKeyboard
from keyboarded_robot import GoPiGo3WithKeyboard
from curtsies import Input

from time import sleep

def Main():

    try:

        # GoPiGo3WithKeyboard is used for mapping
        # keyboard keys to actual GoPiGo3 commands
        # the keys-to-gopigo3 bindings are defined inside the class
        gopigo3 = GoPiGo3WithKeyboard()
    except IOError as error:

        # if the GoPiGo3 is not reachable
        # then print the error and exit
        print(str(error))
        exit(1)

    # draws the GoPiGo3 logo
    gopigo3.drawLogo()
    # writes some description on the GoPiGo3
    gopigo3.drawDescription()
    # writes the menu for controlling the GoPiGo3 robot
    # key bindings are shown in here
    gopigo3.drawMenu()

    # this class is used for detecting key presses on the keyboard
    kb = LiveKeyboard()
    # it's derived from threading.Thread class so we need to start it
    kb.start()
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
    refresh_rate = 50.0

    with Input(keynames = "curtsies", sigint_event = True) as input_generator:
        while True:
            period = 1 / refresh_rate
            key = input_generator.send(period)

            if key is not None:
                result = gopigo3.executeKeyboardJob(key)

                if result == "exit"
                    break
                    
            else if manual_mode is False:
                gopigo3.executeKeyboardJob("x")

if __name__ == "__main__":
    Main()
