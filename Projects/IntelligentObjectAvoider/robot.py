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

from easygopigo3 import *
from time import sleep
import queue
import threading
import sys
import signal

KEEP_HEADING = -1
MINIMUM_VOLTAGE = 7.0

# Thread-launched function for polling the data from the distance sensor.
# It calculates the best path for the robot and then sends the data
# through a queue to the  thread-launched [robotController] function.
#
# [trigger] is used for stopping the thread when CTRL-C is pressed.
# [put_on_hold] is an Event object called by the other thread when needed.
# [simultaneous_launcher] is a Barrier object used for synchronizing the 2 threads.
# [sensor_queue] is a Queue object used for inter-thread communications
def obstacleFinder(trigger, put_on_hold, simultaneous_launcher, sensor_queue):
    leftmost_degrees = 30
    rightmost_degrees = 150
    middle = 90
    current_servo_position = leftmost_degrees
    step = 10
    servo_delay = 0.05
    wait_before_it_starts = 1.0
    distance_trigger = 0.25
    how_much_to_rotate = 150
    to_the_right = True

    # try to connect to the GoPiGo3
    try:
        gopigo3_robot = EasyGoPiGo3()
    except IOError:
        print("GoPiGo3 robot not detected")
        simultaneous_launcher.abort()

    # initialize a Servo object
    servo = gopigo3_robot.init_servo("SERVO1")

    # try to connect to the distance sensor
    try:
        distance_sensor = gopigo3_robot.init_distance_sensor()
    except IOError:
        print("DistanceSensor couldn't be found")
        simultaneous_launcher.abort()
    except gopigo3.FirmwareVersionError:
        print("GoPiGo3 board needs to be updated")
        simultaneous_launcher.abort()
    except Exception:
        print("Unknown error occurred while instantiating GoPiGo3")
        simultaneous_launcher.abort()

    # rotate the servo to the desired start-up position
    servo.rotate_servo(leftmost_degrees)
    sleep(wait_before_it_starts)

    # check if an error has occurred during all the above processes
    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError:
        print("[obstacleFinder] thread couldn't be launched")

    if not simultaneous_launcher.broken:
        print("[obstacleFinder] thread fully active")

    # and if everything is okay
    # start collecting, interpreting and sending messages
    # to the thread-launched [robotController] function
    while not trigger.is_set() and not simultaneous_launcher.broken:
        anterior_distance = 0
        possible_routes = 0
        deadends = 0

        # if the thread is put on hold by [robotController]
        # then wait until it's allowed to proceed
        if not put_on_hold.is_set():

            # when the servo is rotating to the right
            if to_the_right is True:
                # read the distance to the target at every specific orientation of the servo
                # and go with the best greedy-like solution
                while current_servo_position <= rightmost_degrees:
                    servo.rotate_servo(current_servo_position)
                    sleep(servo_delay)

                    distance = distance_sensor.read()
                    current_servo_position += step
                    possible_routes += 1

                    if distance > distance_trigger:
                        if distance > anterior_distance:
                            sensor_queue.put([distance, current_servo_position - 90])
                            anterior_distance = distance
                        else:
                            sensor_queue.put([KEEP_HEADING, 0])
                    else:
                        anterior_distance = 0
                        sensor_queue.put([0, 0])
                        deadends += 1

                # if the distance sensor couldn't found a route
                if deadends == possible_routes:
                    # then rotate a lot in order to find a new spot
                    sensor_queue.put([0, how_much_to_rotate])

                to_the_right = False
                current_servo_position = rightmost_degrees

            # when the servo is rotating to the left
            elif to_the_right is False:
                # read the distance to the target at every specific orientation of the servo
                # and go with the best greedy-like solution
                while current_servo_position >= leftmost_degrees:
                    servo.rotate_servo(current_servo_position)
                    sleep(servo_delay)

                    distance = distance_sensor.read()
                    current_servo_position -= step
                    possible_routes += 1

                    if distance > distance_trigger:
                        if distance > anterior_distance:
                            sensor_queue.put([distance, current_servo_position - 90])
                            anterior_distance = distance
                        else:
                            sensor_queue.put([KEEP_HEADING, 0])
                    else:
                        anterior_distance = 0
                        sensor_queue.put([0, 0])
                        deadends += 1

                # if the distance sensor couldn't found a route
                if deadends == possible_routes:
                    # then rotate a lot in order to find a new spot
                    sensor_queue.put([0, how_much_to_rotate])

                to_the_right = True
                current_servo_position = leftmost_degrees

        else:
            sleep(0.01)

    # move the servo to the middle when the thread is being stopped
    servo.rotate_servo(middle)


