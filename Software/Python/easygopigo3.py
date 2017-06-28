#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
# from builtins import input

import sys
# import tty
# import select
import time
import gopigo3

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
    sys.path.insert(0, '/home/pi/Dexter/GoPiGo/Software/Python/line_follower')
    import line_sensor
    import scratch_line
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
    def __init__(self):
        super(self.__class__, self).__init__()
        self.sensor_1 = None
        self.sensor_2 = None
        self.set_speed(300)
        self.left_eye_color = (0, 255, 255)
        self.right_eye_color = (0, 255, 255)

    def volt(self):
        voltage = self.get_voltage_battery()
        return voltage

    def set_speed(self, in_speed):
        try:
            self.speed = int(in_speed)
        except:
            self.speed = 300
        self.set_motor_limits(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                              dps=self.speed)

    def get_speed(self):
        return int(self.speed)

    def stop(self):
        # only one is needed, we're going overkill
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)
        self.set_motor_power(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)

    def backward(self):
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed() * -1)

    def right(self):
        self.set_motor_dps(self.MOTOR_LEFT, self.get_speed())
        self.set_motor_dps(self.MOTOR_RIGHT, 0)

    def left(self):
        self.set_motor_dps(self.MOTOR_LEFT, 0)
        self.set_motor_dps(self.MOTOR_RIGHT, self.get_speed())

    def forward(self):
        self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed())

    def drive_cm(self, dist, blocking=False):
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

    def drive_inches(self, dist, blocking=False):
        self.drive_cm(dist * 2.54, blocking)

    def drive_degrees(self, degrees, blocking=False):
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
        '''
        check if both wheels have reached their target
        '''
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
        self.set_motor_power(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)
        self.offset_motor_encoder(self.MOTOR_LEFT,self.get_motor_encoder(self.MOTOR_LEFT))
        self.offset_motor_encoder(self.MOTOR_RIGHT,self.get_motor_encoder(self.MOTOR_RIGHT))

    def blinker_on(self, id):
        if id == 1 or id == "left":
            self.set_led(self.LED_LEFT_BLINKER, 255)
        if id == 0 or id == "right":
            self.set_led(self.LED_RIGHT_BLINKER, 255)

    def blinker_off(self, id):
        if id == 1 or id == "left":
            self.set_led(self.LED_LEFT_BLINKER, 0)
        if id == 0 or id == "right":
            self.set_led(self.LED_RIGHT_BLINKER, 0)


    def led_on(self, id):
        self.blinker_on(id)

    def led_off(self, id):
        self.blinker_off(id)


    def set_left_eye_color(self, color):
        if isinstance(color, tuple) and len(color) == 3:
            self.left_eye_color = color
        else:
            raise TypeError("Eye color  not valid")

    def set_right_eye_color(self, color):
        if isinstance(color, tuple) and len(color) == 3:
            self.right_eye_color = color
        else:
            raise TypeError("Eye color  not valid")

    def set_eye_color(self, color):
        self.set_left_eye_color(color)
        self.set_right_eye_color(color)

    def open_left_eye(self):
        self.set_led(self.LED_LEFT_EYE,
                     self.left_eye_color[0],
                     self.left_eye_color[1],
                     self.left_eye_color[2],
                     )

    def open_right_eye(self):
        self.set_led(self.LED_RIGHT_EYE,
                     self.right_eye_color[0],
                     self.right_eye_color[1],
                     self.right_eye_color[2],
                     )

    def open_eyes(self):
        self.open_left_eye()
        self.open_right_eye()

    def close_left_eye(self):
        self.set_led(self.LED_LEFT_EYE, 0, 0, 0)

    def close_right_eye(self):
        self.set_led(self.LED_RIGHT_EYE, 0, 0, 0)

    def close_eyes(self):
        self.close_left_eye()
        self.close_right_eye()

    def turn_degrees(self, degrees, blocking=False):
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

    def create_sensor(self, port, pinmode):
        return Sensor(port, pinmode, self)

    def create_digital_sensor(self, port, pinmode):
        return DigitalSensor(port, pinmode, self)

    def create_analog_sensor(self, port, pinmode):
        return AnalogSensor(port, pinmode, self)

    def create_light_sensor(self, port):
        return LightSensor(port, self)

    def create_sound_sensor(self, port):
        return SoundSensor(port, self)

    def create_ultrasonic_sensor(self, port):
        return UltraSonicSensor(port, self)

    def create_buzzer(self, port):
        return Buzzer(port, self)

    def create_led(self, port):
        return Led(port, self)

    def create_button_sensor(self, port):
        return ButtonSensor(port, self)

    def create_linefollower(self, port):
        return LineFollower(port, self)

    def create_servo(self, port):
        return Servo(port, self)

    def create_dht_sensor(self, port = "SERIAL", sensor_type = 0):
        return DHTSensor(port, port, self, sensor_type)

