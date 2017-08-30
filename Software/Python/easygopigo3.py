#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
# from builtins import input

import sys
# import tty
# import select
import time
hardware_connected = True
try:
    import gopigo3
except ImportError:
    hardware_connected = False
    print("Cannot import gopigo3 library")
except Exception as e:
    hardware_connected = False
    print("Unknown issue while importing gopigo3")
    print(e)


# from datetime import datetime

try:
    from I2C_mutex import *

    mutex = True
except:
    mutex = False
    pass
#import DHT
#import grove_rgb_lcd

import os

try:
    from line_follower import line_sensor
    from line_follower import scratch_line

    # is_line_follower_accessible not really used, just in case
    is_line_follower_accessible = True
except:
    try:
        sys.path.insert(0, '/home/pi/GoPiGo/Software/Python/line_follower')
        import line_sensor
        import scratch_line
        is_line_follower_accessible = True
    except:
        is_line_follower_accessible = False

old_settings = ''
fd = ''
##########################

read_is_open = True


def debug(in_str):
    if False:
        print(in_str)


def _grab_read():
    global read_is_open
    try:
        I2C_Mutex_Acquire()
    except:
        pass
    # thread safe doesn't seem to be required so
    # commented out
    # while read_is_open is False:
    #     time.sleep(0.01)
    read_is_open = False
    # print("acquired")


def _release_read():
    global read_is_open
    I2C_Mutex_Release()
    read_is_open = True
    # print("released")

#####################################################################
#
# EASYGOPIGO3
#
#####################################################################


