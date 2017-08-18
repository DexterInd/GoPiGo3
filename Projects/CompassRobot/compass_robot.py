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

import queue
import signal
import threading
from math import *
from statistics import mean
from time import sleep

import numpy as np
from curtsies import Input
from di_sensors import inertial_measurement_unit
from easygopigo3 import *

MINIMUM_VOLTAGE = 7.0
DEBUG = False
MOTORS_SPEED = 250 # see documentation
MAGNETIC_DECLINATION = 0


def getNorthPoint(imu):
    """
    Determines the heading of the north point.
    This function doesn't take into account the declination.

    :param imu: It's an InertialMeasurementUnit object.
    :return: The heading of the north point measured in degrees. The north point is found at 0 degrees.

    """

    x, y, z = imu.read_magnetometer()

    # using the x and z axis because the sensor is mounted vertically
    # the sensor's top face is oriented towards the back of the robot
    heading = -atan2(x, -z) * 180 / pi

    # adjust it to 360 degrees range
    if heading < 0:
        heading += 360
    elif heading > 360:
        heading -= 360

    # when the heading is towards the west the heading is negative
    # when the heading is towards the east the heading is positive
    if 180 < heading <= 360:
        heading -= 360

    heading += MAGNETIC_DECLINATION

    return heading


def statisticalNoiseReduction(values, std_factor_threshold = 2):
    """
    Eliminates outlier values that go beyond a certain threshold.

    :param values: The list of elements that are being filtered.
    :param std_factor_threshold: Filtering aggressiveness. The bigger the value, the more it filters.
    :return: The filtered list.

    """

    if len(values) == 0:
        return []

    valarray = np.array(values)
    mean = valarray.mean()
    standard_deviation = valarray.std()
    # just return if we only got constant values
    if standard_deviation == 0:
        return values

    # remove outlier values
    valarray = valarray[(valarray > mean - std_factor_threshold * standard_deviation)
                        & (valarray < mean + std_factor_threshold * standard_deviation)]

    return list(valarray)


def orientate(trigger, simultaneous_launcher, sensor_queue):
    """
    Thread-launched function for reading the compass data off of the IMU sensor. The data is then
    interpreted and then it's loaded in a queue.

    :param trigger: CTRL-C event. When it's set, it means CTRL-C was pressed and the thread needs to stop.
    :param simultaneous_launcher: It's a barrier used for synchronizing all threads together.
    :param sensor_queue: Queue where the processed data of the compass is put in.
    :return: Nothing.

    """

    time_to_put_in_queue = 0.2 # measured in seconds
    time_to_wait_after_error = 0.5 # measured in seconds

    # try instantiating an InertialMeasurementUnit object
    try:
        imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")
    except Exception as msg:
        print(str(msg))
        simultaneous_launcher.abort()

    # start the calibrating process of the compass
    print("Rotate the GoPiGo3 robot with your hand until it's fully calibrated")
    try:
        compass = imu.BNO055.get_calibration_status()[3]
    except Exception as msg:
        compass = 0
    values_already_printed = []
    max_conseq_errors = 3

    while compass != 3 and not trigger.is_set() and max_conseq_errors > 0:
        state = ""
        if compass == 0:
            state = "not yet calibrated"
        elif compass == 1:
            state = "partially calibrated"
        elif compass == 2:
            state = "almost calibrated"

        if not compass in values_already_printed:
            print("The GoPiGo3 is " + state)
        values_already_printed.append(compass)

        try:
            compass = imu.BNO055.get_calibration_status()[3]
        except Exception as msg:
            max_conseq_errors -= 1
            sleep(time_to_wait_after_error)
            continue

    # if CTRL-C was triggered or if the calibration failed
    # then abort everything
    if trigger.is_set() or max_conseq_errors == 0:
        print("IMU sensor is not reacheable or kill event was triggered")
        simultaneous_launcher.abort()
    else:
        state = "fully calibrated"
        print("The GoPiGo3 is " + state)

    # point of synchronizing all threads together (including main)
    # it fails if abort method was called
    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError as msg:
        print("[orientate] thread couldn't fully start up")

    # while CTRl-C is not pressed and while the synchronization went fine
    while not (trigger.is_set() or simultaneous_launcher.broken):
        five_values = 10
        heading_list = []
        max_conseq_errors = 3

        # get the north point
        # extract a couple of values before going to the next procedure
        while five_values > 0 and max_conseq_errors > 0:
            try:
                heading_list.append(getNorthPoint(imu))
            except Exception as msg:
                max_conseq_errors -= 1
                sleep(time_to_wait_after_error)
                continue
            five_values -= 1
        if max_conseq_errors == 0:
            print("IMU is not reacheable")
            trigger.set()
            break

        # apply some filtering
        heading_list = statisticalNoiseReduction(heading_list)
        heading_avg = mean(heading_list)

        # and then try to put it in the queue
        # if the queue is full, then just go to the next iteration of the while loop
        try:
            sensor_queue.put(heading_avg, timeout = time_to_put_in_queue)
        except queue.Full:
            pass


