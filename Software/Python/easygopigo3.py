#!/usr/bin/env python
from __future__ import print_function
from __future__ import division
# from builtins import input

import sys
# import tty
# import select
import time
import gopigo3
import picamera
from glob import glob  # for USB checking
import os

# not used yet but will be
from subprocess import check_output, CalledProcessError
from multiprocessing import Process, Lock

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


def _wait_for_read():
    timeout = 0
    while read_is_open is False and timeout < 100:
        time.sleep(0.01)
        timeout += 1
    if timeout > 99:
        return False
    else:
        return True


def _is_read_open():
    return read_is_open


def _grab_read():
    global read_is_open
    # debug("grab")
    read_is_open = False


def _release_read():
    global read_is_open
    # debug("release")
    read_is_open = True

#####################################################################
#
# USB SUPPORT
#
#####################################################################


def check_usb():
    '''
    will return the path to the USB key if there's one that's mounted
    will return false otherwise
    '''
    if len(_get_mount_points()) == 1:
        return _get_mount_points()[0][1]
    return False


def create_folder_on_usb(foldername):
    usb_path = check_usb()
    if usb_path is not False:
        try:
            os.mkdir(usb_path + "/" + foldername, 0755)
            return True
        except:
            return False


def _get_usb_devices():
    '''
    gets a list of devices that could be a usb
    '''
    sdb_devices = map(os.path.realpath, glob('/sys/block/sd*'))
    usb_devices = (dev for dev in sdb_devices
                   if 'usb' in dev.split('/')[5])
    return dict((os.path.basename(dev), dev) for dev in usb_devices)