# the following functions may be redundant
my_gpg = EasyGoPiGo3()


# these functions are here because we need direct access to these
# for the Drive functionality in Sam
# they do not need locking as the fct they call handles that.
def volt():
    return_value = my_gpg.volt()
    return return_value


def stop():
    my_gpg.stop()


def forward():
    my_gpg.forward()


def backward():
    my_gpg.backward()


def left():
    my_gpg.left()


def right():
    my_gpg.right()


#############################################################
#
#############################################################


class Sensor(object):
    '''
    Base class for all sensors
    Class Attributes:
        port : string - user-readable port identification
        portID : integer - actual port id
        pinmode : "INPUT" or "OUTPUT"
        pin : GROVE_1_1, GROVE_1_2, GROVE_2_1, GROVE_2_2
        descriptor = string to describe the sensor for printing purposes
    Class methods:
        set_port / get_port
        set_pin_mode / get_pin_mode
    '''
    PORTS = {}

    def __init__(self, port, pinmode, gpg):
        '''
        port = one of PORTS keys
        pinmode = "INPUT", "OUTPUT", "SERIAL" (which gets ignored)
        '''
        debug("Sensor init")
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
                                        self.gpg.GROVE_TYPE.IR_GO_BOX)
        except:
            pass

    def __str__(self):
        return ("{} on port {} \npinmode {}\nportID {}".format(self.descriptor,
                self.get_port(), self.get_pin_mode(), self.portID))

    def set_pin(self, pin):
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
        return self.pin

    def set_port(self, port):
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
        return (self.port)

    def get_port_ID(self):
        return (self.portID)

    def set_pin_mode(self, pinmode):
        self.pinmode = pinmode

    def get_pin_mode(self):
        return (self.pinmode)

    # def is_analog(self):
    #     return (self.pin == ANALOG)

    # def is_digital(self):
    #     return (self.pin == DIGITAL)

    def set_descriptor(self, descriptor):
        self.descriptor = descriptor
##########################


class DigitalSensor(Sensor):
    '''
    Implements read and write methods
    '''
    def __init__(self, port, pinmode, gpg):
        debug("DigitalSensor init")
        Sensor.__init__(self, port, pinmode, gpg)

    def read(self):
        '''
        '''
        self.value = self.gpg.get_grove_state(self.get_pin())
        return self.value

    def write(self, power):
        self.value = power
        # not ported to GPG3 yet
        return -1
        return gopigo.digitalWrite(self.get_port_ID(), power)
##########################


