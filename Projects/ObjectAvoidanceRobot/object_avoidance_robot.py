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

from easygopigo3 import EasyGoPiGo3
from gopigo3 import FirmwareVersionError
import sys
import signal
from time import sleep

DEBUG = True
MAX_DISTANCE = 3000 # measured in mm
MIN_DISTANCE = 50 # measured in mm
MAX_SPEED = 300
MIN_SPEED = 100

robot_operating = True

def signal_handler(signal, frame):
    global robot_operating
    print("CTRL-C combination pressed")
    robot_operating = False

def Main():

    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

    try:
        gopigo3 = EasyGoPiGo3()
        distance_sensor = gopigo3.init_distance_sensor()

    except IOError as msg:
        print("GoPiGo3 robot not detected or DistanceSensor not installed.")
        if DEBUG is True:
            print("Debug: " + str(msg))
        sys.exit(1)

    except FirmwareVersionError as msg:
        print("GoPiGo3 firmware needs to updated.")
        if DEBUG is True:
            print("Debug: " + str(msg))
        sys.exit(1)

    except Exception as msg:
        print("Error occurred. Set debug = True to see more.")
        if DEBUG is True:
            print("Debug: " + str(msg))
        sys.exit(1)

    gopigo3_stopped = True
    while robot_operating:
        current_distance = distance_sensor.read_mm()
        determined_speed = 0

        if current_distance < MIN_DISTANCE:
            gopigo3_stopped = True
            gopigo3.stop()

        else:
            gopigo3_stopped = False
            percent_speed = (current_distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)
            determined_speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * percent_speed

            gopigo3.set_speed(determined_speed)
            gopigo3.forward()

        print("Current distance : {:4} Current speed: {:4} mm Stopped: {}".format(current_distance, int(determined_speed), gopigo3_stopped is True ))

        sleep(0.08)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    Main()
