#!/usr/bin/env python
"""
## License
 GoPiGo for the Raspberry Pi: an open source robotics platform for the Raspberry Pi.
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

import struct
import sys
import signal
from time import sleep
from easygopigo3 import *
import threading
import gopigo3

debug = True # Print raw values when debugging
signal_not_called = True

MOUSE_THRESH = 20 # How much you can move the mouse from its center before the robot starts moving

def signal_handler(signal, frame):
    global signal_not_called
    signal_not_called = False

# bLeft is 1 if the left mouse button is pressed and 0 if it isn't
# bMiddle is 1 if the middle mouse button is pressed and 0 if it isn't
# bRight is 1 if the right mouse button is pressed and 0 if it isn't
# x is the position of the mouse on the x axis
# y is the position of the mouse on the y axis
def getMouseValues(file_input):

    buf = file_input.read(3)
    button = ord(buf[0])
    left_button = (button & 0x1) > 0
    middle_button = (button & 0x4) > 0
    right_button = (button & 0x2) > 0
    x_axis, y_axis = struct.unpack("bb", buf[1:])

    if debug is True:
        print("Left but: {}, Middle but: {}, Right but: {}, x pos: {}, y pos: {}\n".format(left_button, middle_button, right_button, x_axis, y_axis))

    return (left_button, middle_button, right_button, x_axis, y_axis)


def Main():

    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

    print("For moving the robot around using the mouse buttons press 1 and enter.")
    print("For moving the robot around using the movements of the mouse press 2 and enter.")
    try:
        choice = int(raw_input("choice (1/2) = "))
    except ValueError:
        print("Invalid number read")
        sys.exit(1)

    if not (choice == 1 or choice == 2):
        print("Invalid number entered")
        sys.exit(1)

    print("\nWith this script you can control your GoPiGo3 robot with nothing but a mouse.")
    if choice == 1:
        print("1. Left + Right buttons of the mouse - move the GoPiGo3 forward")
        print("2. Left button of the mouse - move the GoPiGo3 to the left")
        print("3. Right button of the mouse - move the GoPiGo3 to the right")
        print("4. Middle button of the mouse - move the GoPiGo3 backward")
    else:
        print("1. Move the mouse forward - for moving the GoPiGo3 forward")
        print("2. Move the mouse backward - for moving the GoPiGo3 backward")
        print("3. Move the mouse to the left - for rotating the GoPiGo3 to the left")
        print("4. Move the mouse to the right - for rotating the GoPiGo3 to the right")

    # Wait for an input to start
    raw_input("Press Enter to start")

    try:
        robot = EasyGoPiGo3()

    except IOError:
        print("GoPiGo3 not detected")
        sys.exit(1)

    except gopigo3.FirmwareVersionError:
        print("Please update your GoPiGo3 firmware")
        sys.exit(1)

    except Exception:
        print("Something went wrong")
        sys.exit(1)

    print("\nIn order to stop the script, press CTRL-C and move your mouse a little bit")
    print('This script has blocking-methods and moving the mouse will get the script "moving" ')

    with open("/dev/input/mice", "rb") as mouse_input:

        left_button = 0
        middle_button = 0
        right_button = 0
        x_axis = 0
        y_axis = 0

        while signal_not_called:

            (left_button, middle_button, right_button, x_axis, y_axis) = getMouseValues(mouse_input)

            if choice == 1:

                if left_button == True and right_button == True:
                    robot.forward()
                elif left_button == True and right_button == False:
                    robot.left()
                elif left_button == False and right_button == True:
                    robot.right()
                elif middle_button == True:
                    robot.backward()
                elif middle_button == False or (left_button == False and right_button == False):
                    robot.stop()

            else:

                if x_axis < -MOUSE_THRESH:
                    robot.left()
                elif x_axis > MOUSE_THRESH:
                    robot.right()
                elif y_axis < -MOUSE_THRESH:
                    robot.backward()
                elif y_axis > MOUSE_THRESH:
                    robot.forward()
                else:
                    robot.stop()

            sleep(0.10)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    Main()