def robotControl(trigger, simultaneous_launcher, motor_command_queue, sensor_queue):
    """
    Thread-launched function for orientating the robot around. It gets commands from the keyboard as well
    as data from the sensor through the sensor_queue queue.

    :param trigger: CTRL-C event. When it's set, it means CTRL-C was pressed and the thread needs to stop.
    :param simultaneous_launcher: It's a barrier used for synchronizing all threads together.
    :param motor_command_queue: Queue containing commands from the keyboard. The commands are read from within main.
    :param sensor_queue: Processed data off of the IMU. The queue is intended to be read.
    :return: Nothing.

    """

    time_to_wait_in_queue = 0.1 # measured in

    # try to connect to the GoPiGo3
    try:
        gopigo3_robot = EasyGoPiGo3()
    except IOError:
        print("GoPiGo3 robot not detected")
        simultaneous_launcher.abort()
    except gopigo3.FirmwareVersionError:
        print("GoPiGo3 board needs to be updated")
        simultaneous_launcher.abort()
    except Exception:
        print("Unknown error occurred while instantiating GoPiGo3")
        simultaneous_launcher.abort()

    # synchronizing point between all threads
    # if abort method was called, then the synch will fail
    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError as msg:
        print("[robotControl] thread couldn't be launched")

    # if threads were successfully synchronized
    # then set the GoPiGo3 appropriately
    if not simultaneous_launcher.broken:
        gopigo3_robot.stop()
        gopigo3_robot.set_speed(MOTORS_SPEED)

    direction_degrees = None
    move = False
    acceptable_error_percent = 8
    command = "stop"
    rotational_factor = 0.30
    accepted_minimum_by_drivers = 6

    # while CTRL-C is not pressed, the synchronization between threads didn't fail and while the batteries' voltage isn't too low
    while not (trigger.is_set() or simultaneous_launcher.broken or gopigo3_robot.volt() <= MINIMUM_VOLTAGE):
        # read from the queue of the keyboard
        try:
            command = motor_command_queue.get(timeout = time_to_wait_in_queue)
            motor_command_queue.task_done()
        except queue.Empty:
            pass

        # make some selection depending on what every command represents
        if command == "stop":
            move = False
        elif command == "move":
            move = True
        if command == "west":
            direction_degrees = -90.0
        elif command == "east":
            direction_degrees = 90.0
        elif command == "north":
            direction_degrees = 0.0
        elif command == "south":
            direction_degrees = 180.0

        # if a valid orientation was selected
        if direction_degrees is not None:
            # read data and calculate orientation
            heading = sensor_queue.get()
            if direction_degrees == 180.0:
                heading_diff = (direction_degrees - abs(heading)) * (-1 if heading < 0 else 1)
                error = abs(heading_diff / direction_degrees) * 100
            else:
                heading_diff = direction_degrees - heading
                error = abs(heading_diff / 180) * 100

            how_much_to_rotate = int(heading_diff * rotational_factor)

            if DEBUG is True:
                print("direction_degrees {} heading {} error {} heading_diff {}".format(direction_degrees, heading, error, heading_diff))

            # check if the heading isn't so far from the desired orientation
            # if it needs correction, then rotate the robot
            if error >= acceptable_error_percent and abs(how_much_to_rotate) >= accepted_minimum_by_drivers:
                gopigo3_robot.turn_degrees(how_much_to_rotate, blocking = True)

        # command for making the robot move of stop
        if move is False:
            gopigo3_robot.stop()
        else:
            gopigo3_robot.forward()

        sleep(0.001)

    # if the synchronization wasn't broken
    # then stop the motors in case they were running
    if not simultaneous_launcher.broken:
        gopigo3_robot.stop()


def Main(trigger):
    """
    Main thread where the other 2 threads are started, where the keyboard is being read and
    where everything is brought together.

    :param trigger: CTRL-C event. When it's set, it means CTRL-C was pressed and all threads are ended.
    :return: Nothing.

    """
    simultaneous_launcher = threading.Barrier(3) # synchronization object
    motor_command_queue = queue.Queue(maxsize = 2) # queue for the keyboard commands
    sensor_queue = queue.Queue(maxsize = 1) # queue for the IMU sensor
    keyboard_refresh_rate = 20.0 # how many times a second the keyboard should update
    available_commands = {"<LEFT>": "west",
                          "<RIGHT>": "east",
                          "<UP>": "north",
                          "<DOWN>": "south",
                          "<SPACE>": "stop",
                          "w": "move"} # the selectable options within the menu
    menu_order = ["<LEFT>", "<RIGHT>", "<UP>", "<DOWN>", "<SPACE>", "w"] # and the order of these options

    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

    # starting the workers/threads
    orientate_thread = threading.Thread(target = orientate, args = (trigger, simultaneous_launcher, sensor_queue))
    robotcontrol_thread = threading.Thread(target = robotControl, args = (trigger, simultaneous_launcher, motor_command_queue, sensor_queue))
    orientate_thread.start()
    robotcontrol_thread.start()

    # if the threads couldn't be launched, then don't display anything else
    try:
        simultaneous_launcher.wait()

        print("Press the following keys for moving/orientating the robot by the 4 cardinal points")
        for menu_command in menu_order:
            print("{:8} - {}".format(menu_command, available_commands[menu_command]))
    except threading.BrokenBarrierError:
        pass

    # read the keyboard as long as the synchronization between threads wasn't broken
    # and while CTRL-C wasn't pressed
    with Input(keynames = "curtsies") as input_generator:
        while not (trigger.is_set() or simultaneous_launcher.broken):
            period = 1 / keyboard_refresh_rate
            key = input_generator.send(period)

            if key in available_commands:
                try:
                    motor_command_queue.put_nowait(available_commands[key])
                except queue.Full:
                    pass

    # exit codes depending on the issue
    if simultaneous_launcher.broken:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    trigger = threading.Event() # event used when CTRL-C is pressed
    signal.signal(signal.SIGINT, lambda signum, frame : trigger.set()) # SIGINT (CTRL-C) signal handler
    Main(trigger)