class AnalogSensor(Sensor):
    '''
    implements read and write methods
    '''
    def __init__(self, port, pinmode, gpg):
        debug("AnalogSensor init")
        self.value = 0
        self.freq = 24000
        Sensor.__init__(self, port, pinmode, gpg)

        # this delay is at least needed by the Light sensor
        time.sleep(0.01)

    def read(self):
        self.value = self.gpg.get_grove_analog(self.get_pin())
        return self.value

    def percent_read(self):
        '''
        brings the sensor read to a percent scale
        '''
        reading_percent = self.read() * 100 // 4096
        return reading_percent

    def write(self, power):
        self.value = power
        return_value = self.gpg.set_grove_pwm_duty(self.get_pin(),
                                                       power)
        return return_value

    def write_freq(self, freq):
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
    Creates a light sensor from which we can read.
    Light sensor is by default on pin A1(A-one)
    self.pin takes a value of 0 when on analog pin (default value)
        takes a value of 1 when on digital pin
    """
    def __init__(self, port="AD1", gpg=None):
        debug("LightSensor init")
        AnalogSensor.__init__(self, port, "INPUT", gpg)
        self.set_pin(1)
        self.set_descriptor("Light sensor")
##########################


class SoundSensor(AnalogSensor):
    """
    Creates a sound sensor
    """
    def __init__(self, port="AD1", gpg=None):
        debug("Sound Sensor on port " + port)
        AnalogSensor.__init__(self, port, "INPUT", gpg)
        self.set_pin(1)
        self.set_descriptor("Sound sensor")

##########################


class UltraSonicSensor(AnalogSensor):

    def __init__(self, port="AD1", gpg=None):
        try:
            debug("Ultrasonic Sensor on port " + port)
            AnalogSensor.__init__(self, port, "US", gpg)
            self.safe_distance = 500
            self.set_pin(1)
            self.set_descriptor("Ultrasonic sensor")

        except Exception as e:
            raise IOError(e)

    def is_too_close(self):
        if self.gpg.get_grove_value(self.get_port_ID()) < \
           self.get_safe_distance():
            return True
        return False

    def set_safe_distance(self, dist):
        self.safe_distance = int(dist)

    def get_safe_distance(self):
        return self.safe_distance

    def read_mm(self):
        '''
        Ultrasonic sensor is limited to 15-4300 range in mm
        Take 3 readings, discard any that's higher than 4300 or lower than 15
        If we discard 5 times, then assume there's nothing in front
            and return 501
        '''
        return_reading = 0
        readings = []
        skip = 0
        value=0

        while len(readings) < 3 and skip < 5:
            try:
                print("taking a reading")
                value = self.gpg.get_grove_value(self.get_port_ID())
            except:
                skip += 1
                time.sleep(0.05)
                continue

            if value < 4300 and value > 14:
                readings.append(value)
                debug (readings)
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

        return_reading = int(return_reading // len(readings))

        return (return_reading)

    def read(self):
        # returns value in cm
        value = self.read_mm()
        if value > 15 and value <= 5010:
            return value // 10
        return value

    def read_inches(self):
        value = self.read()   # cm reading
        if value == 501:
            return 501
        return (int(value / 2.54))
##########################


class Buzzer(AnalogSensor):
    '''
    Default port is AD1
    It has three methods:
    sound(power) -> will change incoming power to 0 or 50
    note: 50 duty cycle allows for musical tones
    sound_off() -> which is the same as _sound(0)
    sound_on() -> which is the same as _sound(50)
    '''

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
        try:
            AnalogSensor.__init__(self, port, "OUTPUT", gpg)
            self.set_pin(1)
            self.set_descriptor("Buzzer")
            self.power = 50
            self.freq = 329
            self.sound_off()
        except:
            raise AttributeError

    def sound(self, freq):
        '''
        '''
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
        '''
        Makes buzzer silent
        '''
        self.sound(0)

    def sound_on(self):
        '''
        Default buzzer sound. It will take the internal frequency as is
        '''
        self.sound(self.freq)
##########################


class Led(AnalogSensor):
    def __init__(self, port="AD1", gpg=None):
        try:
            AnalogSensor.__init__(self, port, "OUTPUT", gpg)
            self.set_pin(1)
            self.set_descriptor("LED")
        except Exception as e:
            print(e)
            raise ValueError

    def light_on(self, power):
        self.write(power)

    def light_max(self):
        max_power = 100
        self.light_on(max_power)

    def light_off(self):
        self.write(0)

    def is_on(self):
        return (self.value > 0)

    def is_off(self):
        return (self.value == 0)
##########################


# class MotionSensor(DigitalSensor):
#     def __init__(self, port="D11", gpg=None):
#         DigitalSensor.__init__(self, port, "INPUT", gpg)
#         self.set_descriptor("Motion Sensor")
##########################


class ButtonSensor(DigitalSensor):

    def __init__(self, port="AD1", gpg=None):
        DigitalSensor.__init__(self, port, "DIGITAL_INPUT", gpg)
        self.set_pin(1)
        self.set_descriptor("Button sensor")

    def is_button_pressed(self):
        return self.read() == 1
##########################


# class Remote(Sensor):

#     def __init__(self, port="AD1", gpg=None):
#         Sensor.__init__(self, port, "IR", gpg)
#         self.set_descriptor("Remote Control")

#     def get_remote_code(self):
#         '''
#         Returns the keycode from the remote control
#         '''
#         self.get_grove_value(self.getPortID())

##########################


class LineFollower(Sensor):
    '''
    The line follower detects the presence of a black line or its
      absence.
    You can use this in one of three ways.
    1. You can use read_position() to get a simple position status:
        center, left or right.
        these indicate the position of the black line.
        So if it says left, the GoPiGo has to turn right
    2. You can use read() to get a list of the five sensors.
        each position in the list will either be a 0 or a 1
        It is up to you to determine where the black line is.
    3. You can use read_raw_sensors() to get raw values from all sensors
        You will have to handle the calibration yourself
    '''

    def __init__(self, port="I2C", gpg=None):
        try:
            Sensor.__init__(self, port, "INPUT", gpg)
            self.set_descriptor("Line Follower")
        except Exception as e:
            print (e)
            raise ValueError("Line Follower Library not found")

    def read_raw_sensors(self):
        '''
        Returns raw values from all sensors
        From 0 to 1023
        May return a list of -1 when there's a read error
        '''

        five_vals = line_sensor.read_sensor()

        if five_vals != -1:
            return five_vals
        else:
            return [-1, -1, -1, -1, -1]

    def get_white_calibration(self):
        return line_sensor.get_white_line()

    def get_black_calibration(self):
        return line_sensor.get_black_line()

    def read(self):
        '''
        Returns a list of 5 values between 0 and 1
        Depends on the line sensor being calibrated first
            through the Line Sensor Calibration tool
        May return all -1 on a read error
        '''
        five_vals = scratch_line.absolute_line_pos()

        return five_vals

    def read_position(self):
        '''
        Returns a string telling where the black line is, compared to
            the GoPiGo
        Returns: "Left", "Right", "Center", "Black", "White"
        May return "Unknown"
        This method is not intelligent enough to handle intersections.
        '''
        five_vals = [-1, -1, -1, -1, -1]


        five_vals = self.read()

        if five_vals == [0, 0, 1, 0, 0] or five_vals == [0, 1, 1, 1, 0]:
            return "Center"
        if five_vals == [1, 1, 1, 1, 1]:
            return "Black"
        if five_vals == [0, 0, 0, 0, 0]:
            return "White"
        if five_vals == [0, 1, 1, 0, 0] or \
           five_vals == [0, 1, 0, 0, 0] or \
           five_vals == [1, 0, 0, 0, 0] or \
           five_vals == [1, 1, 0, 0, 0] or \
           five_vals == [1, 1, 1, 0, 0] or \
           five_vals == [1, 1, 1, 1, 0]:
            return "Left"
        if five_vals == [0, 0, 0, 1, 0] or \
           five_vals == [0, 0, 1, 1, 0] or \
           five_vals == [0, 0, 0, 0, 1] or \
           five_vals == [0, 0, 0, 1, 1] or \
           five_vals == [0, 0, 1, 1, 1] or \
           five_vals == [0, 1, 1, 1, 1]:
            return "Right"
        return "Unknown"
##########################


class Servo(Sensor):
    '''
    Wrapper to control the Servo Motors on the GPG3.
    Allows you to rotate the servo by feeding in the angle of rotation.
    Connect the Servo to the Servo1 and Servo2 ports of GPG3.
    '''

    def __init__(self, port="SERVO1", gpg=None):
        try:
            Sensor.__init__(self, port, "OUTPUT", gpg)
            self.set_descriptor("GoPiGo3 Servo")
        except:
            raise ValueError("GoPiGo3 Servo not found")

    def rotate_servo(self, servo_position):
        '''
        This calculation will vary with servo and is an approximate anglular movement of the servo
        Pulse Width varies between 575us to 24250us for a 60KHz Servo Motor which rotates between 0 to 180 degrees
        0 degree ~= 575us
        180 degree ~= 2425us
        Pulse width Range= 2425-575 =1850
        => 1 degree rotation requires ~= 10.27us
        '''

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
        self.gpg.set_servo(self.portID, 0)

#######################################################################
#
# DistanceSensor
#
# under try/except in case the Distance Sensor is not installed
#######################################################################
try:
    from Distance_Sensor import distance_sensor

    class DistanceSensor(Sensor, distance_sensor.DistanceSensor):
        '''
        Wrapper to measure the distance in cms from the DI distance sensor.
        Connect the distance sensor to I2C port.
        '''
        def __init__(self, port="I2C1",gpg=None):
            Sensor.__init__(self, port, "OUTPUT", gpg)
            try:
                distance_sensor.DistanceSensor.__init__(self)
            except Exception as e:
                # print(e)
                raise IOError("Distance Sensor not found")

            self.set_descriptor("Distance Sensor")

        # Returns the values in cms
        def read_mm(self):

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
                    mm = self.readRangeSingleMillimeters()
                except:
                    mm = 0
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
            cm = self.read_mm()//10
            return (cm)

        def read_inches(self):
            cm = self.read()
            return cm / 2.54

except Exception as e:
    # it is possible to use easygopigo3 on Raspbian without having
    # the distance sensor library installed.
    # if that's the case, just ignore
    # print("Note: Distance Sensor library not installed")
    # print(e)
    pass


class DHTSensor(Sensor):
    '''
    Support for the Adafruit DHT sensor, blue or white
    All imports are done internally so it's done on a as needed basis only
        as in many cases the DHT sensor is not connected.
    '''
    def __init__(self, port="SERIAL",gpg=None, sensor_type=0):
        try:
            import threading

            Sensor.__init__(self,port,"INPUT",gpg)

            self.sensor_type = sensor_type

            # here we keep the temperature values after removing outliers
            self.filtered_temperature = []

            # here we keep the filtered humidity values after removing the outliers
            self.filtered_humidity = []

            # we are using an event so we can close the thread as soon as KeyboardInterrupt is raised
            self.event = threading.Event()
            if self.sensor_type == 0:
                self.set_descriptor("Blue DHT Sensor")
            else:
                self.set_descriptor("White DHT Sensor")

        except Exception as e:
            print("DHTSensor: {}".format(e))
            raise ValueError("DHT Sensor not found")

    def read_temperature(self):
        '''
        Return values may be a float, or error strings
        TBD: raise errors instead of returning strings
        import done internally so it's done on a as needed basis only
        '''

        from DHT_Sensor import DHT

        _grab_read()
        temp = DHT.dht(self.sensor_type)[0]
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
        import threading
        from DHT_Sensor import DHT

        _grab_read()
        humidity = DHT.dht(self.sensor_type)[1]
        _release_read()

        if humidity == -2:
            return "Bad reading, trying again"
        elif humidity == -3:
            return "Run the program as sudo"
        else:
            # print("Humidity = %.02f%%"%humidity)
            return humidity

    def read_dht(self):
        from DHT_Sensor import DHT

        _grab_read()
        [temp , humidity]=DHT.dht(self.sensor_type)
        _release_read()

        if temp ==-2.0 or humidity == -2.0:
            return "Bad reading, trying again"
        elif temp ==-3.0 or humidity == -3.0:
            return "Run the program as sudo"
        else:
            print("Temperature = %.02fC Humidity = %.02f%%"%(temp, humidity))
            return [temp, humidity]

    def _eliminateNoise(self, values, std_factor = 2):
        """
        function which eliminates the noise by using a statistical model we determine the standard normal deviation and we exclude anything that goes beyond a threshold think of a probability distribution plot - we remove the extremes the greater the std_factor, the more "forgiving" is the algorithm with the extreme values
        """
        import numpy

        mean = numpy.mean(values)
        standard_deviation = numpy.std(values)

        if standard_deviation == 0:
            return values

        final_values = [element for element in values if element > mean - std_factor * standard_deviation]

        final_values = [element for element in final_values if element < mean + std_factor * standard_deviation]

        return final_values

    def _readingValues(self,sensor_type=0):
        """function for processing the data filtering, periods of time, yada yada
        """

        import threading
        from DHT_Sensor import DHT
        import numpy
        import math
        # after this many second we make a record
        seconds_window = 10

        values = []
        while not self.event.is_set():
            counter = 0
            while counter < seconds_window and not self.event.is_set():
                temp = None
                humidity = None

                _grab_read()
                try:
                    [temp, humidity] = DHT.dht(sensor_type)
                except IOError:
                    print("we've got IO error")
                _release_read()

                if math.isnan(temp) == False and math.isnan(humidity) == False:
                    values.append({"temp" : temp, "hum" : humidity})
                    counter += 1
                #else:
                    #print("we've got NaN")
                time.sleep(1)

        self.filtered_temperature.append(numpy.mean(self._eliminateNoise([x["temp"] for x in values])))
        self.filtered_humidity.append(numpy.mean(self._eliminateNoise([x["hum"] for x in values])))

        values = []

    def continuous_read_dht(self):
        """
        Function used to Read the values continuously and displays values after normalising them
        """
        import threading

        try:
            # here we start the thread we use a thread in order to gather/process the data separately from the printing process
            data_collector = threading.Thread(target = self._readingValues)
            data_collector.start()

            while not self.event.is_set():
                if len(self.filtered_temperature) > 0:
                # or we could have used filtered_humidity instead

                    temperature = self.filtered_temperature.pop()
                    humidity = self.filtered_humidity.pop()

            # here you can do whatever you want with the variables: print them, file them out, anything
            print('{},Temperature:{:.01f}C, Humidity:{:.01f}%' .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),temperature,humidity))

            # wait a second before the next check
            time.sleep(1)

            # wait until the thread is finished
            data_collector.join()

        except Exception as e:
            self.event.set()
            print ("continuous_read_dht: {}".format(e))


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
