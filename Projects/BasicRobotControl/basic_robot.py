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
from builtins import input

import easygopigo3 as easy

def getch():
    import termios
    import sys, tty
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    return _getch()

class GoPiGo3WithKeyboard(object):

    KEY_DESCRIPTION = 0
    KEY_FUNC_SUFFIX = 1

    left_blinker_on = False
    right_blinker_on = False

    left_eye_on = False
    right_eye_on = False

    def __init__(self):
        self.gopigo3 = easy.EasyGoPiGo3()
        self.keybindings = {
        "w" : ["Move the GoPiGo3 forward", "forward"],
        "s" : ["Move the GoPiGo3 backward", "backward"],
        "a" : ["Turn the GoPiGo3 to the left", "left"],
        "d" : ["Turn the GoPiGo3 to the right", "right"],
        "x" : ["Stop the GoPiGo3 from moving", "stop"],
        "c" : ["Drive forward for 10 centimeters", "forward10cm"],
        "i" : ["Drive forward for 10 inches", "forward10in"],
        "e" : ["Drive forward for 360 degrees (aka 1 wheel rotation)", "forwardturn"],
        "1" : ["Turn ON/OFF both blinkers of the GoPiGo3","blinkers"],
        "2" : ["Turn ON/OFF both eyes of the GoPiGo3", "eyes"],
        "3" : ["Change the eyes' color on the go", "eyescolor"],
        "z" : ["Exit", "exit"],
        }

    def executeKeyboardJob(self, argument):
        method_prefix = "_gopigo3_command_"
        method_suffix = str(self.keybindings[argument][self.KEY_FUNC_SUFFIX])
        method_name = method_prefix + method_suffix

        method = getattr(self, method_name, lambda : "nothing")

        return method()

    def drawLogo(self):
        print("   _____       _____ _  _____         ____  ")
        print("  / ____|     |  __ (_)/ ____|       |___ \ ")
        print(" | |  __  ___ | |__) || |  __  ___     __) |")
        print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
        print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
        print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
        print("                                            ")

    def drawMenu(self):
        order_of_keys = ["w", "s", "a", "d", "x", "c", "i", "e", "1", "2", "3", "z"]
        for key in order_of_keys:
            print("[key {}] :  {}".format(key, self.keybindings[key][self.KEY_DESCRIPTION]))

    def _gopigo3_command_forward(self):
        self.gopigo3.forward()

        return "done"

    def _gopigo3_command_stop(self):
        self.gopigo3.stop()

        return "done"

    def _gopigo3_command_left(self):
        self.gopigo3.left()

        return "done"

    def _gopigo3_command_right(self):
        self.gopigo3.right()

        return "done"

    def _gopigo3_command_stop(self):
        self.gopigo3.stop()

        return "done"

    def _gopigo3_command_forward10cm(self):
        self.gopigo3.drive_cm(10)

        return "done"

    def _gopigo3_command_forward10in(self):
        self.gopigo3.drive_in(10)

        return "done"

    def _gopigo3_command_forwardturn(self):
        self.gopigo3.drive_degrees(10)

        return "done"

    def _gopigo3_command_blinkers(self):
        if self.left_blinker_on is True and self.right_blinker_on is True:
            self.gopigo3.led_off()
        elif self.left_blinker_on is False and self.right_blinker_on is False:
            self.gopigo3.led_on()
        else:
            self.gopigo3.led_off()

        return "done"

    def _gopigo3_command_eyes(self):
        if self.left_eye_on is True and self.right_eye_on is True:
            self.gopigo3.close_eyes()
        elif self.left_eye_on is False and self.right_eye_on is False:
            self.gopigo3.open_eyes()
        else:
            self.gopigo3.close_eyes()

        return "done"

def Main():
    #printLogo()
    #printMenu()

    read_character = getch()
    #while not read_character == "z":


if __name__ == "__main__":
    Main()
