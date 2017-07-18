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

class GoPiGo3Switcher(object):

    def __init__():
        self.gopigo3 = easy.EasyGoPiGo3()

    def executeJob(self, argument):
        method_name = "_gopigo3_command_" + str(argument)
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
        print("[w key]     : Move the GoPiGo3 forward")
        print("[s key]     : Move the GoPiGo3 backward")
        print("[a key]     : Turn the GoPiGo3 to the left")
        print("[d key]     : Turn the GoPiGo3 to the right")
        print("[x key]     : Stop the GoPiGo3 from moving")
        print("[c key]     : Drive forward for 10 centimeters)
        print("[i key]     : Drive forward for 10 inches")
        print("[e key]     : Drive forward for 360 degrees (aka 1 wheel rotation))
        print("[1 key]     : Turn ON/OFF both blinkers of the GoPiGo3")
        print("[2 key]     : Turn ON/OFF both eyes of the GoPiGo3")
        print("[3 key]     : Change the eyes' color on the go")
        print("[z key]     : Exit")

    def _gopigo3_command_w(self):
        self.gopigo3.forward()

    def _gopigo3_command_x(self):
        self.gopigo3.stop()

def Main():
    #printLogo()
    #printMenu()

    read_character = getch()
    #while not read_character == "z":


if __name__ == "__main__":
    Main()