def robotController(trigger, put_on_hold, simultaneous_launcher, sensor_queue):
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

    # set a lower speed of the GoPiGo3
    gopigo3_robot.set_speed(200)
    gopigo3_robot.stop() # in case the GoPiGo3 is moving, stop it
    previous = 0 # see the following instructions
    how_much_of_distance = 0.30 # measured in percentage

    # if the robot is unplugged from the battery pack
    # or if the batteries are low
    # then abort everything
    if gopigo3_robot.volt() <= MINIMUM_VOLTAGE:
        print("Voltage too low")
        simultaneous_launcher.abort()

    # check if an error has occurred during all the above processes
    try:
        simultaneous_launcher.wait()
    except threading.BrokenBarrierError:
        print("[robotController] thread couldn't be launched")

    if not simultaneous_launcher.broken:
        print("[robotController] thread fully active")

    # if everything is fine
    # start polling messages from [obstacleFinder] function (which is thread-launched)
    while not trigger.is_set() and not simultaneous_launcher.broken:
        try:
            (distance_to_walk, rotation) = sensor_queue.get_nowait()
            sensor_queue.task_done()
        except queue.Empty:
            sleep(0.001)
            continue

        # if we need to rotate the GoPiGo3
        if rotation > 0:
            put_on_hold.set()
            gopigo3_robot.turn_degrees(rotation, blocking = True)
            put_on_hold.clear()

        # if we need to move the GoPiGo3 around
        if previous != 0 and distance_to_walk >= 0:
            gopigo3_robot.drive_cm(distance_to_walk * how_much_of_distance)

        # keep the previous distance we read
        # if it's 0 now and the next time is still 0
        # then the drive method won't be called
        previous = distance_to_walk

        sleep(0.001)

    # stop the motors when the thread is being stopped
    gopigo3_robot.stop()


def Main(trigger):
    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

    print("Let your GoPiGo3 move around and avoid any obstacles.")
    print("Pay attention to how your GoPiGo3 moves around.")
    print("Avoid sharp corners / edges as the algorithm wasn't made for advanced stuff.")

    # Event object for letting one thread
    # control the other thread's flow control
    put_on_hold = threading.Event()
    # used for synchronizing the threads
    simultaneous_launcher = threading.Barrier(2)
    # for exchanging messages between threads
    sensor_queue = queue.Queue()

    print("\nWaiting threads to fire up")

    path_finder = threading.Thread(target=obstacleFinder, args=(trigger, put_on_hold, simultaneous_launcher, sensor_queue))
    controller = threading.Thread(target=robotController, args=(trigger, put_on_hold, simultaneous_launcher, sensor_queue))

    # start the threads
    path_finder.start()
    controller.start()

    # wait for the user to press CTRL-C
    # or to have an error while firing up the threads
    while not trigger.is_set() and not simultaneous_launcher.broken:
        sleep(0.001)
    # if an error was encountered
    if simultaneous_launcher.broken:
        # then exit the script
        sys.exit(1)

    # otherwise, just wait for the threads to finish
    path_finder.join()
    controller.join()

    # and then exit successfully
    sys.exit(0)

