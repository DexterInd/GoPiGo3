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
DEBUG = True

def getNorthPoint(imu):
    x, y, z = imu.read_magnetometer()

    heading = -atan2(x, -z) * 180 / pi

    if heading < 0:
        heading += 360
    elif heading > 360:
        heading -= 360

    if 180 < heading <= 360:
        heading -= 360

    return heading


def statisticalNoiseReduction(values, std_factor_threshold = 2):
    if len(values) == 0:
        return []

    valarray = np.array(values)
    mean = valarray.mean()
    standard_deviation = valarray.std()
    # just return if we only got constant values
    if standard_deviation == 0:
        return values

    # remove outlier values which are less and bigger than the average than the calculated threshold
    valarray = valarray[valarray > mean - std_factor_threshold * standard_deviation]
    valarray = valarray[valarray < mean + std_factor_threshold * standard_deviation]

    return list(valarray)


def orientate(trigger, simultaneous_launcher, sensor_queue):

    time_to_put_in_queue = 0.2 # measured in seconds
    time_to_wait_after_error = 0.5 # measured in seconds

    try:
        imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")
    except Exception as msg:
        print(str(msg))
        simultaneous_launcher.abort()

    print("Rotate the GoPiGo3 robot with your hand until it's fully calibrated")
    try:
        compass = imu.BNO055.get_calibration_status()[3]
    except Exception as msg:
        pass
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

    if trigger.is_set() or max_conseq_errors == 0:
        print("IMU sensor is not reacheable or kill event was triggered")
        simultaneous_launcher.abort()
    else:
        state = "fully calibrated"
        print("The GoPiGo3 is " + state)

    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError as msg:
        print("[orientate] thread couldn't fully start up")

    while not (trigger.is_set() or simultaneous_launcher.broken):
        five_values = 10
        heading_list = []
        max_conseq_errors = 3

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

        heading_list = statisticalNoiseReduction(heading_list)
        heading_avg = mean(heading_list)

        try:
            sensor_queue.put(heading_avg, timeout = time_to_put_in_queue)
        except queue.Full:
            pass


def robotControl(trigger, simultaneous_launcher, motor_command_queue, sensor_queue):
    # try to connect to the GoPiGo3
    time_to_wait_in_queue = 0.1

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

    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError as msg:
        print("[robotControl] thread couldn't be launched")

    if not simultaneous_launcher.broken:
        gopigo3_robot.stop()
        gopigo3_robot.set_speed(100)

    direction_degrees = None
    move = False
    acceptable_error_percent = 8
    command = "stop"
    rotational_factor = 0.30
    accepted_minimum_by_drivers = 6

    while not (trigger.is_set() or simultaneous_launcher.broken or gopigo3_robot.volt() <= MINIMUM_VOLTAGE):
        try:
            command = motor_command_queue.get(timeout = time_to_wait_in_queue)
            motor_command_queue.task_done()
        except queue.Empty:
            pass

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

        if direction_degrees is not None:
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

            if error >= acceptable_error_percent and abs(how_much_to_rotate) >= accepted_minimum_by_drivers:
                gopigo3_robot.turn_degrees(how_much_to_rotate, blocking = True)

        if move is False:
            gopigo3_robot.stop()
        else:
            gopigo3_robot.forward()

    if not simultaneous_launcher.broken:
        gopigo3_robot.stop()


def Main(trigger):
    simultaneous_launcher = threading.Barrier(3)
    motor_command_queue = queue.Queue(maxsize = 2)
    sensor_queue = queue.Queue(maxsize = 1)
    keyboard_refresh_rate = 20.0
    available_commands = {"<LEFT>": "west",
                          "<RIGHT>": "east",
                          "<UP>": "north",
                          "<DOWN>": "south",
                          "<SPACE>": "stop",
                          "w": "move"}

    orientate_thread = threading.Thread(target = orientate, args = (trigger, simultaneous_launcher, sensor_queue))
    robotcontrol_thread = threading.Thread(target = robotControl, args = (trigger, simultaneous_launcher, motor_command_queue, sensor_queue))
    orientate_thread.start()
    robotcontrol_thread.start()

    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError:
        pass

    with Input(keynames = "curtsies") as input_generator:
        while not (trigger.is_set() or simultaneous_launcher.broken):
            period = 1 / keyboard_refresh_rate
            key = input_generator.send(period)

            if key in available_commands:
                try:
                    motor_command_queue.put_nowait(available_commands[key])
                except queue.Full:
                    pass

    if simultaneous_launcher.broken:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    trigger = threading.Event()
    signal.signal(signal.SIGINT, lambda signum, frame : trigger.set())
    Main(trigger)