def _get_mount_points(devices=None):
    '''
    returns a list of all mounted USBs
    '''
    # if devices are None: get_usb_devices
    devices = devices or _get_usb_devices()

    output = check_output(['mount']).splitlines()
    is_usb = lambda path: any(dev in path for dev in devices)
    usb_info = (line for line in output if is_usb(line.split()[0]))
    return [(info.split()[0], info.split()[2]) for info in usb_info]

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
        # Limit the speed
        self.set_motor_limits(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                              dps=self.get_speed())

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
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0)
            _release_read()

    def forward(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed())
            _release_read()

    def drive_cm(self, dist, blocking=False):
        # dist is in cm
        # if dist is negative, this becomes a backward move

        dist_mm = dist * 10

        # the number of degrees each wheel needs to turn
        WheelTurnDegrees = ((dist_mm / self.WHEEL_CIRCUMFERENCE) * 360)

        # get the starting position of each motor
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
            StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

            self.set_motor_position(self.MOTOR_LEFT,
                                    (StartPositionLeft + WheelTurnDegrees))
            self.set_motor_position(self.MOTOR_RIGHT,
                                    (StartPositionRight + WheelTurnDegrees))

            _release_read()

            if blocking:
                while self.target_reached(
                        StartPositionLeft + WheelTurnDegrees,
                        StartPositionRight + WheelTurnDegrees) is False:
                    time.sleep(0.1)

    def drive_inches(self, dist, blocking=False):
        self.drive_cm(dist * 2.54, blocking)

    def drive_degrees(self, degrees, blocking=False):
        # degrees is in degrees, not radians
        # if degrees is negative, this becomes a backward move

        _wait_for_read()
        if _is_read_open():
            _grab_read()
            # get the starting position of each motor
            StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
            StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

            self.set_motor_position(self.MOTOR_LEFT,
                                    (StartPositionLeft + degrees))
            self.set_motor_position(self.MOTOR_RIGHT,
                                    (StartPositionRight + degrees))

            _release_read()

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

        _wait_for_read()
        if _is_read_open():
            _grab_read()
            current_left_position = self.get_motor_encoder(self.MOTOR_LEFT)
            current_right_position = self.get_motor_encoder(self.MOTOR_RIGHT)
            _release_read()

        if current_left_position > min_left_target and \
           current_left_position < max_left_target and \
           current_right_position > min_right_target and \
           current_right_position < max_right_target:
            return True
        else:
            return False

    def backward(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_motor_dps(self.MOTOR_LEFT + self.MOTOR_RIGHT,
                               self.get_speed() * -1)
            _release_read()

    def left(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_motor_dps(self.MOTOR_LEFT, self.get_speed())
            self.set_motor_dps(self.MOTOR_RIGHT, 0)
            _release_read()

    def right(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_motor_dps(self.MOTOR_LEFT, 0)
            self.set_motor_dps(self.MOTOR_RIGHT, self.get_speed())
            _release_read()

    def blinker_on(self, id):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            if id == 1 or id == "left":
                self.set_led(self.LED_LEFT_BLINKER, 255)
            if id == 0 or id == "right":
                self.set_led(self.LED_RIGHT_BLINKER, 255)
            _release_read()

    def blinker_off(self, id):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            if id == 1:
                self.set_led(self.LED_LEFT_BLINKER, 0)
            if id == 0:
                self.set_led(self.LED_RIGHT_BLINKER, 0)
            _release_read()

    def led_on(self, id):
        self.blinker_on(id)

    def led_off(self, id):
        self.blinker_off(id)

    def set_left_eye_color(self, color):
        if isinstance(color, tuple) and len(color) == 3:
            self.left_eye_color = color
        else:
            raise TypeError

    def set_right_eye_color(self, color):
        if isinstance(color, tuple) and len(color) == 3:
            self.right_eye_color = color
        else:
            raise TypeError

    def set_eye_color(self, color):
        self.set_left_eye_color(color)
        self.set_right_eye_color(color)

    def open_left_eye(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_led(self.LED_LEFT_EYE,
                         self.left_eye_color[0],
                         self.left_eye_color[1],
                         self.left_eye_color[2],
                         )
            _release_read()

    def open_right_eye(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_led(self.LED_RIGHT_EYE,
                         self.left_eye_color[0],
                         self.left_eye_color[1],
                         self.left_eye_color[2],
                         )
            _release_read()

    def open_eyes(self):
        self.open_left_eye()
        self.open_right_eye()

    def close_left_eye(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_led(self.LED_LEFT_EYE, 0, 0, 0)
            _release_read()

    def close_right_eye(self):
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            self.set_led(self.LED_RIGHT_EYE, 0, 0, 0)
            _release_read()

    def close_eyes(self):
        self.close_left_eye()
        self.close_right_eye()

    def turn_degrees(self, degrees):
        # the distance in mm that each wheel needs to travel
        WheelTravelDistance = ((self.WHEEL_BASE_CIRCUMFERENCE * degrees) / 360)

        # the number of degrees each wheel needs to turn
        WheelTurnDegrees = ((WheelTravelDistance / self.WHEEL_CIRCUMFERENCE) *
                            360)

        _wait_for_read()
        if _is_read_open():
            _grab_read()
            # get the starting position of each motor
            StartPositionLeft = self.get_motor_encoder(self.MOTOR_LEFT)
            StartPositionRight = self.get_motor_encoder(self.MOTOR_RIGHT)

            # Set each motor target
            self.set_motor_position(self.MOTOR_LEFT,
                                    (StartPositionLeft + WheelTurnDegrees))
            self.set_motor_position(self.MOTOR_RIGHT,
                                    (StartPositionRight - WheelTurnDegrees))
            _release_read()


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


# ANALOG = 1
# DIGITAL = 0
# SERIAL = -1
# I2C = -2

##########################


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

        _wait_for_read()
        if _is_read_open():
            _grab_read()
            if pinmode == "INPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_INPUT_ANALOG)
            if pinmode == "OUTPUT":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.CUSTOM)
                self.gpg.set_grove_mode(self.portID,
                                        self.gpg.GROVE_OUTPUT_PWM)
            if pinmode == "US":
                self.gpg.set_grove_type(self.portID,
                                        self.gpg.GROVE_TYPE.US)
            _release_read()

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
        else:
            self.portID = -3

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
        # self.pin = DIGITAL
        Sensor.__init__(self, port, pinmode, gpg)

    def read(self):
        '''
        tries to get a value up to 10 times.
        As soon as a valid value is read, it returns either 0 or 1
        returns -1 after 10 unsuccessful tries
        '''
        okay = False
        error_count = 0

        _wait_for_read()

        if _is_read_open():
            _grab_read()
            rtn = -1
            while not okay and error_count < 10:
                try:
                    # not ported to gpg3 yet
                    # rtn = int(gopigo.digitalRead(self.get_port_ID()))
                    okay = True
                except:
                    error_count += 1
            _release_read()
            if error_count > 10:
                return -1
            else:
                return rtn

    def write(self, power):
        self.value = power
        # not ported to GPG3 yet
        return -1
        # return gopigo.digitalWrite(self.get_port_ID(), power)
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

    def read(self):
        _wait_for_read()

        if _is_read_open():
            _grab_read()
            self.value = self.gpg.get_grove_analog(self.get_pin())
            _release_read()
        return self.value

    def percent_read(self):
        '''
        brings the sensor read to a percent scale
        '''
        reading_percent = self.read() * 100 // 4096
        return reading_percent

    def write(self, power):
        self.value = power
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            return_value = self.gpg.set_grove_pwm_duty(self.get_pin(),
                                                       power)
            # debug ("Analog Write on {} at {}".format(self.get_pin(),
            #                                          power))
            _release_read()
        return return_value

    def write_freq(self, freq):
        self.freq = freq
        # debug("write_freq: {}".format(self.freq))
        _wait_for_read()
        if _is_read_open():
            _grab_read()
            return_value = self.gpg.set_grove_pwm_frequency(
                self.get_port_ID(),
                self.freq)
            debug ("Analog Write on {} at {}".format(self.get_port_ID(),
                                                     self.freq))
            _release_read()
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

        except:
            raise AttributeError

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

        # THREAD SAFE
        _wait_for_read()
        if _is_read_open():
            _grab_read()

            while len(readings) < 3:
                try:
                    value = self.gpg.get_grove_value(self.get_port_ID())
                except:
                    continue

                if value < 4300 and value > 14:
                    readings.append(value)
                    # debug (readings)
                else:
                    skip += 1
                    if skip > 5:
                        break
            _release_read()

        if skip > 5:
            # no special meaning to the number 501
            return(5010)

        for reading in readings:
            return_reading += reading

        return_reading = int(return_reading // len(readings))

        return (return_reading)

    def read(self):
        # returns value in cm
        value = self.read_mm()
        if value > 15 and value < 5010:
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


class MotionSensor(DigitalSensor):
    def __init__(self, port="D11", gpg=None):
        DigitalSensor.__init__(self, port, "INPUT", gpg)
        self.set_descriptor("Motion Sensor")
##########################


class ButtonSensor(DigitalSensor):

    def __init__(self, port="D11", gpg=None):
        DigitalSensor.__init__(self, port, "INPUT", gpg)
        self.set_descriptor("Button sensor")
##########################


class Remote(Sensor):

    def __init__(self, port="SERIAL", gpg=None):
        global IR_RECEIVER_ENABLED
        # IR Receiver
        try:
            import ir_receiver
            import ir_receiver_check
            IR_RECEIVER_ENABLED = True
        except:
            IR_RECEIVER_ENABLED = False

        if ir_receiver_check.check_ir() == 0:
            print("*** Error with the Remote Controller")
            print("Please enable the IR Receiver in the Advanced Comms tool")
            IR_RECEIVER_ENABLED = False
        else:
            Sensor.__init__(self, port, "SERIAL", gpg=None)
            self.set_descriptor("Remote Control")

    def is_enabled(self):
        return IR_RECEIVER_ENABLED

    def get_remote_code(self):
        '''
        Returns the keycode from the remote control
        No preprocessing
        You have to check that length > 0
            before handling the code value
        if the IR Receiver is not enabled, this will return -1
        '''
        if IR_RECEIVER_ENABLED:
            return ir_receiver.nextcode()
        else:
            print("Error with the Remote Controller")
            print("Please enable the IR Receiver in the Advanced Comms tool")
            return -1
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
        _wait_for_read()

        _grab_read()
        five_vals = line_sensor.read_sensor()
        _release_read()

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
        _wait_for_read()

        if _is_read_open():
            _grab_read()
            five_vals = scratch_line.absolute_line_pos()
            _release_read()

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

        _wait_for_read()
        if _is_read_open():
            _grab_read()
            five_vals = self.read()
            _release_read()

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


class EasyCamera(picamera.PiCamera):
    '''
    Wrapper around the PiCamera driver
    you can set the resolution if you want to.
    And take_photo() will take care of the delay that's required
        to initialize the camera properly
    '''
    def __init__(self, resolution=(1920, 1080), gpg=None):
        picamera.PiCamera.__init__(self)
        self.resolution = resolution
        self.start_time = time.time()  # timestamp on creation

    def take_photo(self, filename):
        # 2 seconds must have passed since the start of the program
        # in order to be able to take a photo
        # known as "camera warm-up time"

        # check for the presence of a properly mounted USB key
        path = check_usb()
        if path is False:
            return False

        # ensure we have waited long enough for camera
        # to be properly initialised
        while time.time() - self.start_time < 2:
            time.sleep(0.1)

        # now we can take a photo. Smile!
        self.capture(path + "/" + filename)
        return True


if __name__ == '__main__':
    b = Buzzer()
    print (b)
    print ("Sounding buzzer")
    b.sound_on()
    time.sleep(1)
    print ("buzzer off")
    b.sound_off()
