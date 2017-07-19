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

from keyboarded_robot import *
from time import sleep

def Main():

    try:
        gopigo3 = GoPiGo3WithKeyboard()
    except IOError as error:
        print(str(error))
        exit(1)

    gopigo3.drawLogo()
    gopigo3.drawDescription()
    gopigo3.drawMenu()

    kb = LiveKeyboard()
    kb.start()
    result = "nothing"
    """
    result can take the following values:
    "nothing", "moving", "path", "static", "exit"
    """
    manual_mode = False
    successful_exit = True

    while True:
        key = kb.getKey()

        if key is not None:

            try:
                result = gopigo3.executeKeyboardJob(key)
            except IOError as error:
                print(str(error))
                kb.join()
                successful_exit = False
                break

            if result == "exit":
                kb.join()
                break
        else:
            if result == "moving" and manual_mode is True:
                # "x" is for stopping the robot from moving
                gopigo3.executeKeyboardJob("x")

        sleep(0.05)

    if successful_exit is True:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    Main()