class EasyGoPiGo3(gopigo3.GoPiGo3):
    """
    | This class is used for controlling a `GoPiGo3`_ robot.
    | With this class you can do the following things with your `GoPiGo3`_:

     * drive your robot in any number of directions
     * have precise control over the direction of the robot
     * set the speed of the robot
     * turn *on* or *off* the blinker LEDs
     * control the `GoPiGo3`_' Dex's *eyes*, *color* and so on ...

     .. needs revisiting

     .. warning::

         Without a battery pack connected to the `GoPiGo3`_, the robot won't move.

    """

    def __init__(self):
        """
        | This constructor sets the variables to the following values:

        :var int speed = 300: The speed of the motors should go between **0-1000** DPS.
        :var tuple(int,int,int) left_eye_color = (0,255,255): Set Dex's left eye color to **turqoise**.
        :var tuple(int,int,int) right_eye_color = (0,255,255): Set Dex's right eye color to **turqoise**.
        :var int DEFAULT_SPEED = 300: Starting speed value: not too fast, not too slow.
        :raises IOError: When the GoPiGo3 is not detected. It also debugs a message in the terminal.
        :raises gopigo3.FirmwareVersionError: If the GoPiGo3 firmware needs to be updated. It also debugs a message in the terminal.
        :raises Exception: For any other kind of exceptions.

        """
        try:
            super(self.__class__, self).__init__()
        except IOError as e:
            print("FATAL ERROR:\nGoPiGo3 is not detected.")
            raise e
        except gopigo3.FirmwareVersionError as e:
            print("FATAL ERROR:\nTo update the firmware on Raspbian for Robots you need to run DI Software Update and choose Update Robot")
            raise e
        except Exception as e:
            raise e

        self.sensor_1 = None
        self.sensor_2 = None
        self.DEFAULT_SPEED=300
        self.set_speed(self.DEFAULT_SPEED)
        self.left_eye_color = (0, 255, 255)
        self.right_eye_color = (0, 255, 255)

    def volt(self):
        """
        | This method returns the battery voltage of the `GoPiGo3`_.

        :return: The battery voltage of the `GoPiGo3`_.
        :rtype: float

        """
        voltage = self.get_voltage_battery()
        return voltage

    def set_speed(self, in_speed):
        """
        | This method sets the speed of the `GoPiGo3`_ specified by ``in_speed`` argument.
        | The speed is measured in *DPS = degrees per second* of the robot's wheel(s).

        :param int in_speed: The speed at which the robot is set to run - speed between **0-1000** DPS.

        .. warning::

             **0-1000** DPS are the *preferred* speeds for the `GoPiGo3`_ robot.
             The speed variable can be basically set to any positive value, but factors like *voltage*, *load*, *battery amp rating*, etc, will determine the effective speed of the motors.

             Experiments should be run by every user, as each case is unique.

        """
        try:
            self.speed = int(in_speed)
        except:
            self.speed = self.DEFAULT_SPEED
        self.set_motor_limits(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                              dps=self.speed)

    def get_speed(self):
        """
        | Use this method for getting the speed of your `GoPiGo3`_.

        :return: The speed of the robot measured between **0-1000** DPS.
        :rtype: int

        """
        return int(self.speed)

    def reset_speed(self):
        """
        | This method resets the speed to its original value.

        """
        self.set_speed(self.DEFAULT_SPEED)

    def stop(self):
        """
        | This method stops the `GoPiGo3`_ from moving.
        | It brings the `GoPiGo3`_ to a full stop.

        .. note::

             This method is used in conjuction with the following methods:

                 * :py:meth:`~easygopigo3.EasyGoPiGo3.backward`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.right`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.left`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.forward`

        """
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)


    def backward(self):
        """
        | Move the `GoPiGo3`_ backward.

        | For setting the motor speed, use :py:meth:`~easygopigo3.EasyGoPiGo3.set_speed`.
        | Default ``speed`` is set ``300`` - see :py:meth:`~easygopigo3.EasyGoPiGo3.__init__`.

        """
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed() * -1)

    def right(self):
        """
        | Move the `GoPiGo3`_ to the right.

        | For setting the motor speed, use :py:meth:`~easygopigo3.EasyGoPiGo3.set_speed`.
        | Default ``speed`` is set to **300** - see :py:meth:`~easygopigo3.EasyGoPiGo3.__init__`.

        .. important::
             | The robot will activate only the left motor, whilst the right motor will be completely stopped.
             | This causes the robot to rotate in very short circles.

        """
        self.set_motor_dps(self.MOTOR_LEFT, self.get_speed())
        self.set_motor_dps(self.MOTOR_RIGHT, 0)

    def left(self):
        """
        | Move the `GoPiGo3`_ to the left.

        | For setting the motor speed, use :py:meth:`~easygopigo3.EasyGoPiGo3.set_speed`.
        | Default ``speed`` is set to **300** - see :py:meth:`~easygopigo3.EasyGoPiGo3.__init__`.

        .. important::
             | The robot will activate only the right motor, whilst the left motor will be completely stopped.
             | This causes the robot to rotate in very short circles.

        """
        self.set_motor_dps(self.MOTOR_LEFT, 0)
        self.set_motor_dps(self.MOTOR_RIGHT, self.get_speed())

    def forward(self):
        """
        | Move the `GoPiGo3`_ forward.

        | For setting the motor speed, use :py:meth:`~easygopigo3.EasyGoPiGo3.set_speed`.
        | Default ``speed`` is set to **300** - see :py:meth:`~easygopigo3.EasyGoPiGo3.__init__`.

        """
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed())

    def drive_cm(self, dist, blocking=True):
        """
        | Move the `GoPiGo3`_ forward / backward for ``dist`` amount of centimeters.

        | For moving the `GoPiGo3`_ robot forward, the ``dist`` parameter has to be *positive*.
        | For moving the `GoPiGo3`_ robot backward, the ``dist`` parameter has to be *negative*.

        :param float dist: The distance in ``cm`` the `GoPiGo3`_ has to move.
        :param boolean blocking = True: Set it as a blocking or non-blocking method.

        ``blocking`` parameter can take the following values:

             * ``True`` so that the method will wait for the `GoPiGo3`_ robot to finish moving.
             * ``False`` so that the method will exit immediately while the `GoPiGo3`_ robot will continue moving.

        """
        # dist is in cm
        # if dist is negative, this becomes a backward move

        dist_mm = dist * 10

        # the number of degrees each wheel needs to turn
        WheelTurnDegrees = ((dist_mm / self.WHEEL_CIRCUMFERENCE) * 360)

        # get the starting position of each motor
        StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
        StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

        self.set_motor_position(self.MOTOR_LEFT,
                                (StartPositionLeft + WheelTurnDegrees))
        self.set_motor_position(self.MOTOR_RIGHT,
                                (StartPositionRight + WheelTurnDegrees))

        if blocking:
            while self.target_reached(
                    StartPositionLeft + WheelTurnDegrees,
                    StartPositionRight + WheelTurnDegrees) is False:
                time.sleep(0.1)

    def drive_inches(self, dist, blocking=True):
        """
        | Move the `GoPiGo3`_ forward / backward for ``dist`` amount of inches.

        | For moving the `GoPiGo3`_ robot forward, the ``dist`` parameter has to be *positive*.
        | For moving the `GoPiGo3`_ robot backward, the ``dist`` parameter has to be *negative*.

        :param float dist: The distance in ``inches`` the `GoPiGo3`_ has to move.
        :param boolean blocking = True: Set it as a blocking or non-blocking method.

        ``blocking`` parameter can take the following values:

             * ``True`` so that the method will wait for the `GoPiGo3`_ robot to finish moving.
             * ``False`` so that the method will exit immediately while the `GoPiGo3`_ robot will continue moving.

        """
        self.drive_cm(dist * 2.54, blocking)

    def drive_degrees(self, degrees, blocking=True):
        """
        | Move the `GoPiGo3`_ forward / backward for ``degrees / 360`` wheel rotations.

        | For moving the `GoPiGo3`_ robot forward, the ``degrees`` parameter has to be *positive*.
        | For moving the `GoPiGo3`_ robot backward, the ``degrees`` parameter has to be *negative*.

        :param float degrees: Distance based on how many wheel rotations are made. Calculated by ``degrees / 360``.
        :param boolean blocking = True: Set it as a blocking or non-blocking method.

        ``blocking`` parameter can take the following values:

             * ``True`` so that the method will wait for the `GoPiGo3`_ robot to finish rotating.
             * ``False`` so that the method will exit immediately while the `GoPiGo3`_ robot will continue rotating.

        For instance, the following function call is going to drive the `GoPiGo3`_ robot forward for *310 / 360* wheel rotations, which equates to aproximately *86%*
        of the `GoPiGo3`_'s wheel circumference.

        .. code-block:: python

            gpg3_obj.drive_degrees(310)

        On the other hand, changing the polarity of the argument we're passing, is going to make the `GoPiGo3`_ robot move backward.

        .. code-block:: python

            gpg3_obj.drive_degrees(-30.5)

        This line of code is makes the `GoPiGo3`_ robot backward for *30.5 / 360* rotations, which is roughly *8.5%* of the `GoPiGo3`_'s wheel circumference.

        """
        # these degrees are meant to be wheel rotations.
        # 360 degrees would be a full wheel rotation
        # not the same as turn_degrees() which is a robot rotation
        # degrees is in degrees, not radians
        # if degrees is negative, this becomes a backward move

        # get the starting position of each motor
        StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
        StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

        self.set_motor_position(self.MOTOR_LEFT,
                                (StartPositionLeft + degrees))
        self.set_motor_position(self.MOTOR_RIGHT,
                                (StartPositionRight + degrees))


        if blocking:
            while self.target_reached(
                    StartPositionLeft + degrees,
                    StartPositionRight + degrees) is False:
                time.sleep(0.1)
        return

    def target_reached(self, left_target_degrees, right_target_degrees):
        """
        | Checks if :

             * The left *wheel* has rotated for ``left_target_degrees`` degrees.
             * The right *wheel* has rotated for ``right_target_degrees`` degrees.

        | If both conditions are met, it returns ``True``, otherwise it's ``False``.

        :param int left_target_degrees: Target degrees for the *left* wheel.
        :param int right_target_degrees: Target degrees for the *right* wheel.

        :return: Whether both wheels have reached their target.
        :rtype: boolean.

        For checking if the `GoPiGo3`_ robot has moved **forward** for ``360 / 360`` wheel rotations, we'd use the following code snippet.

        .. code-block:: python

            # both variables are measured in degrees
            left_motor_target = 360
            right_motor_target = 360

            # reset the encoders
            gpg3_obj.reset_encoders()
            # and make the robot move forward
            gpg3_obj.forward()

            while gpg3_obj.target_reached(left_motor_target, right_motor_target):
                # give the robot some time to move
                sleep(0.05)

            # now lets stop the robot
            # otherwise it would keep on going
            gpg3_obj.stop()

        On the other hand, for moving the `GoPiGo3`_ robot to the **right** for ``187 / 360`` wheel rotations of the left wheel, we'd use the following code snippet.

        .. code-block:: python

            # both variables are measured in degrees
            left_motor_target = 187
            right_motor_target = 0

            # reset the encoders
            gpg3_obj.reset_encoders()
            # and make the robot move to the right
            gpg3_obj.right()

            while gpg3_obj.target_reached(left_motor_target, right_motor_target):
                # give the robot some time to move
                sleep(0.05)

            # now lets stop the robot
            # otherwise it would keep on going
            gpg3_obj.stop()

        .. note::

            You *can* use this method in conjuction with the following methods:

                 * :py:meth:`~easygopigo3.EasyGoPiGo3.drive_cm`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.drive_inches`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.drive_degrees`

            when they are used in *non-blocking* mode.

            And almost *everytime* with the following ones:

                 * :py:meth:`~easygopigo3.EasyGoPiGo3.backward`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.right`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.left`
                 * :py:meth:`~easygopigo3.EasyGoPiGo3.forward`

        """
        tolerance = 5
        min_left_target = left_target_degrees - tolerance
        max_left_target = left_target_degrees + tolerance
        min_right_target = right_target_degrees - tolerance
        max_right_target = right_target_degrees + tolerance

        current_left_position = self.get_motor_encoder(self.MOTOR_LEFT)
        current_right_position = self.get_motor_encoder(self.MOTOR_RIGHT)

        if current_left_position > min_left_target and \
           current_left_position < max_left_target and \
           current_right_position > min_right_target and \
           current_right_position < max_right_target:
            return True
        else:
            return False

    def reset_encoders(self):
        """
        | Resets both the encoders back to **0**.

        | When keeping track of the `GoPiGo3`_ movements, this method is exclusively being required by the following methods:

             * :py:meth:`~easygopigo3.EasyGoPiGo3.backward`
             * :py:meth:`~easygopigo3.EasyGoPiGo3.right`
             * :py:meth:`~easygopigo3.EasyGoPiGo3.left`
             * :py:meth:`~easygopigo3.EasyGoPiGo3.forward`

        """
        self.set_motor_power(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)
        self.offset_motor_encoder(self.MOTOR_LEFT,self.get_motor_encoder(self.MOTOR_LEFT))
        self.offset_motor_encoder(self.MOTOR_RIGHT,self.get_motor_encoder(self.MOTOR_RIGHT))

    def read_encoders(self):
        """
        | Reads the encoders' position in degrees. 360 degrees represent 1 full rotation (or 360 degrees) of a wheel.

        :returns: A tuple containing the position in degrees of each encoder. The 1st element is for the left motor and the 2nd is for the right motor.
        :rtype: tuple(int,int)

        """

        left_encoder = self.get_motor_encoder(self.MOTOR_LEFT)
        right_encoder = self.get_motor_encoder(self.MOTOR_RIGHT)
        encoders = (left_encoder, right_encoder)

        return encoders

    def turn_degrees(self, degrees, blocking=False):
        """
        | Makes the `GoPiGo3`_ robot turn at a specific angle while staying in the same spot.

        :param float degrees: The angle in degress at which the `GoPiGo3`_ has to turn. For rotating the robot to the left, ``degrees`` has to negative, and make it turn to the right, ``degrees`` has to be positive.
        :param boolean blocking = False: Set it as a blocking or non-blocking method.

        ``blocking`` parameter can take the following values:

             * ``True`` so that the method will wait for the `GoPiGo3`_ robot to finish moving.
             * ``False`` so that the method will exit immediately while the `GoPiGo3`_ robot will continue moving.

        In order to better understand what does this method do, let's take a look at the following graphical representation.

        .. image:: images/gpg3_robot.svg

        In the image, we have multiple identifiers:

             * The "*heading*": it represents the robot's heading. By default, "rotating" the robot by 0 degrees is going to make the robot stay in place.
             * The "*wheel circle circumference*": this is the circle that's described by the 2 motors moving in opposite direction.
             * The "*GoPiGo3*": the robot we're playing with. The robot's body isn't draw in this representation as it's not the main focus here.
             * The "*wheels*": these are just the `GoPiGo3`_'s wheels - selfexplanatory.

        The effect of this class method is that the `GoPiGo3`_ will rotate in the same spot (depending on ``degrees`` parameter), while the wheels will be describing a perfect circle.

        So, in order to calculate how much the motors have to spin, we divide the *angle* (at which we want to rotate the robot) by 360 degrees and we get a float number between 0 and 1 (think of it as a percentage).
        We then multiply this value with the *wheel circle circumference* (which is the circumference of the circle the robot's wheels describe when rotating in the same place).


        At the end we get the distance each wheel has to travel in order to rotate the robot by ``degrees`` degrees.

        """
        # this is the method to use if you want the robot to turn 90 degrees
        # or any other amount. This method is based on robot orientation
        # and not wheel rotation
        # the distance in mm that each wheel needs to travel
        WheelTravelDistance = ((self.WHEEL_BASE_CIRCUMFERENCE * degrees) / 360)

        # the number of degrees each wheel needs to turn
        WheelTurnDegrees = ((WheelTravelDistance / self.WHEEL_CIRCUMFERENCE) *
                            360)

        # get the starting position of each motor
        StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
        StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

        # Set each motor target
        self.set_motor_position(self.MOTOR_LEFT,
                                (StartPositionLeft + WheelTurnDegrees))
        self.set_motor_position(self.MOTOR_RIGHT,
                                (StartPositionRight - WheelTurnDegrees))

        if blocking:
            while self.target_reached(
                    StartPositionLeft + WheelTurnDegrees,
                    StartPositionRight - WheelTurnDegrees) is False:
                time.sleep(0.1)

    def blinker_on(self, id):
        """
        | Turns *ON* one of the 2 red blinkers that `GoPiGo3`_ has.

        :param int|str id: **0** / **1** for the right / left led or string literals can be used : ``"right"`` and ``"left"``.


        """
        if id == 1 or id == "left":
            self.set_led(self.LED_LEFT_BLINKER, 255)
        if id == 0 or id == "right":
            self.set_led(self.LED_RIGHT_BLINKER, 255)

    def blinker_off(self, id):
        """
        | Turns *OFF* one of the 2 red blinkers that `GoPiGo3`_ has.

        :param int|str id: **0** / **1** for the right / left led or string literals can be used : ``"right"`` and ``"left"``.

        """
        if id == 1 or id == "left":
            self.set_led(self.LED_LEFT_BLINKER, 0)
        if id == 0 or id == "right":
            self.set_led(self.LED_RIGHT_BLINKER, 0)


    def led_on(self, id):
        """
        | Turns *ON* one of the 2 red blinkers that `GoPiGo3`_ has.
        | The same as :py:meth:`~easygopigo3.EasyGoPiGo3.blinker_on`.

        :param int|str id: **0** / **1** for the right / left led or string literals can be used : ``"right"``` and ``"left"``.

        """
        self.blinker_on(id)

    def led_off(self, id):
        """
        | Turns *OFF* one of the 2 red blinkers that `GoPiGo3`_ has.
        | The same as :py:meth:`~easygopigo3.EasyGoPiGo3.blinker_off`.

        :param int|str id: **0** / **1** for the right / left led or string literals can be used : ``"right"`` and ``"left"``.

        """
        self.blinker_off(id)


    def set_left_eye_color(self, color):
        """
        | Sets the LED color for Dexter mascot's left eye.

        :param tuple(int,int,int) color: 8-bit RGB tuple that represents the left eye's color.
        :raises TypeError: When ``color`` parameter is not valid.

        .. important::

             After setting the eye's color, call :py:meth:`~easygopigo3.EasyGoPiGo3.open_left_eye` or :py:meth:`~easygopigo3.EasyGoPiGo3.open_eyes` to update the color,
             or otherwise the left eye's color won't change.

        """
        if isinstance(color, tuple) and len(color) == 3:
            self.left_eye_color = color
        else:
            raise TypeError("Eye color not valid")

    def set_right_eye_color(self, color):
        """
        | Sets the LED color for Dexter mascot's right eye.

        :param tuple(int,int,int) color: 8-bit RGB tuple that represents the right eye's color.
        :raises TypeError: When ``color`` parameter is not valid.

        .. important::

             After setting the eye's color, call :py:meth:`~easygopigo3.EasyGoPiGo3.open_right_eye` or :py:meth:`~easygopigo3.EasyGoPiGo3.open_eyes` to update the color,
             or otherwise the right eye's color won't change.

        """
        if isinstance(color, tuple) and len(color) == 3:
            self.right_eye_color = color
        else:
            raise TypeError("Eye color not valid")

    def set_eye_color(self, color):
        """
        | Sets the LED color for Dexter mascot's eyes.

        :param tuple(int,int,int) color: 8-bit RGB tuple that represents the eyes' color.
        :raises TypeError: When ``color`` parameter is not valid.

        .. important::

             After setting the eyes' color, call :py:meth:`~easygopigo3.EasyGoPiGo3.open_eyes` to update the color of both eyes,
             or otherwise the color won't change.

        """
        self.set_left_eye_color(color)
        self.set_right_eye_color(color)

    def open_left_eye(self):
        """
        | Turns *ON* Dexter mascot's left eye.

        """
        self.set_led(self.LED_LEFT_EYE,
                     self.left_eye_color[0],
                     self.left_eye_color[1],
                     self.left_eye_color[2],
                     )

    def open_right_eye(self):
        """
        | Turns *ON* Dexter mascot's right eye.

        """
        self.set_led(self.LED_RIGHT_EYE,
                     self.right_eye_color[0],
                     self.right_eye_color[1],
                     self.right_eye_color[2],
                     )

    def open_eyes(self):
        """
        | Turns *ON* Dexter mascot's eyes.

        """
        self.open_left_eye()
        self.open_right_eye()

    def close_left_eye(self):
        """
        | Turns *OFF* Dexter mascot's left eye.

        """
        self.set_led(self.LED_LEFT_EYE, 0, 0, 0)

    def close_right_eye(self):
        """
        | Turns *OFF* Dexter mascot's right eye.

        """
        self.set_led(self.LED_RIGHT_EYE, 0, 0, 0)

    def close_eyes(self):
        """
        | Turns *OFF* Dexter mascot's eyes.

        """
        self.close_left_eye()
        self.close_right_eye()

    def init_light_sensor(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.LightSensor` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.LightSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return LightSensor(port, self)

    def init_sound_sensor(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.SoundSensor` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.SoundSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return SoundSensor(port, self)
        
    def init_loudness_sensor(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.LoudnessSensor` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.LoudnessSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return LoudnessSensor(port, self)
               

    def init_ultrasonic_sensor(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.UltraSonicSensor` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.UltraSonicSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return UltraSonicSensor(port, self)

    def init_buzzer(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.Buzzer` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.Buzzer` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return Buzzer(port, self)

    def init_led(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.Led` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.Led` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return Led(port, self)

    def init_button_sensor(self, port = "AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.ButtonSensor` object and then returns it.

        :param str port = "AD1": Can be either ``"AD1"`` or ``"AD2"``. By default it's set to be ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.ButtonSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` and ``"AD2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return ButtonSensor(port, self)

    def init_line_follower(self, port = "I2C"):
        """
        | Initialises a :py:class:`~easygopigo3.LineFollower` object and then returns it.

        :param str port = "I2C": The only option for this parameter is ``"I2C"``. The default value for this parameter is already set to ``"I2C"``.
        :returns: An instance of the :py:class:`~easygopigo3.LineFollower` class and with the port set to ``port``'s value.

        The ``"I2C"`` ports are mapped to the following :ref:`hardware-ports-section`.

        .. tip::

             | The sensor can be connected to any of the I2C ports.
             | You can connect different I2C devices simultaneously provided that:

                * The I2C devices have different addresses.
                * The I2C devices are recognizeable by the `GoPiGo3`_ platform.

        """
        return LineFollower(port, self)

    def init_servo(self, port = "SERVO1"):
        """
        | Initialises a :py:class:`~easygopigo3.Servo` object and then returns it.

        :param str port = "SERVO1": Can be either ``"SERVO1"`` or ``"SERVO2"``. By default it's set to be ``"SERVO1"``.
        :returns: An instance of the :py:class:`~easygopigo3.Servo` class and with the port set to ``port``'s value.

        The ``"SERVO1"`` and ``"SERVO2"`` ports are mapped to the following :ref:`hardware-ports-section`.

        """
        return Servo(port, self)

    def init_distance_sensor(self, port = "I2C"):
        """

        | Initialises a :py:class:`~easygopigo3.DistanceSensor` object and then returns it.

        :param str port = "I2C": the only option for this parameter is ``"I2C"``. The parameter has ``"I2C"`` as a default value.
        :returns: An instance of the :py:class:`~easygopigo3.DistanceSensor` class and with the port set to ``port``'s value.

        The ``"I2C"`` ports are mapped to the following :ref:`hardware-ports-section`.

        .. tip::

             | The sensor can be connected to any of the I2C ports.
             | You can connect different I2C devices simultaneously provided that:

                * The I2C devices have different addresses.
                * The I2C devices are recognizeable by the `GoPiGo3`_ platform.

        """
        return DistanceSensor(port, self)

    def init_dht_sensor(self, port = "SERIAL", sensor_type = 0):
        """
        | Initialises a :py:class:`~easygopigo3.DHTSensor` object and then returns it.

        :param str port = "SERIAL": The only available port name is ``"SERIAL"``. The default value is also ``"SERIAL"``, so it can be left alone.
        :returns: An instance of the :py:class:`~easygopigo3.DHTSensor` class and with the port set to ``port``'s value.

        The ``"SERIAL"`` port is mapped to the following :ref:`hardware-ports-section`.

        """
        return DHTSensor(port, self, sensor_type)

    def init_remote(self, port="AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.Remote` object and then returns it.

        :param str port = "AD1": Can be set to either ``"AD1"`` or ``"AD2"``. Set by default to ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.Remote` class and with the port set to ``port``'s value.

        The ``"AD1"`` port is mapped to the following :ref:`hardware-ports-section`.

        """
        return Remote(port,self)

    def init_motion_sensor(self, port="AD1"):
        """
        | Initialises a :py:class:`~easygopigo3.MotionSensor` object and then returns it
        
        :param str port = "AD1": Can be set to either ``"AD1"`` or ``"AD2"``. Set by default to ``"AD1"``.
        :returns: An instance of the :py:class:`~easygopigo3.MotionSensor` class and with the port set to ``port``'s value.

        The ``"AD1"`` port is mapped to the following :ref:`hardware-ports-section`.
        """
                
        return MotionSensor(port,self)
        
# the following functions may be redundant


#############################################################
# SENSORS
#############################################################


class Sensor(object):
    """
    Base class for all sensors. Can only be instantiated through the use of an :py:class:`~easygopigo3.EasyGoPiGo3` object.

    It *should* only be used as a base class for any type of sensor. Since it contains methods for setting / getting the ports or the pinmode,
    it's basically useless unless a derived class comes in and adds functionalities.

    :var str port: There're 4 types of ports - analog, digital, I2C and serial ports. The string identifiers are mapped in the following graphical representation - :ref:`hardware-ports-section`.
    :var str pinmode: Represents the mode of operation of a pin - can be a digital input/output, an analog input/output or even a custom mode which must defined in the `GoPiGo3`_'s firmware.
    :var int pin: Each grove connector has 4 pins: GND, VCC and 2 signal pins that can be user-defined. This variable specifies which pin of these 2 signal pins is used.
    :var int portID: Depending on ``ports``'s value, an ID is given to each port. This variable is not important to us.
    :var str descriptor: Represents the "informal" string representation of an instantiated object of this class.
    :var EasyGoPiGo3 gpg: Object instance of the :py:class:`~easygopigo3.EasyGoPiGo3` class.

    .. note::

        The classes which derive from this class are the following:

             * :py:class:`~easygopigo3.DigitalSensor`
             * :py:class:`~easygopigo3.AnalogSensor`
             * :py:class:`~easygopigo3.LineFollower`
             * :py:class:`~easygopigo3.Servo`
             * :py:class:`~easygopigo3.DistanceSensor`
             * :py:class:`~easygopigo3.DHTSensor`

        And the classes which are found at 2nd level of inheritance from this class are:

            * :py:class:`~easygopigo3.LightSensor`
            * :py:class:`~easygopigo3.SoundSensor`
            * :py:class:`~easygopigo3.LoudnessSensor`
            * :py:class:`~easygopigo3.UltraSonicSensor`
            * :py:class:`~easygopigo3.Buzzer`
            * :py:class:`~easygopigo3.Led`
            * :py:class:`~easygopigo3.ButtonSensor`

    .. warning::

        1. This class should only be used by the developers of the `GoPiGo3`_ platform.
        2. The name of this class isn't representative of the devices we connect to the `GoPiGo3`_ robot - we don't only use this class for sensors, but for any kind of device that we can connect to the `GoPiGo3`_ robot.

    """
    PORTS = {}

    def __init__(self, port, pinmode, gpg):
        """
        Constructor for creating a connection to one of the available grove ports on the `GoPIGo3`_.

        :param str port: Specifies the port with which we want to communicate / interact with. The string literals we can use for identifying a port are found in the following graphical drawing : :ref:`hardware-ports-section`.
        :param str pinmode: The mode of operation of the pin we're selecting.
        :param easygopigo3.EasyGoPiGo3 gpg: An instantiated object of the :py:class:`~easygopigo3.EasyGoPiGo3` class. We need this :py:class:`~easygopigo3.EasyGoPiGo3` class for setting up the `GoPiGo3`_ robot's pins.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following string values:

             * ``"AD1"`` - for digital and analog ``pinmode``'s.
             * ``"AD2"`` - for digital and analog ``pinmode``'s.
             * ``"SERVO1"`` - for ``"OUTPUT"`` ``pinmode``.
             * ``"SERVO2"`` - for ``"OUTPUT"`` ``pinmode``.
             * ``"I2C"`` - the ``pinmode`` is irrelevant here.
             * ``"SERIAL"`` - the ``pinmode`` is irrelevant here.

        These ports' locations can be seen in the following graphical representation - :ref:`hardware-ports-section`.

        The ``pinmode`` parameter can take the following string values:

             * ``"INPUT"`` - for general purpose inputs. The `GoPiGo3`_ has 12-bit ADCs.
             * ``"DIGITAL_INPUT"`` - for digital inputs. The port can detect either **0** or **1**.
             * ``"OUTPUT"`` - for general purpose outputs.
             * ``"DIGITAL_OUTPUT"`` - for digital outputs. The port can only be set to **0** or **1**.
             * ``"US"`` - that's for the :py:class:`~easygopigo3.UltraSonicSensor` which can be bought from our `shop`_. Can only be used with ports ``"AD1"`` and ``"AD2"``.
             * ``"IR"`` - that's for the `infrared receiver`_. Can only be used with ports ``"AD1"`` and ``"AD2"``.

        .. warning::

             At the moment, there's no class for interfacing with the `infrared receiver`_.

        """
        debug("Sensor init")

        if type(gpg) != EasyGoPiGo3:
            raise TypeError("Use an EasyGoPiGo3 object for the gpg parameter.")
        self.gpg = gpg
        debug(pinmode)
        self.set_port(port)
        self.set_pin_mode(pinmode)

        try:
            # I2C sensors don't need a valid gpg
            if pinmode == "INPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_INPUT_ANALOG)
            if pinmode == "DIGITAL_INPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_INPUT_DIGITAL)
            if pinmode == "OUTPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_OUTPUT_PWM)
            if pinmode == "DIGITAL_OUTPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_OUTPUT_DIGITAL)
            if pinmode == "US":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.US)
            if pinmode == "IR":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.IR_DI_REMOTE)
        except:
            pass

    def __str__(self):
        """
        Prints out a short summary of the class-instantiated object's attributes.

        :returns: A string with a short summary of the object's attributes.
        :rtype: str

        The returned string is made of the following components:

             * the :py:attr:`~easygopigo3.Sensor.descriptor`'s description
             * the :py:attr:`~easygopigo3.Sensor.port` name
             * the :py:attr:`~easygopigo3.Sensor.pin` identifier
             * the :py:attr:`~easygopigo3.Sensor.portID` - see :py:meth:`~easygopigo3.Sensor.set_port` method.

        Sample of returned string as shown in a terminal:

        .. code-block:: console

             $ ultrasonic sensor on port AD1
             $ pinmode OUTPUT
             $ portID 3

        """
        return ("{} on port {} \npinmode {}\nportID {}".format(self.descriptor,
                self.get_port(), self.get_pin_mode(), self.portID))

    def set_pin(self, pin):
        """
        Selects one of the 2 available pins of the grove connector.

        :param int pin: **1** for the exterior pin of the grove connector (aka SIG) or anything else for the interior one.

        """
        if self.port == "AD1":
            if pin == 1:
                self.pin = self.gpg.GROVE_1_1
            else:
                self.pin = self.gpg.GROVE_1_2
        elif self.port == "AD2":
            if pin == 1:
                self.pin = self.gpg.GROVE_2_1
            else:
                self.pin = self.gpg.GROVE_2_2
        debug("setting pin to {}".format(self.pin))

    def get_pin(self):
        """
        Tells us which pin of the grove connector is used.

        :returns: For exterior pins (aka SIG) it returns :py:data:`gopigo3.GROVE_2_1` or :py:data:`gopigo3.GROVE_2_2` and for interior pins (aka NC) it returns :py:data:`gopigo3.GROVE_1_2` or :py:data:`gopigo3.GROVE_1_2`.
        :rtype: int

        """
        return self.pin

    def set_port(self, port):
        """
        Sets the port that's going to be used by our new device. Again, we can't communicate with our
        device, because the class doesn't have any methods for interfacing with it, so we need to create
        a derived class that does this.

        :param str port: The port we're connecting the device to. Take a look at the :ref:`hardware-ports-section`' locations.

        Apart from this graphical representation of the ports' locations (:ref:`hardware-ports-section` locations),
        take a look at the list of ports in :py:meth:`~easygopigo3.Sensor.__init__`'s description.

        """
        debug(port)
        self.port = port
        debug(self.port)
        debug("self.gpg is {}".format(self.gpg))

        if port == "AD1":
            self.portID = self.gpg.GROVE_1
        elif port == "AD2":
            self.portID = self.gpg.GROVE_2
        elif port == "SERIAL":
            self.portID = -1
        elif port == "I2C":
            self.portID = -2
        elif port == "SERVO1":
            self.portID = self.gpg.SERVO_1
        elif port == "SERVO2":
            self.portID = self.gpg.SERVO_2
        else:
            self.portID = -5

        debug(self.portID)

    def get_port(self):
        """
        Gets the current port our device is connected to.

        :returns: The current set port.
        :rtype: str

        Apart from this graphical representation of the ports' locations (:ref:`hardware-ports-section` locations),
        take a look at the list of ports in :py:meth:`~easygopigo3.Sensor.__init__`'s description.

        """
        return (self.port)

    def get_port_ID(self):
        """
        Gets the ID of the port we're set to.

        :returns: The ID of the port we're set to.
        :rtype: int

        See more about port IDs in :py:class:`~easygopigo3.Sensor`'s description.

        """
        return (self.portID)

    def set_pin_mode(self, pinmode):
        """
        Sets the pin mode of the port we're set to.

        :param str pinmode: The pin mode of the port.

        See more about pin modes in :py:meth:`~easygopigo3.Sensor.__init__`'s description.

        """
        self.pinmode = pinmode

    def get_pin_mode(self):
        """
        Gets the pin mode of the port we're set to.

        :returns: The pin mode of the port.
        :rtype: str

        See more about pin modes in :py:meth:`~easygopigo3.Sensor.__init__`'s description.

        """
        return (self.pinmode)

    # def is_analog(self):
    #     return (self.pin == ANALOG)

    # def is_digital(self):
    #     return (self.pin == DIGITAL)

    def set_descriptor(self, descriptor):
        """
        Sets the object's description.

        :param str descriptor: The object's description.

        See more about class descriptors in :py:class:`~easygopigo3.Sensor`'s description.

        """
        self.descriptor = descriptor
##########################


class DigitalSensor(Sensor):
    def __init__(self, port, pinmode, gpg):
        debug("DigitalSensor init")
        try:
            Sensor.__init__(self, port, pinmode, gpg)
        except:
            raise

    def read(self):
        '''
        Return values:
        0 or 1 are valid values
        -1 may occur when there's a reading error

        On a reading error, a second attempt will be made before
        returning a -1 value
        '''
        try:
            self.value = self.gpg.get_grove_state(self.get_pin())
        except gopigo3.ValueError as e:
            try:
                self.value = self.gpg.get_grove_state(self.get_pin())
            except Exception as e:
                print(e)
                return -1

        return self.value

    def write(self, power):
        self.value = power
        # not ported to GPG3 yet
        return -1
        return gopigo.digitalWrite(self.get_port_ID(), power)
##########################


class AnalogSensor(Sensor):
    """
    | Class for analog devices with input/output capabilities on the `GoPiGo3`_ robot.
    | This class is derived from :py:class:`~easygopigo3.Sensor` class, so this means this class inherits all attributes and methods.

    | For creating an :py:class:`~easygopigo3.AnalogSensor` object an :py:class:`~easygopigo3.EasyGoPiGo3` object is needed like in the following example.

    .. code-block:: python

         # initialize an EasyGoPiGo3 object first
         gpg3_obj = EasyGoPiGo3()

         # let's have an analog input sensor on "AD1" port
         port = "AD1"
         pinmode = "INPUT"

         # instantiate an AnalogSensor object
         # pay attention that we need the gpg3_obj
         analogsensor_obj = AnalogSensor(port, pinmode, gpg3_obj)

         # for example
         # read the sensor's value as we have an analog sensor connected to "AD1" port
         analogsensor_obj.read()

    .. warning::

        The name of this class isn't representative of the type of devices we connect to the `GoPiGo3`_ robot.
        With this class, both analog sensors and actuators (output devices such as LEDs which may require controlled output voltages) can be connected.

    """
    def __init__(self, port, pinmode, gpg):
        """
        Binds an analog device to the specified ``port`` with the appropriate ``pinmode`` mode.

        :param str port: The port to which the sensor/actuator is connected.
        :param str pinmode: The pin mode of the device that's connected to the `GoPiGo3`_.
        :param easygopigo3.EasyGoPiGo3 gpg: Required object for instantiating an :py:class:`~easygopigo3.AnalogSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The available ``port``'s for use are the following:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        .. important::

            Since the grove connector allows 2 signals to pass through 2 pins (not concurently), we can select which pin to go with by using the :py:meth:`~easygopigo3.Sensor.set_pin` method.
            By default, we're using pin **1**, which corresponds to the exterior pin of the grove connector (aka SIG) and the wire is yellow.

        """
        debug("AnalogSensor init")

        self.value = 0
        self.freq = 24000
        self._max_value = 4096
        try:
            Sensor.__init__(self, port, pinmode, gpg)
        except:
            raise

        # select the outwards pin of the grove connector
        self.set_pin(1)

        # this delay is at least needed by the Light sensor
        time.sleep(0.01)

    def read(self):
        """
        Reads analog value of the sensor that's connected to our `GoPiGo3`_ robot.

        :returns: 12-bit number representing the voltage we get from the sensor. Range goes from 0V-5V.
        :rtype: int
        :raises gopigo3.ValueError: If an invalid value was read.
        :raises Exception: If any other errors happens.

        """
        try:
            self.value = self.gpg.get_grove_analog(self.get_pin())
        except gopigo3.ValueError as e:
            try:
                self.value = self.gpg.get_grove_analog(self.get_pin())
            except Exception as e:
                print("Value Error: {}".format(e))
                return 0
        return self.value

    def percent_read(self):
        """
        Reads analog value of the sensor that's connected to our `GoPiGo3`_ robot as a percentage.

        :returns: Percentage mapped to 0V-5V range.
        :rtype: int

        """
        reading_percent = round(self.read() * 100 // self._max_value)
        
        # Some sensors - like the loudness_sensor - 
        # can actually return higher than 100% so let's clip it
        # and keep classrooms within an acceptable noise level
        if reading_percent > 100:
            reading_percent = 100
        return reading_percent

    def write(self, power):
        """
        | Generates a PWM signal on the selected port.
        | Good for simulating an DAC convertor - for instance an LED is a good candidate.

        :param int power: Number from **0** to **100** that represents the duty cycle as a percentage of the frequency's period.

        .. tip::

             If the ``power`` parameter is out of the given range, the most close and valid value will be selected.


        """
        self.value = power
        return_value = self.gpg.set_grove_pwm_duty(self.get_pin(),
                                                       power)
        return return_value

    def write_freq(self, freq):
        """
        | Sets the frequency of the PWM signal.
        | The frequency range goes from 3Hz up to 48000Hz.
        | Default value is set to 24000Hz (24kHz).

        :param int freq: Frequency of the PWM signal.

        .. seealso::

            Read more about this in :py:meth:`gopigo3.GoPiGo3.set_grove_pwm_frequency`'s description.

        """
        self.freq = freq
        # debug("write_freq: {}".format(self.freq))
        return_value = self.gpg.set_grove_pwm_frequency(
                self.get_port_ID(),
                self.freq)
        debug ("Analog Write on {} at {}".format(self.get_port_ID(),
                                                     self.freq))
        return return_value
##########################


class LightSensor(AnalogSensor):
    """
    | Class for the `Grove Light Sensor`_.

    | This class derives from :py:class:`~easygopigo3.AnalogSensor` class, so all of its attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.LightSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_light_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a LightSensor object through the gpg3_obj object
         light_sensor = gpg3_obj.init_light_sensor()

         # do the usual stuff, like read the data of the sensor
         value = light_sensor.read()
         value_percentage = light_sensor.percent_read()

         # take a look at AnalogSensor class for more methods and attributes

    | Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the Light Sensor connected to
         port = "AD2"

         light_sensor = gpg3_obj.init_light_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.LightSensor` object for the `Grove Light Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Light Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.LightSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("LightSensor init")
        self.set_descriptor("Light sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg)
        except:
            raise
        self.set_pin(1)
##########################


class SoundSensor(AnalogSensor):
    """
    | Class for the `Grove Sound Sensor`_.

    | This class derives from :py:class:`~easygopigo3.AnalogSensor` class, so all of its attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.SoundSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_sound_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a SoundSensor object through the gpg3_obj object
         sound_sensor = gpg3_obj.init_sound_sensor()

         # do the usual stuff, like read the data of the sensor
         value = sound_sensor.read()
         value_percentage = sound_sensor.percent_read()

         # take a look at AnalogSensor class for more methods and attributes

    | Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the sound sensor connected to
         port = "AD1"

         sound_sensor = gpg3_obj.init_sound_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.SoundSensor` object for the `Grove Sound Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Sound Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.SoundSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("Sound Sensor on port " + port)
        self.set_descriptor("Sound sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg)
        except:
            raise
        self.set_pin(1)


##########################

class LoudnessSensor(AnalogSensor):
    """
    | Class for the `Grove Loudness Sensor`_.

    | This class derives from :py:class:`~easygopigo3.Sensor` and :py:class:`~easygopigo3.AnalogSensor` class, so all of their attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.LoudnessSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_loudness_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a LoudnessSensor object through the gpg3_obj object
         loudness_sensor = gpg3_obj.init_loudness_sensor()

         # do the usual stuff, like read the data of the sensor
         value = loudness_sensor.read()
         value_percentage = loudness_sensor.percent_read()

         # take a look at AnalogSensor class and Sensor class for more methods and attributes

    | Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the sound sensor connected to
         port = "AD1"

         loudness_sensor = gpg3_obj.init_loudness_sensor(port)

         # read the sensor the same way as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.

    """
    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.LoudnessSensor` object for the `Grove Loudness Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Loudness Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.LoudnessSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        debug("Loudness Sensor on port " + port)
        self.set_descriptor("Loudness sensor")
        try:
            AnalogSensor.__init__(self, port, "INPUT", gpg)
        except:
            raise
        self.set_pin(1)
        self._max_value = 1024  # based on empirical tests


##########################        


class UltraSonicSensor(AnalogSensor):
    """
    | Class for the `Grove Ultrasonic Sensor`_.

    | This class derives from :py:class:`~easygopigo3.AnalogSensor` class, so all of its attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.UltraSonicSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_ultrasonic_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a UltraSonicSensor object through the gpg3_obj object
         ultrasonic_sensor = gpg3_obj.init_ultrasonic_sensor()

         # do the usual stuff, like read the distance the sensor is measuring
         distance_cm = ultrasonic_sensor.read()
         distance_inches = ultrasonic_sensor.read_inches()

         # take a look at AnalogSensor class for more methods and attributes

    | Or if we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the ultrasonic sensor connected to
         port = "AD1"

         ultrasonic_sensor = gpg3_obj.init_ultrasonic_sensor(port)

         # read the sensor's measured distance as in the previous example

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.UltraSonicSensor` object for the `Grove Ultrasonic Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Ultrasonic Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.UltraSonicSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """

        try:
            debug("Ultrasonic Sensor on port " + port)
            AnalogSensor.__init__(self, port, "US", gpg)
            self.set_descriptor("Ultrasonic sensor")
            self.safe_distance = 500
            self.set_pin(1)
        except:
            raise


    def is_too_close(self):
        """
        Checks whether the `Grove Ultrasonic Sensor`_ measures a distance that's too close to a target than
        what we consider a *safe distance*.

        :returns: Whether the `Grove Ultrasonic Sensor`_ is too close from a target.
        :rtype: boolean
        :raises gopigo3.SensorError: If a sensor is not yet configured when trying to read it.

        A *safe distance* can be set with the :py:meth:`~easygopigo3.UltraSonicSensor.set_safe_distance` method.

        .. note::

            The default *safe distance* is set at 50 cm.


        """
        try:
            val = self.gpg.get_grove_value(self.get_port_ID())
        except gopigo3.SensorError as e:
            print("Invalid Reading")
            print(e)
            return False

        if  val < self.get_safe_distance():
            return True
        return False

    def set_safe_distance(self, dist):
        """
        Sets a *safe distance* for the `Grove Ultrasonic Sensor`_.

        :param int dist: Minimum distance from a target that we can call a *safe distance*.

        To check whether the robot is too close from a target, please check the :py:meth:`~easygopigo3.UltraSonicSensor.is_too_close` method.

        .. note::

            The default *safe distance* is set at 50 cm.


        """
        self.safe_distance = int(dist)

    def get_safe_distance(self):
        """
        Gets what we call the *safe distance* for the `Grove Ultrasonic Sensor`_.

        :returns: The minimum distance from a target that can be considered a *safe distance*.
        :rtype: int

        .. note::

            The default *safe distance* is set at 50 cm.

        """
        return self.safe_distance

    def read_mm(self):
        """
        Measures the distance from a target in millimeters.

        :returns: The distance from a target in millimeters.
        :rtype: int
        :raises gopigo3.ValueError: If trying to read an invalid value.
        :raises Exception: If any other error occurs.

        .. important::

            * This method can read distances between **15-4300** millimeters.
            * This method will read the data for 3 times and it'll discard anything that's smaller than 15 millimeters and bigger than 4300 millimeters.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **5010**.

        """
        return_reading = 0
        readings = []
        skip = 0
        value=0

        while len(readings) < 3 and skip < 5:
            try:
                value = self.gpg.get_grove_value(self.get_port_ID())
                print ("raw {}".format(value))
            except gopigo3.ValueError as e:
                # print("Value Error")
                # print(e)
                value = 5010   # assume open road ahead
                time.sleep(0.05)

            except Exception as e:
                print(e)
                skip += 1
                time.sleep(0.05)
                continue

            if value <= 4300 and value >= 15:
                readings.append(value)
                # debug (readings)
            else:
                skip += 1

        if skip >= 5:
            # if value = 0 it means Ultrasonic Sensor wasn't found
            if value == 0:
                return(0)

            # no special meaning to the number 5010
            return(5010)

        for reading in readings:
            return_reading += reading

        return_reading = int(return_reading / len(readings))

        return (return_reading)

    def read(self):
        """
        Measures the distance from a target in centimeters.

        :returns: The distance from a target in centimeters.
        :rtype: int

        .. important::

            * This method can read distances between **2-430** centimeters.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **501**.

        """
        # returns value in cm
        value = self.read_mm()
        if value >= 15 and value <= 5010:
            return int(round(value / 10.0))
        return value

    def read_inches(self):
        """
        Measures the distance from a target in inches.

        :returns: The distance from a target in inches.
        :rtype: float (one decimal)

        .. important::

            * This method can read distances of up to **169** inches.
            * If data is discarded 5 times (due to a communication error with the sensor), then the method returns **501**.

        """
        value = self.read()   # cm reading
        if value == 501:
            return 501
        return (round(value / 2.54, 1))
##########################


class Buzzer(AnalogSensor):
    """
    | Class for the `Grove Buzzer`_.

    | This class derives from :py:class:`~easygopigo3.AnalogSensor` class, so all of its attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.Buzzer` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_buzzer` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a UltraSonicSensor object through the gpg3_obj object
         buzzer = gpg3_obj.init_buzzer()

         # turn on and off the buzzer
         buzzer.sound_on()
         sleep(1)
         buzzer.sound_off()

         # take a look at AnalogSensor class for more methods and attributes

    | If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the ultrasonic sensor connected to
         port = "AD1"

         buzzer = gpg3_obj.init_buzzer(port)

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    #: | Dictionary of frequencies for each musical note.
    #: | For instance, ``scale["A3"]`` instruction is equal to 220 Hz (that's the A3 musical note's frequency).
    #: | This dictionary is useful when we want to make the buzzer ring at certain frequencies (aka musical notes).
    scale = {"A3": 220,
             "A3#": 233,
             "B3": 247,
             "C4": 261,
             "C4#": 277,
             "D4": 293,
             "D4#": 311,
             "E4": 329,
             "F4": 349,
             "F4#": 370,
             "G4": 392,
             "G4#": 415,
             "A4": 440,
             "A4#": 466,
             "B4": 494,
             "C5": 523,
             "C5#": 554,
             "D5": 587,
             "D5#": 622,
             "E5": 659,
             "F5": 698,
             "F5#": 740,
             "G5": 784,
             "G5#": 831}

    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.Buzzer` object for the `Grove Buzzer`_.

        :param str port = "AD1": Port to which we have the `Grove Buzzer`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.Buzzer` object.
        :var int power = 50: Duty cycle of the signal that's put on the buzzer.
        :var int freq = 329: Frequency of the signal that's put on the buzzer. 329Hz is synonymous to E4 musical note. See :py:attr:`~.easygopigo3.Buzzer.scale` for more musical notes.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """

        try:
            AnalogSensor.__init__(self, port, "OUTPUT", gpg)
            self.set_pin(1)
            self.set_descriptor("Buzzer")
            self.power = 50
            self.freq = 329
            self.sound_off()
        except:
            raise

    def sound(self, freq):
        """
        Sets a musical note for the `Grove Buzzer`_.

        :param int freq: The frequency of the signal that's put on the `Grove Buzzer`_.

        For a list of musical notes, please see :py:attr:`~.easygopigo3.Buzzer.scale`.

        Example on how to play musical notes.

        .. code-block:: python

             # initialize all the required objects and connect the sensor to the GoPiGo3

             musical_notes = buzzer.scale
             notes_i_want_to_play = {"F4#", "F4#", "C5#", "B3", "B3", "B3"}
             wait_time = 1.0

             for note in notes_i_want_to_play:
                buzzer.sound(musical_notes[note])
                sleep(wait_time)

                # enjoy the musical notes

        """
        try:
            freq = int(freq)
        except:
            freq = 0

        # limit duty cycles (aka power) values to either 0 or 50
        if freq <= 0:
            power = 0
            freq = 0
        else:
            power = 50

        # if buzzer has to emit a sound then set frequency
        if power == 50:
            # translation_factor = ((40000 - 20) / 100)
            # freq = (freq * translation_factor) + 20
            self.write_freq(freq)

        # debug(freq, power)
        # set duty cycle, either 0 or 50
        self.write(power)

    def sound_off(self):
        """
        Turns off the `Grove Buzzer`_.

        """
        self.sound(0)

    def sound_on(self):
        """
        Turns on the `Grove Buzzer`_ at the set frequency.

        For changing the frequency, please check the :py:meth:`~easygopigo3.Buzzer.sound` method.

        """
        self.sound(self.freq)
##########################


class Led(AnalogSensor):
    """
    | Class for the `Grove LED`_.
    | With this class the following things can be done:

         * Turn *ON*/*OFF* an LED.
         * Set a level of brightness for the LED.
         * Check if an LED is turned *ON* or *OFF*.

    | This class derives from :py:class:`~easygopigo3.AnalogSensor` class, so all of its attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.Led` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_led` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Led object through the gpg3_obj object
         led = gpg3_obj.init_led()

         # turn on and off the buzzer
         led.light_max()
         sleep(1)
         led.light_off()

         # take a look at AnalogSensor class for more methods and attributes

    | If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the led connected to
         port = "AD1"

         led = gpg3_obj.init_led(port)

         # call some Led-specific methods

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """
    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.Led` object for the `Grove LED`_.

        :param str port = "AD1": Port to which we have the `Grove LED`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.Led` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("LED")
            AnalogSensor.__init__(self, port, "OUTPUT", gpg)
            self.set_pin(1)
        except:
            raise

    def light_on(self, power):
        """
        Sets the duty cycle for the `Grove LED`_.

        :param int power: Number between **0** and **100** that represents the duty cycle of PWM signal.

        """
        self.write(power)

    def light_max(self):
        """
        Turns on the `Grove LED`_ at full power.

        """
        max_power = 100
        self.light_on(max_power)

    def light_off(self):
        """
        Turns off the `Grove LED`_.

        """
        self.write(0)

    def is_on(self):
        """
        Checks if the `Grove LED`_ is turned on.

        :returns: If the `Grove LED`_ is on.
        :rtype: boolean

        """
        return (self.value > 0)

    def is_off(self):
        """
        Checks if the `Grove LED`_ is turned off.

        :returns: If the `Grove LED`_ is off.
        :rtype: boolean

        """
        return (self.value == 0)
##########################


class MotionSensor(DigitalSensor):
    """
    | Class for the `Grove Motion Sensor`_.

    | This class derives from :py:class:`~easygopigo3.Sensor` (check for throwable exceptions) and :py:class:`~easygopigo3.DigitalSensor` classes, so all attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.MotionSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_motion_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Motion Sensor object through the gpg3_obj object on default port AD1
         motion_sensor = gpg3_obj.init_motion_sensor()

         while True:
             if motion_sensor.motion_detected():
                 print("motion detected")
             else:
                 print("no motion")

         # take a look at DigitalSensor & Sensor class for more methods and attributes

    | If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the motion sensor connected to
         port = "AD2"

         motion_sensor = gpg3_obj.init_motion_sensor(port)

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """
   
    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.MotionSensor` object for the `Grove Motion Sensor`_.

        :param str port = "AD1": Port to which we have the `Grove Motion Sensor`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.MotionSensor` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Motion Sensor")
            DigitalSensor.__init__(self, port, "DIGITAL_INPUT", gpg)
            self.set_pin(1)
        except:
            raise

    def motion_detected(self,port="AD1"):
        """
        Checks if the `Grove Motion Sensor`_ detects a motion.

        :returns: ``True`` or ``False``, if the `Grove Motion Sensor`_ detects a motion or not.
        :rtype: boolean

        """
        return self.read() == 1
##########################


class ButtonSensor(DigitalSensor):
    """
    | Class for the `Grove Button`_.

    | This class derives from :py:class:`~easygopigo3.Sensor` (check for throwable exceptions) and :py:class:`~easygopigo3.DigitalSensor` classes, so all attributes and methods are inherited.
    | For creating a :py:class:`~easygopigo3.ButtonSensor` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_button_sensor` method like in the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now instantiate a Button object through the gpg3_obj object
         button = gpg3_obj.init_button_sensor()

         while True:
             if button.is_button_pressed():
                 print("button pressed")
             else:
                 print("button released")

         # take a look at DigitalSensor & Sensor class for more methods and attributes

    | If we need to specify the port we want to use, we might do it like in the following example.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # variable for holding the port to which we have the button connected to
         port = "AD1"

         button = gpg3_obj.init_button_sensor(port)

         # call some button-specific methods

    .. seealso::

         For more sensors, please see our Dexter Industries `shop`_.


    """

    def __init__(self, port="AD1", gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.ButtonSensor` object for the `Grove Button`_.

        :param str port = "AD1": Port to which we have the `Grove Button`_ connected to.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object used for instantiating a :py:class:`~easygopigo3.Button` object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``port`` parameter can take the following values:

             * ``"AD1"`` - general purpose input/output port.
             * ``"AD2"`` - general purpose input/output port.

        The ports' locations can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Button sensor")
            DigitalSensor.__init__(self, port, "DIGITAL_INPUT", gpg)
            self.set_pin(1)
        except:
            raise

    def is_button_pressed(self):
        """
        Checks if the `Grove Button`_ is pressed.

        :returns: ``True`` or ``False``, if the `Grove Button`_ is pressed.
        :rtype: boolean

        """
        return self.read() == 1
##########################


class Remote(Sensor):
    """
    Class for interfacing with the `Infrared Receiver`_.

    With this sensor, you can command your `GoPiGo3`_ with an `Infrared Remote`_.

    In order to create an object of this class, we would do it like in the following example.

    .. code-block:: python

        # initialize an EasyGoPiGo3 object
        gpg3_obj = EasyGoPiGo3()

        # now initialize a Remote object
        remote_control = gpg3_obj.init_remote()

        # read whatever command you want from the remote by using
        # the [remote_control] object

    """

    #: List for mapping the codes we get with the :py:meth:`~easygopigo3.Remote.read` method to
    #: the actual symbols we see on the `Infrared Remote`_.
    keycodes = ["up", "left", "ok", "right","down","1","2","3","4","5","6","7", "8","9","*","0","#"]

    def __init__(self, port="AD1",gpg=None):
        """
        Constructor for initializing a :py:class:`~easygopigo3.Remote` object.

        :param str port = "AD1": The port to which we connect the `Infrared Receiver`_.
        :param easygopigo3.EasyGoPiGo3 gpg = None: The :py:class:`~easygopigo3.EasyGoPiGo3` object that we need for instantiating this object.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The ``"AD1"`` and ``"AD2"`` ports' location on the `GoPiGo3`_ robot can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("Remote Control")
            Sensor.__init__(self, port, "IR", gpg)
        except:
            raise

    def read(self):
        """
        Reads the numeric code received by the `Infrared Receiver`_.

        :return: The numeric code of the symbol that was pressed on the `Infrared Remote`_.
        :rtype: int

        The numeric code represents the index of the :py:attr:`~easygopigo3.Remote.keycodes` list.
        By accessing the :py:attr:`~easygopigo3.Remote.keycodes` elements with the numeric code, you
        get the symbol that was pressed on the `Infrared Remote`_.

        For only getting the symbol that was pressed on the `Infrared Remote`_, please check the :py:meth:`~easygopigo3.Remote.get_remote_code` method.

        .. warning::

           On :py:class:`~gopigo3.SensorError` exception:

            * ``"Invalid Reading"`` string is printed in the console.
            * The value of **-1** is returned.

        """
        try:
            val = self.gpg.get_grove_value(self.get_port_ID())
            return val
        except gopigo3.SensorError as e:
            print("Invalid Reading")
            return -1


    def get_remote_code(self):
        """
        Returns the symbol of the pressed key in a string format.

        :return: The symbol that was pressed on the `Infrared Remote`_.
        :rtype: str

        Check the :py:attr:`~easygopigo3.Remote.keycodes` list for seeing what strings this method can return.
        On error or when nothing is read, an empty string is returned.

        """
        string = ""
        key = self.read()

        if key > 0 and key < len(self.keycodes)+1:
            string = self.keycodes[self.read()-1]

        return string
##########################


class LineFollower(Sensor):
    """
    Class for interacting with the `Line Follower`_ sensor.
    With this sensor, you can make your robot follow a black line on a white background.

    The `Line Follower`_ sensor has 5 IR sensors.
    Each IR sensor is capable of diferentiating a black surface from a white one.

    In order to create an object of this class, we would do it like in the following example.

    .. code-block:: python

         # initialize an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and then initialize the LineFollower object
         line_follower = gpg3_obj.init_line_follower()

         # use it however you want it
         line_follower.read_raw_sensors()

    .. warning::

         This class requires the :py:mod:`line_sensor` library.

    """

    def __init__(self, port="I2C", gpg=None):
        """
        Constructor for initalizing a :py:class:`~easygopigo3.LineFollower` object.

        :param str port = "I2C": The port to which we have connected the `Line Follower`_ sensor.
        :param easygopigo3.EasyGoPiGo3 gpg = None: The :py:class:`~easygopigo3.EasyGoPiGo3` object that we need for instantiating this object.
        :raises ImportError: If the :py:mod:`line_follower` module couldn't be found.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.


        The only value the ``port`` parameter can take is ``"I2C"``.

        The I2C ports' location on the `GoPiGo3`_ robot can be seen in the following graphical representation: :ref:`hardware-ports-section`.

        """
        if is_line_follower_accessible is False:
            raise ImportError("Line Follower library not found")

        try:
            self.set_descriptor("Line Follower")
            Sensor.__init__(self, port, "INPUT", gpg)
        except:
            raise

    def read_raw_sensors(self):
        """
        Read the 5 IR sensors of the `Line Follower`_ sensor.

        :returns: A list with 5 10-bit numbers that represent the readings from the line follower device.
        :rtype: list[int]

        """
        five_vals = line_sensor.read_sensor()

        if five_vals != -1:
            return five_vals
        else:
            return [-1, -1, -1, -1, -1]

    def get_white_calibration(self):
        """
        Place the `GoPiGo3`_ robot on top of a white-colored surface.
        After that, call this method for calibrating the robot on a white surface.

        :returns: A list with 5 10-bit numbers that represent the readings of line follower sensor.
        :rtype: int

        Also, for fully calibrating the sensor, the :py:class:`~easygopigo3.LineFollower.get_black_calibration` method also needs to be called.

        """
        return line_sensor.get_white_line()

    def get_black_calibration(self):
        """
        Place the `GoPiGo3`_ robot on top of a black-colored surface.
        After that, call this method for calibrating the robot on a black surface.

        :returns: A list with 5 10-bit numbers that represent the readings of line follower sensor.
        :rtype: int

        Also, for fully calibrating the sensor, the :py:class:`~easygopigo3.LineFollower.get_white_calibration` method also needs to be called.

        """
        return line_sensor.get_black_line()

    def read(self):
        """
        Reads the 5 IR sensors of the `Line Follower`_ sensor.

        :returns: A list with 5 numbers that represent the readings of the line follower device. The values are either **0** (for black) or **1** (for white).
        :rtype: list[int]

        .. warning::

             If an error occurs, a list of **5 numbers** with values set to **-1** will be returned.
             This may be caused by bad calibration values.

             Please use :py:meth:`~easygopigo3.LineFollower.get_black_calibration` or :py:meth:`~easygopigo3.LineFollower.get_white_calibration` methods before calling this method.

        """
        five_vals = scratch_line.absolute_line_pos()

        return five_vals

    def read_position(self):
        """
        Returns a string telling to which side the black line that we're following is located.

        :returns: String that's indicating the location of the black line.
        :rtype: str

        The strings this method can return are the following:

            * ``"center"`` - when the line is found in the middle.
            * ``"black"`` - when the line follower sensor only detects black surfaces.
            * ``"white"`` - when the line follower sensor only detects white surfaces.
            * ``"left"`` - when the black line is located on the left of the sensor.
            * ``"right"`` - when the black line is located on the right of the sensor.

        .. note::

            This isn't the most "intelligent" algorithm for following a black line, but it proves the point and it works.

        """
        five_vals = [-1, -1, -1, -1, -1]


        five_vals = self.read()

        if five_vals == [0, 0, 1, 0, 0] or five_vals == [0, 1, 1, 1, 0]:
            return "center"
        if five_vals == [1, 1, 1, 1, 1]:
            return "black"
        if five_vals == [0, 0, 0, 0, 0]:
            return "white"
        if five_vals == [0, 1, 1, 0, 0] or \
           five_vals == [0, 1, 0, 0, 0] or \
           five_vals == [1, 0, 0, 0, 0] or \
           five_vals == [1, 1, 0, 0, 0] or \
           five_vals == [1, 1, 1, 0, 0] or \
           five_vals == [1, 1, 1, 1, 0]:
            return "left"
        if five_vals == [0, 0, 0, 1, 0] or \
           five_vals == [0, 0, 1, 1, 0] or \
           five_vals == [0, 0, 0, 0, 1] or \
           five_vals == [0, 0, 0, 1, 1] or \
           five_vals == [0, 0, 1, 1, 1] or \
           five_vals == [0, 1, 1, 1, 1]:
            return "right"
        return "unknown"
##########################


class Servo(Sensor):
    """
    Class for controlling `servo`_ motors with the `GoPiGo3`_ robot.
    Allows you to rotate the servo by serving the angle of rotation.

    This class is derived from :py:class:`~easygopigo3.Sensor` class and because of this, it inherits all the attributes and methods.

    For creating a :py:class:`~easygopigo3.Servo` object we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_servo` method like in
    the following examples.

    .. code-block:: python

         # create an EasyGoPiGo3 object
         gpg3_obj = EasyGoPiGo3()

         # and now let's instantiate a Servo object through the gpg3_obj object
         # this will bind a servo to port "SERVO1"
         servo = gpg3_obj.init_servo()

         # rotate the servo at 160 degrees
         servo.rotate_servo(160)

    Or if we want to specify the port to which we connect the servo, we need to call :py:meth:`~easygopigo3.EasyGoPiGo3.init_servo` the following way.

    .. code-block:: python

         servo = gpg3_obj.init_servo("SERVO2")

    .. seealso::

        For more sensors, please see our Dexter Industries `shop`_.

    """

    def __init__(self, port="SERVO1", gpg=None):
        """
        Constructor for instantiating a :py:class:`~easygopigo3.Servo` object for a (or multiple) `servo`_ (servos).

        :param str port = "SERVO1": The port to which we have connected the `servo`_.
        :param easygopigo3.EasyGoPiGo3 gpg = None: :py:class:`~easygopigo3.EasyGoPiGo3` object that we need for instantiation.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        The available ports that can be used for a `servo`_ are:

             * ``"SERVO1"`` - servo controller port.
             * ``"SERVO2"`` - servo controller port.

        To see where these 2 ports are located, please take a look at the following graphical representation: :ref:`hardware-ports-section`.

        """
        try:
            self.set_descriptor("GoPiGo3 Servo")
            Sensor.__init__(self, port, "OUTPUT", gpg)
        except:
            raise

    def rotate_servo(self, servo_position):
        """
        Rotates the `servo`_ at a specific angle.

        :param int servo_position: Angle at which the servo has to rotate. The values can be anywhere from **0** to **180** degrees.

        The pulse width varies the following way:

             * **575 uS** for **0 degrees** - the servo's default position.
             * **24250 uS** for **180 degrees** - where the servo is rotated at its maximum position.

        Each rotation of **1 degree** requires an increase of the pulse width by **10.27 uS**.

        .. warning::

             | We use PWM signals (Pulse Width Modulation), so the angle at which a `servo`_ will rotate will be case-dependent.
             | This means a servo's 180 degrees position won't be the same as with another servo.

        """

        #Pulse width range in us corresponding to 0 to 180 degrees
        PULSE_WIDTH_RANGE=1850

        # Servo Position in degrees
        if servo_position > 180:
            servo_position = 180
        elif servo_position < 0:
            servo_position = 0

        pulsewidth = round( (1500-(PULSE_WIDTH_RANGE/2)) +
                            ((PULSE_WIDTH_RANGE /180) * servo_position))

        # Set position for the servo
        self.gpg.set_servo( self.portID, int(pulsewidth))

    def reset_servo(self):
        """
        Resets the `servo`_ straight ahead, in the middle position.

        .. tip::

           | Same as calling ``rotate_servo(90)``.
           | Read more about :py:meth:`~easygopigo3.Servo.rotate_servo` method.

        """
        self.gpg.set_servo(self.portID, 90)

#######################################################################
#
# DistanceSensor
#
# under try/except in case the Distance Sensor is not installed
#######################################################################
try:
    from di_sensors import distance_sensor

except:
    try:
        from mock_package import distance_sensor
        print ("Loading library without distance sensor")
    except:
        pass


class DistanceSensor(Sensor, distance_sensor.DistanceSensor):
    """
    Class for the `Distance Sensor`_ device.

    We can create this :py:class:`~easygopigo3.DistanceSensor` object similar to how we create it in the following template.

    .. code-block:: python

        # create an EasyGoPiGo3 object
        gpg3_obj = EasyGoPiGo3()

        # and now let's instantiate a DistanceSensor object through the gpg3_obj object
        distance_sensor = gpg3_obj.init_distance_sensor()

        # read values continuously and print them in the terminal
        while True:
            distance = distance_sensor.read()

            print(distance)

    """
    def __init__(self, port="I2C",gpg=None):
        """
        Creates a :py:class:`~easygopigo3.DistanceSensor` object which can be used for interfacing with a `distance sensor`_.

        :param str port = "I2C": Port to which the distance sensor is connected.
        :param easygopigo3.EasyGoPiGo3 gpg = None: Object that's required for instantianting a :py:class:`~easygopigo3.DistanceSensor` object.
        :raises IOError: If :py:class:`di_sensors.distance_sensor.DistanceSensor` can't be found. Probably the :py:mod:`di_sensors` module isn't installed.
        :raises TypeError: If the ``gpg`` parameter is not a :py:class:`~easygopigo3.EasyGoPiGo3` object.

        To see where the ports are located on the `GoPiGo3`_ robot, please take a look at the following diagram: :ref:`hardware-ports-section`.

        """
        self.set_descriptor("Distance Sensor")
        try:
            Sensor.__init__(self, port, "OUTPUT", gpg)
        except:
            raise

        try:
            _grab_read()
            distance_sensor.DistanceSensor.__init__(self)
        except Exception as e:
            print("Distance Sensor init: {}".format(e))
            raise
        finally:
            _release_read()

    # Returns the values in cms
    def read_mm(self):
        """
        Reads the distance in millimeters.

        :returns: Distance from target in millimeters.
        :rtype: int

        .. note::

             1. Sensor's range is **5-8,000** millimeters.
             2. When the values are out of the range, it returns **8190**.

        """

        # 8190 is what the sensor sends when it's out of range
        # we're just setting a default value
        mm = 8190
        readings = []
        attempt = 0

        # try 3 times to have a reading that is
        # smaller than 8m or bigger than 5 mm.
        # if sensor insists on that value, then pass it on
        while (mm > 8000 or mm < 5) and attempt < 3:
            try:
                _grab_read()
                mm = self.read_range_single()
            except:
                mm = 0
            finally:
                _release_read()
                
            attempt = attempt + 1
            time.sleep(0.001)

        # add the reading to our last 3 readings
        # a 0 value is possible when sensor is not found
        if (mm < 8000 and mm > 5) or mm == 0:
            readings.append(mm)
        if len(readings) > 3:
            readings.pop(0)

        # calculate an average and limit it to 5 > X > 3000
        if len(readings) > 1: # avoid division by 0
            mm = round(sum(readings) / float(len(readings)))
        if mm > 3000:
            mm = 3000

        return mm

    def read(self):
        """
        Reads the distance in centimeters.

        :returns: Distance from target in centimeters.
        :rtype: int

        .. note::

             1. Sensor's range is **0-800** centimeters.
             2. When the values are out of the range, it returns **819**.

        """

        cm = self.read_mm()//10
        return (cm)

    def read_inches(self):
        """
        Reads the distance in inches.

        :returns: Distance from target in inches.
        :rtype: float with one decimal

        .. note::

             1. Sensor's range is **0-314** inches.
             2. Anything that's bigger than **314** inches is returned when the sensor can't detect any target/surface.

        """
        cm = self.read()
        return round(cm / 2.54, 1)


class DHTSensor(Sensor):
    '''
    Support for the Adafruit DHT sensor, blue or white
    All imports are done internally so it's done on a as needed basis only
        as in many cases the DHT sensor is not connected.
    '''
    def __init__(self, port="SERIAL",gpg=None, sensor_type=0):

        self.sensor_type = sensor_type

        if self.sensor_type == 0:
            self.set_descriptor("Blue DHT Sensor")
        else:
            self.set_descriptor("White DHT Sensor")

        try:
            Sensor.__init__(self,port,"INPUT",gpg)
        except:
            raise

    def read_temperature(self):
        '''
        Return values may be a float, or error strings
        TBD: raise errors instead of returning strings
        import done internally so it's done on a as needed basis only
        '''

        from di_sensors import DHT

        try:
            _grab_read()
            temp = DHT.dht(self.sensor_type)[0]
        except Exception as e:
            raise
        finally:
            _release_read()

        if temp == -2:
            return "Bad reading, trying again"
        elif temp == -3:
            return "Run the program as sudo"
        else:
            # print("Temperature = %.02fC"%temp)
            return temp

    def read_humidity(self):
        '''
        Return values may be a float, or error strings
        TBD: raise errors instead of returning strins
        '''
        from di_sensors import DHT

        try:
            _grab_read()
            humidity = DHT.dht(self.sensor_type)[1]
        except Exception as e:
            raise
        finally:
            _release_read()

        if humidity == -2:
            return "Bad reading, trying again"
        elif humidity == -3:
            return "Run the program as sudo"
        else:
            # print("Humidity = %.02f%%"%humidity)
            return humidity

    def read(self):
        from di_sensors import DHT

        try:
            _grab_read()
            [temp , humidity]=DHT.dht(self.sensor_type)
        except Exception as e:
            raise
        finally:
            _release_read()

        if temp ==-2.0 or humidity == -2.0:
            return "Bad reading, trying again"
        elif temp ==-3.0 or humidity == -3.0:
            return "Run the program as sudo"
        else:
            print("Temperature = %.02fC Humidity = %.02f%%"%(temp, humidity))
            return [temp, humidity]



# class RgbLcd(Sensor):
#     '''
#     Wrapper to display Text, change background color on RGB LCD.
#     Connect the sensor to the I2C Port.
#     '''

#     def __init__(self, port="I2C",gpg=None):
#         try:
#             Sensor.__init__(self, port, "OUTPUT",gpg)
#             self.set_descriptor("Grove RGB Lcd")
#         except:
#             raise ValueError("Grove RGB Lcd not found")

#     def display_text(self,text):
#         '''
#         To display a text. It moves to the next line when it encounters "\n" in the text or if there are more than 16 characters.
#         Input the text as a string.
#         '''

#         grove_rgb_lcd.setText(text)

#     # Displays Text over the previous screen without clearing the screen
#     def display_text_over(self,text):
#         grove_rgb_lcd.setText_norefresh(text)

#     def set_BgColor(self,red,green,blue):
#         '''
#         To set the background color of the LCD
#         Red, Green and Blue variables range between (0-255) which indicate the intensity of the color
#         '''
#         grove_rgb_lcd.setRGB(red,green,blue)


if __name__ == '__main__':
   e=EasyGoPiGo3()
   # b = Buzzer()
   # print (b)
   # print ("Sounding buzzer")
   # b.sound_on()
   # time.sleep(1)
   # print ("buzzer off")
   # b.sound_off()

   #  c = RgbLcd("I2C",e)
   #  c.display_text("Hello World")
   #  c.display_text_over("\nK")
   #  c.set_BgColor(0,128,64)
   #  time.sleep(2)


   #  d=Distance("I2C",e)
   #  h=d.read_distance()
   #  print(h)

   #  f=Servo("SERVO",e)
   #  f.rotate_servo("both",0)
   #  time.sleep(1)
   #  f.rotate_servo(1,180)
   #  time.sleep(1)
   #  f.rotate_servo("two",180)

   #  g=DHTSensor("SERIAL",e)
   #  g.read_humidity()
   #  g.read_temperature()
   #  g.read_dht()
   #  g.continuous_read_dht()
