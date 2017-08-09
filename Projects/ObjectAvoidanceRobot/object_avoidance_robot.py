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

DEBUG = False # if set to True, any exception that's encountered is debugged
MAX_DISTANCE = 2300 # measured in mm
MIN_DISTANCE = 150 # measured in mm
NO_OBSTACLE = 3000
ERROR = 0 # the error that's returned when the DistanceSensor is not found
MAX_SPEED = 300 # max speed of the GoPiGo3
MIN_SPEED = 100 # min speed of the GoPiGo3

# variable for triggering the closing procedure of the script
# used for stopping the while loop that's in the Main() function
robot_operating = True

# handles the CTRL-C signal sent from the keyboard
# required for gracefull exits of the script
def signal_handler(signal, frame):
    global robot_operating
    print("CTRL-C combination pressed")
    robot_operating = False

# function for debugging
def debug(string):
    if DEBUG is True:
        print("Debug: " + str(string))

def Main():

    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

    # initializing an EasyGoPiGo3 object and a DistanceSensor object
    # used for interfacing with the GoPiGo3 and with the distance sensor
    try:
        gopigo3 = EasyGoPiGo3()
        distance_sensor = gopigo3.init_distance_sensor()

    except IOError as msg:
        print("GoPiGo3 robot not detected or DistanceSensor not installed.")
        debug(msg)
        sys.exit(1)

    except FirmwareVersionError as msg:
        print("GoPiGo3 firmware needs to updated.")
        debug(msg)
        sys.exit(1)

    except Exception as msg:
        print("Error occurred. Set debug = True to see more.")
        debug(msg)
        sys.exit(1)

    if DEBUG is True:
        distance_sensor.enableDebug()

    # variable that says whether the GoPiGo3 moves or is stationary
    # used during the runtime
    gopigo3_stationary = True

    global robot_operating

    # while the script is running
    while robot_operating:
        # read the distance from the distance sensor
        current_distance = distance_sensor.read_mm()
        determined_speed = 0

        # if the sensor can't be detected
        if current_distance == ERROR:
            print("Cannot reach DistanceSensor. Stopping the process.")
            robot_operating = False

        # if the robot is closer to the target
        elif current_distance < MIN_DISTANCE:
            # then stop the GoPiGo3
            gopigo3_stationary = True
            gopigo3.stop()

        # if the robot is far away from the target
        else:
            gopigo3_stationary = False

            # if the distance sensor can't detect any target
            if current_distance == NO_OBSTACLE:
                # then set the speed to maximum
                determined_speed = MAX_SPEED
            else:
                # otherwise, calculate the speed with respect to the distance from the target
                percent_speed = float(current_distance - MIN_DISTANCE) / (MAX_DISTANCE - MIN_DISTANCE)
                determined_speed = MIN_SPEED + (MAX_SPEED - MIN_SPEED) * percent_speed

            # apply the changes
            gopigo3.set_speed(determined_speed)
            gopigo3.forward()

        # and last, print some stats
        print("Current distance : {:4} mm Current speed: {:4} Stopped: {}".format(current_distance, int(determined_speed), gopigo3_stationary is True ))

        # give it some time,
        # otherwise you'll have a hard time exiting the script
        sleep(0.08)

    # and finally stop the GoPiGo3 from moving
    gopigo3.stop()


if __name__ == "__main__":
    # signal handler
    # handles the CTRL-C combination of keys
    signal.signal(signal.SIGINT, signal_handler)
    Main()
