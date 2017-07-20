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

import random
import easygopigo3 as easy
import threading
from time import sleep

class GoPiGo3WithKeyboard(object):
    """
    Class for interfacing with the GoPiGo3.
    It's functionality is to map different keys
    of the keyboard to different commands of the GoPiGo3.
    """

    KEY_DESCRIPTION = 0
    KEY_FUNC_SUFFIX = 1

    left_blinker_on = False
    right_blinker_on = False

    left_eye_on = False
    right_eye_on = False

    def __init__(self):
        """
        Instantiates the key-bindings between the GoPiGo3 and the keyboard's keys.
        Sets the order of the keys in the menu.
        """
        self.gopigo3 = easy.EasyGoPiGo3()
        self.keybindings = {
        "<F1>" : ["Turn SERVO1 completely to the left.", "leftservo1_immediately"],
        "<F2>" : ["Turn SERVO1 completely to the right.", "rightservo1_immediately"],
        "<F5>" : ["Turn SERVO2 completely to the left.", "leftservo1_immediately"],
        "<F6>" : ["Turn SERVO2 completely to the right.", "rightservo2_immediately"],
        "<SPACE>" : ["Reset both servos to the original position.", "reset"],

        "a" : ["Turn SERVO1 to the left incrementely.", "leftservo1_incrementally"],
        "d" : ["Turn SERVO1 to the right incrementely.", "rightservo1_incrementally"],

        "<LEFT>" : ["Turn SERVO1 to the left incrementely.", "leftservo1_incrementally"],
        "<RIGHT>" : ["Turn SERVO2 to the right incrementely.", "rightservo1_incrementally"],

        "<ESC>" : ["Exit", "exit"],
        }
        self.order_of_keys = ["<F1>", "<F2>", "<F5>", "<F6>", "<SPACE>", "a", "d", "<LEFT>", "<RIGHT>", "<ESC>"]

    def executeKeyboardJob(self, argument):
        """
        Argument can be any of the strings stored in self.keybindings list.

        For instance: if argument is "w", then the algorithm looks inside self.keybinds dict and finds
        the "forward" value, which in turn calls the "_gopigo3_command_forward" method
        for driving the gopigo3 forward.

        The return values are:
        * "nothing" - when no method could be found for the given argument.
        * "moving" - when the robot has to move forward, backward, to the left or to the right for indefinite time.
        * "path" - when the robot has to move in a direction for a certain amount of time/distance.
        * "static" - when the robot doesn't move in any direction, but instead does static things, such as turning the LEDs ON.
        * "exit" - when the key for exiting the program is pressed.
        """
        method_prefix = "_gopigo3_command_"
        try:
            method_suffix = str(self.keybindings[argument][self.KEY_FUNC_SUFFIX])
        except KeyError:
            method_suffix = ""
        method_name = method_prefix + method_suffix

        method = getattr(self, method_name, lambda : "nothing")

        return method()

    def drawLogo(self):
        """
        Draws the name of the GoPiGo3.
        """
        print("   _____       _____ _  _____         ____  ")
        print("  / ____|     |  __ (_)/ ____|       |___ \ ")
        print(" | |  __  ___ | |__) || |  __  ___     __) |")
        print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
        print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
        print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
        print("                                            ")

    def drawDescription(self):
        """
        Prints details related on how to operate the GoPiGo3.
        """
        print("\nPress the following keys to run the features of the GoPiGo3.")
        print("To move the motors, make sure you have a fresh set of batteries powering the GoPiGo3.\n")

    def drawMenu(self):
        """
        Prints all the key-bindings between the keys and the GoPiGo3's commands on the screen.
        """
        try:
            for key in self.order_of_keys:
                print("\r[key {:8}] :  {}".format(key, self.keybindings[key][self.KEY_DESCRIPTION]))
        except KeyError:
            print("Error: Keys found GoPiGo3WithKeyboard.order_of_keys don't match with those in GoPiGo3WithKeyboard.keybindings.")

    def _gopigo3_command_exit(self):
        return "exit"