if __name__ == "__main__":
    exit_trigger = threading.Event()
    # CTRL-C signal handler
    # used a lambda, because a proper function is too much code
    signal.signal(signal.SIGINT, lambda signum, frame: exit_trigger.set())
    Main(exit_trigger)

##################################
# Heavy-math project on avoiding #
# objects while continuously     #
# reading with the distance      #
# sensor - vezi desen scanat     #
##################################
"""
def offset_movement(values):

    # distanta maxima de intoarcere permisa pe o intoarcere completa a servomoturlui este limitata la 40 de grade.
    # the maximum number of degrees the robot can turn on a full turn of the servomotor is 40 degrees.

    DEGREE = 0
    DIST = 1
    ORIENTATION = 2
    TARGET = 3
    print("=========================")
    for step in range(1, len(values)):

        # aici se calculeaza proiectia vectorului pe traiectoria normala a robotului
        # here is the vector's projection on the normal (original) trajectory of the robot
        a = values[step - 1][DIST]
        b = values[step][DIST]
        degrees = values[step][DEGREE]
        values[step][DIST] = sqrt(pow(a, 2) + pow(b, 2) - 2 * a * b * cos(degrees * pi / 180))
        values[step][DEGREE] += values[step - 1][DEGREE]

        # se calculeaza proiectia vectorului a obstacolului
        # calculate the obstacle vector's projection
        target_orientation_degrees = values[step][ORIENTATION] - 90
        target_orientation_radians = target_orientation_degrees * pi / 180
        target_projection = (values[step][TARGET] / 100) * cos(target_orientation_radians)

        # aici sunt calculate proiectiile unghiului de vizibilitate
        # interiorul se refera la latura mai apropriata de traiectoria normala a robotului
        # here you can find the projections of the viewing angle
        robot_path_projection_interior = values[step][DIST] * sin(120 * pi / 180) / sin((180 - 120 - abs(values[step][DEGREE])) * pi / 180)
        y1 = values[step][DIST] * sin(values[step][DEGREE] * pi / 180) / sin((180 - 120 - abs(values[step][DEGREE])) * pi / 180)
        y2 = 2.20 # max measure-able distance
        angle_y1y2 = 120
        b = sqrt(pow(y1,2) + pow(y2,2) - 2 * y1 * y2 * cos(angle_y1y2))
        A = (90 - (180 - 120 - abs(values[step][DEGREE]))) * pi / 180 - acos((pow(y1, 2) + pow(b, 2) - pow(y2,2)) / (y1 * b))
        B = (180 - 90) * pi / 180 - A
        # exteriorul se refera la latura mai departata de traiectoria normala a robotului (horizontala)
        # the exterior refers to the edge that's further from the normal trajectory of the robot
        robot_path_projection_exterior = robot_path_projection_interior - b * sin(A) / sin(B)

        print(robot_path_projection_interior)
        print(robot_path_projection_exterior)

        #print(values[step][ORIENTATION], values[step][TARGET], target_projection * 100)
"""

"""
# asta intra in obstacleFinder, in whileul cel mare
(now_left_motor, now_right_motor) = gopigo3.read_encoders()
diff_left_motor = left_motor_position - now_left_motor
diff_right_motor = right_motor_position - now_right_motor
# how much it rotated in degrees around the circle - positive for going to the right, negative for going to the left
how_much_rotated = (diff_right_motor - diff_left_motor) / (
    gopigo3.WHEEL_BASE_WIDTH * 2 / gopigo3.WHEEL_DIAMETER)
# how much it moved (in meters)
how_much_moved = (min([diff_left_motor, diff_right_motor]) / 360) * (gopigo3.WHEEL_CIRCUMFERENCE / 1000)
distance_from_target = distance_sensor.read()
distance_values.append([how_much_rotated, how_much_moved, current_servo_position, distance_from_target])

current_servo_position += step
(left_motor_position, right_motor_position) = gopigo3.read_encoders()
"""
