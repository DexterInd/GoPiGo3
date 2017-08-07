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
from easygopigo3 import EasyGoPiGo3
from builtins import input
import threading
import gopigo3
import atexit

debug = False # Print raw values when debugging
signal_not_called = True # used to stop reading values from the mouse

MOUSE_THRESH = 20 # the mouse's sensitivity - the bigger the number, the less sensible the mouse. Idem vice-versa.

# ensure that upon exit the robot stops moving
def cleanup_func(gopigo3):
    print("stopping GoPiGo3")
    gopigo3.stop()

# upon exit, stop reading values from the mouse
# used in conjunction with signal_not_called var
def signal_handler(signal, frame):
    print("stop reading mouse values")
    global signal_not_called
    signal_not_called = False

# bLeft is 1 if the left mouse button is pressed and 0 if it isn't
# bMiddle is 1 if the middle mouse button is pressed and 0 if it isn't
# bRight is 1 if the right mouse button is pressed and 0 if it isn't
# x is the position of the mouse on the x axis
# y is the position of the mouse on the y axis
def getMouseValues(file_input):

    buf = file_input.read(3)

    # if ran with Python 3
    # ord function will throw an exception, since
    # buf[0] already is an integer, as opposed in Python 2
    # where buf[0] is a string
    try:
        button = ord(buf[0])
    except TypeError as msg:
        button = buf[0]
        if debug is True:
            print(str(msg))

    print(button)
    left_button = (button & 0x1) > 0
    middle_button = (button & 0x4) > 0
    right_button = (button & 0x2) > 0
    x_axis, y_axis = struct.unpack("bb", buf[1:])

    if debug is True:
        print("Left but: {}, Middle but: {}, Right but: {}, x pos: {}, y pos: {}".format(left_button, middle_button, right_button, x_axis, y_axis))

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

    # read data from the keyboard
    # if it fails reading the right values, then the script exits
    try:
        choice = int(input("choice (1/2) = "))
    except ValueError:
        print("Invalid number read")
        sys.exit(1)

    if not (choice == 1 or choice == 2):
        print("Invalid number entered")
        sys.exit(1)

    # now the choice var can either be 1 or 2
    # show different menus depending on the choice var
    print("\nWith this script you can control your GoPiGo3 robot with a wireless mouse.")
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
    input("\nPress Enter to start")

    # create an instance of the EasyGoPiGo3 class
    # if it fails instantiating the object, then the scripts exits
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

    # stops the robot from moving when exiting the script
    # the cleanup_func is called after the signal_handler function
    atexit.register(cleanup_func, gopigo3 = robot)

    print("\nIn order to stop the script, press CTRL-C and move your mouse a little bit")

    # open file for reading the continuous stream of data from the mouse
    with open("/dev/input/mice", "rb") as mouse_input:

        left_button = 0
        middle_button = 0
        right_button = 0
        x_axis = 0
        y_axis = 0

        # as long as CTRL-C hasn't been pressed
        while signal_not_called:

            # read the mouse's values
            # this is a blocking function
            (left_button, middle_button, right_button, x_axis, y_axis) = getMouseValues(mouse_input)

            # if we have the first choice (see the menu)
            if choice == 1:

                # when both the mouse's buttons are pressed
                # move forward
                if left_button == True and right_button == True:
                    robot.forward()
                # when just the left button is pressed
                # move to the left
                elif left_button == True and right_button == False:
                    robot.left()
                # when just the right button is pressed
                # move to the right
                elif left_button == False and right_button == True:
                    robot.right()
                # when the middle button is pressed
                # move backward
                elif middle_button == True:
                    robot.backward()
                # when no button is pressed
                # stop the robot from moving
                elif middle_button == False or (left_button == False and right_button == False):
                    robot.stop()

            # if we have the second choice (see the menu)
            else:

                # if the mouse is moved to the left
                # then move the robot to the left
                if x_axis < -MOUSE_THRESH:
                    robot.left()
                # if the mouse is moved to the right
                # then move the robot to the right
                elif x_axis > MOUSE_THRESH:
                    robot.right()
                # if the mouse is moved backward
                # then move the robot backward
                elif y_axis < -MOUSE_THRESH:
                    robot.backward()
                # if the mouse is moved forward
                # then move the robot forward
                elif y_axis > MOUSE_THRESH:
                    robot.forward()
                # if the mouse is not moving in any direction
                # then stop the robot from moving
                else:
                    robot.stop()

            sleep(0.10)

if __name__ == "__main__":
    # when CTRL-C is pressed, this is will ensure signal_handler is called
    signal.signal(signal.SIGINT, signal_handler)
    Main()
