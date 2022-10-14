# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# Python drivers for the GoPiGo3

from __future__ import print_function
from __future__ import division
#from builtins import input
hardware_connected = True
__version__ = "1.3.2"

import subprocess # for executing system calls
try:
    import spidev
    import fcntl      # for lockf mutex support
except:
    hardware_connected = False
    print ("Can't import spidev or fcntl")

import math       # import math for math.pi constant
import time
import json

FIRMWARE_VERSION_REQUIRED = "1.0.x" # Make sure the top 2 of 3 numbers match

import pigpio

if hardware_connected:
    GPG_SPI = spidev.SpiDev()
    GPG_SPI.open(0, 1)
    GPG_SPI.max_speed_hz = 500000
    GPG_SPI.mode = 0b00
    GPG_SPI.bits_per_word = 8


class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for _, name in enumerate(names.split('\n')):
            if name.find(",") >= 0:
                # strip out the spaces
                while(name.find(" ") != -1):
                    name = name[:name.find(" ")] + name[(name.find(" ") + 1):]

                # strip out the commas
                while(name.find(",") != -1):
                    name = name[:name.find(",")] + name[(name.find(",") + 1):]

                # if the value was specified
                if(name.find("=") != -1):
                    number = int(float(name[(name.find("=") + 1):]))
                    name = name[:name.find("=")]

                # optionally print to confirm that it's working correctly
                #print "%40s has a value of %d" % (name, number)

                setattr(self, name, number)
                number = number + 1


class FirmwareVersionError(Exception):
    """Exception raised if the GoPiGo3 firmware needs to be updated"""


class SensorError(Exception):
    """Exception raised if a sensor is not yet configured when trying to read it"""


class I2CError(Exception):
    """Exception raised if there was an error on an I2C bus"""


class ValueError(Exception):
    """Exception raised if trying to read an invalid value"""


class GoPiGo3(object):
    WHEEL_BASE_WIDTH         = 117  # distance (mm) from left wheel to right wheel. This works with the initial GPG3 prototype. Will need to be adjusted.
    WHEEL_DIAMETER           = 66.5 # wheel diameter (mm)
    WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * math.pi # The circumference of the circle the wheels will trace while turning (mm)
    WHEEL_CIRCUMFERENCE      = WHEEL_DIAMETER   * math.pi # The circumference of the wheels (mm)

    MOTOR_GEAR_RATIO           = 120 # Motor gear ratio # 220 for Nicole's prototype
    ENCODER_TICKS_PER_ROTATION = 6   # Encoder ticks per motor rotation (number of magnet positions) # 16 for early prototypes
    MOTOR_TICKS_PER_DEGREE = ((MOTOR_GEAR_RATIO * ENCODER_TICKS_PER_ROTATION) / 360.0) # encoder ticks per output shaft rotation degree

    GROVE_I2C_LENGTH_LIMIT = 32

    SPI_MESSAGE_TYPE = Enumeration("""
        NONE,

        GET_MANUFACTURER,
        GET_NAME,
        GET_HARDWARE_VERSION,
        GET_FIRMWARE_VERSION,
        GET_ID,

        SET_LED,

        GET_VOLTAGE_5V,
        GET_VOLTAGE_VCC,

        SET_SERVO,

        SET_MOTOR_PWM,

        SET_MOTOR_POSITION,
        SET_MOTOR_POSITION_KP,
        SET_MOTOR_POSITION_KD,

        SET_MOTOR_DPS,

        SET_MOTOR_LIMITS,

        OFFSET_MOTOR_ENCODER,

        GET_MOTOR_ENCODER_LEFT,
        GET_MOTOR_ENCODER_RIGHT,

        GET_MOTOR_STATUS_LEFT,
        GET_MOTOR_STATUS_RIGHT,

        SET_GROVE_TYPE,
        SET_GROVE_MODE,
        SET_GROVE_STATE,
        SET_GROVE_PWM_DUTY,
        SET_GROVE_PWM_FREQUENCY,

        GET_GROVE_VALUE_1,
        GET_GROVE_VALUE_2,
        GET_GROVE_STATE_1_1,
        GET_GROVE_STATE_1_2,
        GET_GROVE_STATE_2_1,
        GET_GROVE_STATE_2_2,
        GET_GROVE_VOLTAGE_1_1,
        GET_GROVE_VOLTAGE_1_2,
        GET_GROVE_VOLTAGE_2_1,
        GET_GROVE_VOLTAGE_2_2,
        GET_GROVE_ANALOG_1_1,
        GET_GROVE_ANALOG_1_2,
        GET_GROVE_ANALOG_2_1,
        GET_GROVE_ANALOG_2_2,

        START_GROVE_I2C_1,
        START_GROVE_I2C_2,
    """)

    GROVE_TYPE = Enumeration("""
        CUSTOM = 1,
        IR_DI_REMOTE,
        IR_EV3_REMOTE,
        US,
        I2C,
    """)

    GROVE_STATE = Enumeration("""
        VALID_DATA,
        NOT_CONFIGURED,
        CONFIGURING,
        NO_DATA,
        I2C_ERROR,
    """)

    LED_EYE_LEFT      = 0x02
    LED_EYE_RIGHT     = 0x01
    LED_BLINKER_LEFT  = 0x04
    LED_BLINKER_RIGHT = 0x08
    LED_LEFT_EYE      = LED_EYE_LEFT
    LED_RIGHT_EYE     = LED_EYE_RIGHT
    LED_LEFT_BLINKER  = LED_BLINKER_LEFT
    LED_RIGHT_BLINKER = LED_BLINKER_RIGHT
    LED_WIFI  = 0x80 # Used to indicate WiFi status. Should not be controlled by the user.

    SERVO_1 = 0x01
    SERVO_2 = 0x02

    MOTOR_LEFT  = 0x01
    MOTOR_RIGHT = 0x02

    MOTOR_FLOAT = -128

    GROVE_1_1 = 0x01
    GROVE_1_2 = 0x02
    GROVE_2_1 = 0x04
    GROVE_2_2 = 0x08

    GROVE_1 = GROVE_1_1 + GROVE_1_2
    GROVE_2 = GROVE_2_1 + GROVE_2_2

    GroveType = [0, 0]
    GroveI2CInBytes = [0, 0]

    GROVE_INPUT_DIGITAL          = 0
    GROVE_OUTPUT_DIGITAL         = 1
    GROVE_INPUT_DIGITAL_PULLUP   = 2
    GROVE_INPUT_DIGITAL_PULLDOWN = 3
    GROVE_INPUT_ANALOG           = 4
    GROVE_OUTPUT_PWM             = 5
    GROVE_INPUT_ANALOG_PULLUP    = 6
    GROVE_INPUT_ANALOG_PULLDOWN  = 7

    GROVE_LOW  = 0
    GROVE_HIGH = 1

    def __init__(self, addr = 8, detect = True, config_file_path="/home/pi/Dexter/gpg3_config.json"):
        """
        Do any necessary configuration, and optionally detect the GoPiGo3

        * Optionally set the SPI address to something other than 8
        * Optionally disable the detection of the GoPiGo3 hardware. This can be used for debugging
          and testing when the GoPiGo3 would otherwise not pass the detection tests.

        The ``config_file_path`` parameter represents the path to a JSON file. The presence of this configuration file is optional and is only required in cases where
        the GoPiGo3 has a skewed trajectory due to minor differences in these two constants: the **wheel diameter** and the **wheel base width**. In most cases, this won't be the case.

        By-default, the constructor tries to read the ``config_file_path`` file and silently fails if something goes wrong: wrong permissions, non-existent file, improper key values and so on.
        To set custom values to these 2 constants, use :py:meth:`~easygopigo3.EasyGoPiGo3.set_robot_constants` method and for saving the constants to a file call
        :py:meth:`~easygopigo3.EasyGoPiGo3.save_robot_constants` method.

        """

        # Make sure the SPI lines are configured for mode ALT0 so that the hardware SPI controller can use them
        # subprocess.call('gpio mode 12 ALT0', shell=True)
        # subprocess.call('gpio mode 13 ALT0', shell=True)
        # subprocess.call('gpio mode 14 ALT0', shell=True)

        pi_gpio = pigpio.pi()
        pi_gpio.set_mode(9, pigpio.ALT0)
        pi_gpio.set_mode(10, pigpio.ALT0)
        pi_gpio.set_mode(11, pigpio.ALT0)
        pi_gpio.stop()

        self.SPI_Address = addr
        if detect == True:
            try:
                manufacturer = self.get_manufacturer()
                board = self.get_board()
                vfw = self.get_version_firmware()
            except IOError:
                raise IOError("No SPI response. GoPiGo3 with address %d not connected." % addr)
            if manufacturer != "Dexter Industries" or board != "GoPiGo3":
                raise IOError("GoPiGo3 with address %d not connected." % addr)
            if vfw.split('.')[0] != FIRMWARE_VERSION_REQUIRED.split('.')[0] or \
               vfw.split('.')[1] != FIRMWARE_VERSION_REQUIRED.split('.')[1]:
                raise FirmwareVersionError("GoPiGo3 firmware needs to be version %s but is currently version %s" \
                                           % (FIRMWARE_VERSION_REQUIRED, vfw))

        # load wheel diameter & wheel base width
        # also default ENCODER_TICKS_PER_ROTATION and MOTOR_GEAR_RATIO
        # should there be a problem doing that then save the current default configuration
        try:
            self.load_robot_constants(config_file_path)
        except Exception as e:
            pass

    def spi_transfer_array(self, data_out):
        """
        Conduct a SPI transaction

        Keyword arguments:
        data_out -- a list of bytes to send. The length of the list will determine how many bytes are transferred.

        Returns a list of the bytes read.
        """
        result = GPG_SPI.xfer2(data_out)
        return result

    def spi_read_8(self, MessageType):
        """
        Read an 8-bit value over SPI

        Keyword arguments:
        MessageType -- the SPI message type

        Returns touple:
        value, error
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int(reply[4])
        raise IOError("No SPI response")
        return 0

    def spi_read_16(self, MessageType):
        """
        Read a 16-bit value over SPI

        Keyword arguments:
        MessageType -- the SPI message type

        Returns touple:
        value, error
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 8) | reply[5])
        raise IOError("No SPI response")
        return 0

    def spi_read_32(self, MessageType):
        """
        Read a 32-bit value over SPI

        Keyword arguments:
        MessageType -- the SPI message type

        Returns touple:
        value, error
        """
        outArray = [self.SPI_Address, MessageType, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return int((reply[4] << 24) | (reply[5] << 16) | (reply[6] << 8) | reply[7])
        raise IOError("No SPI response")
        return 0

    def spi_write_32(self, MessageType, Value):
        """
        Send a 32-bit value over SPI

        Keyword arguments:
        MessageType -- the SPI message type
        Value -- the value to be sent
        """
        outArray = [self.SPI_Address, MessageType,\
                    ((Value >> 24) & 0xFF), ((Value >> 16) & 0xFF), ((Value >> 8) & 0xFF), (Value & 0xFF)]
        self.spi_transfer_array(outArray)

    def _check_serial_number_for_16_ticks(self, config_file_path="/home/pi/Dexter/gpg3_config.json"):
        '''
        Check known list of serial numbers that were shipped with 16 tick motors
        '''
        import pickle
        from os import path
        serial_path = path.split(config_file_path)[0]
        serial_file = serial_path+"/.list_of_serial_numbers.pkl"
        try:
            with open(serial_file, 'rb') as f:
                serials_with_16_ticks = pickle.load(f)
                if self.get_id() in serials_with_16_ticks:
                    return True
                else:
                    return False
        except:
            # list_of_serial_numbers file doesn't exist
            # assume 6 ticks
            return False


    def load_robot_constants(self, config_file_path="/home/pi/Dexter/gpg3_config.json"):
        """
        Load wheel diameter and wheel base width constants for the GoPiGo3 from file.

        This method gets called by the constructor.

        :param str config_file_path = "/home/pi/Dexter/gpg3_config.json": Path to JSON config file that stores the wheel diameter and wheel base width for the GoPiGo3.
        :raises FileNotFoundError: When the file is non-existent.
        :raises KeyError: If one of the keys is not part of the dictionary.
        :raises ValueError: If the saved values are not positive numbers (floats or ints).
        :raises TypeError: If the saved values are not numbers.
        :raises IOError: When the file cannot be accessed.
        :raises PermissionError: When there are not enough permissions to access the file.
        :raises json.JSONDecodeError: When the config file fails at parsing.

        Here's how the JSON config file must look like before reading it. Obviously, the supported format is JSON so that anyone can come in
        and edit their own config file if they don't want to go through saving the values by using the API.

        .. code-block:: json

            {
                "wheel-diameter": 66.5,
                "wheel-base-width": 117,
                "ticks": 6,
                "motor_gear_ratio": 120
            }

        If the file doesn't exist, one gets written for the user.
        If the file is empty (which may happens on GoPiGo OS), then the file will be overwritten with appropriate default values.
        If the file has content, the robot constants are redefined based on that content. Should tick and gear_ratio be missing, default values will be supplied.
        """

        # default values for ticks and motor_gear_ratio
        # in case they are not present in the file we load up
        ticks = self.ENCODER_TICKS_PER_ROTATION
        motor_gear_ratio = self.MOTOR_GEAR_RATIO

        try:
            with open(config_file_path, 'r') as json_file:
                data = json.load(json_file)

                # Check for the presence of ticks and positive value
                if 'ticks' in data:
                    ticks = data['ticks']

                # Check for the presence of motor_gear_ratio
                if 'motor_gear_ratio' in data:
                    motor_gear_ratio = data['motor_gear_ratio']

                if data['wheel-diameter'] > 0 and data['wheel-base-width'] > 0 and ticks > 0 and motor_gear_ratio > 0:
                    self.set_robot_constants(data['wheel-diameter'], data['wheel-base-width'], ticks, motor_gear_ratio )
                else:
                    raise ValueError('positive values required')

        except json.decoder.JSONDecodeError:
            # config file exists but is empty
            if self._check_serial_number_for_16_ticks(config_file_path):
                self.ENCODER_TICKS_PER_ROTATION = 16
            try:
                self.save_robot_constants(config_file_path)
            except:
                # protect against write errors - just in case
                pass

        except Exception as e:
            # This may happen if the file doesn't exist\
            if self._check_serial_number_for_16_ticks(config_file_path):
                self.ENCODER_TICKS_PER_ROTATION = 16
            else:
                self.ENCODER_TICKS_PER_ROTATION = 6
            try:
                self.save_robot_constants(config_file_path)
            except:
                # protect against write errors - just in case
                pass

    def save_robot_constants(self, config_file_path="/home/pi/Dexter/gpg3_config.json"):
        """
        Save the current wheel diameter and wheel base width constants (from within this object's context) for the GoPiGo3 to file for future use.

        :param str config_file_path = "/home/pi/Dexter/gpg3_config.json": Path to JSON config file that stores the wheel diameter and wheel base width for the GoPiGo3.
        :raises IOError: When the file cannot be accessed.
        :raises PermissionError: When there are not enough permissions to create the file.

        Here's how the JSON config file will end up looking like. The values can differ from case to case.

        .. code-block:: json

            {
                "wheel-diameter": 66.5,
                "wheel-base-width": 117,
                "ticks": 6,
                "motor_gear_ratio": 120
            }

        """
        with open(config_file_path, 'w') as json_file:
            data = {
                "wheel-diameter": self.WHEEL_DIAMETER,
                "wheel-base-width": self.WHEEL_BASE_WIDTH,
                "ticks": self.ENCODER_TICKS_PER_ROTATION,
                "motor_gear_ratio": self.MOTOR_GEAR_RATIO
            }
            json.dump(data, json_file)

    def set_robot_constants(self, wheel_diameter, wheel_base_width, ticks, motor_gear_ratio):
        """
        Set new wheel diameter and wheel base width values for the GoPiGo3.

        :param float wheel_diameter: Diameter of the GoPiGo3 wheels as measured in millimeters.
        :param float wheel_base_width: The distance between the 2 centers of the 2 wheels as measured in millimeters.

        This should only be required in rare cases when the GoPiGo3's trajectory is skewed due to minor differences in the wheel-to-body measurements.

        The GoPiGo3 class instantiates itself with default values for both constants:

        1. ``wheel_diameter`` is by-default set to **66.5** *mm*.

        2. ``wheel_base_width`` is by-default set to **117** *mm*.

        3. ``ticks`` is by default set to **6**, but GoPiGos manufactured in 2021 need 16.

        4. ``motor_gear_ratio`` is by default set to **120**.

        """
        self.WHEEL_DIAMETER = wheel_diameter
        self.WHEEL_CIRCUMFERENCE = self.WHEEL_DIAMETER * math.pi
        self.WHEEL_BASE_WIDTH = wheel_base_width
        self.WHEEL_BASE_CIRCUMFERENCE = self.WHEEL_BASE_WIDTH * math.pi
        self.MOTOR_GEAR_RATIO = motor_gear_ratio
        self.ENCODER_TICKS_PER_ROTATION = ticks
        self.MOTOR_TICKS_PER_DEGREE = ((self.MOTOR_GEAR_RATIO * self.ENCODER_TICKS_PER_ROTATION) / 360.0)


    def get_manufacturer(self):
        """
        Read the 20 charactor GoPiGo3 manufacturer name

        Returns touple:
        GoPiGo3 manufacturer name string, error
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.GET_MANUFACTURER,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name
        raise IOError("No SPI response")
        return ""

    def get_board(self):
        """
        Read the 20 charactor GoPiGo3 board name

        Returns touple:
        GoPiGo3 board name string, error
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.GET_NAME,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            name = ""
            for c in range(4, 24):
                if reply[c] != 0:
                    name += chr(reply[c])
                else:
                    break
            return name
        raise IOError("No SPI response")
        return ""

    def get_version_hardware(self):
        """
        Read the hardware version

        Returns touple:
        hardware version, error
        """
        version = self.spi_read_32(self.SPI_MESSAGE_TYPE.GET_HARDWARE_VERSION)
        return ("%d.x.x" % (version / 1000000))

    def get_version_firmware(self):
        """
        Read the firmware version

        Returns touple:
        firmware version, error
        """
        version = self.spi_read_32(self.SPI_MESSAGE_TYPE.GET_FIRMWARE_VERSION)
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000)))

    def get_id(self):
        """
        Read the 128-bit GoPiGo3 hardware serial number

        Returns touple:
        serial number as 32 char HEX formatted string, error
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.GET_ID,\
                    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            return ("%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X%02X" % \
            (reply[4], reply[5], reply[6], reply[7], reply[8], reply[9], reply[10], reply[11], \
             reply[12], reply[13], reply[14], reply[15], reply[16], reply[17], reply[18], reply[19]))
        raise IOError("No SPI response")
        return "00000000000000000000000000000000"

    def set_led(self, led, red, green = 0, blue = 0):
        """
        Set an LED

        Keyword arguments:
        led -- The LED(s). LED_LEFT_EYE, LED_RIGHT_EYE, LED_LEFT_BLINKER, LED_RIGHT_BLINKER, and/or LED_WIFI.
        red -- The LED's Red color component (0-255)
        green -- The LED's Green color component (0-255)
        blue -- The LED's Blue color component (0-255)
        """

        if led < 0 or led > 255:
            return

        if red > 255:
            red = 255
        if green > 255:
            green = 255
        if blue > 255:
            blue = 255

        if red < 0:
            red = 0
        if green < 0:
            green = 0
        if blue < 0:
            blue = 0

        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_LED, led, red, green, blue]
        reply = self.spi_transfer_array(outArray)

    def get_voltage_5v(self):
        """
        Get the 5v circuit voltage

        Returns touple:
        5v circuit voltage, error
        """
        value = self.spi_read_16(self.SPI_MESSAGE_TYPE.GET_VOLTAGE_5V)
        return (value / 1000.0)

    def get_voltage_battery(self):
        """
        Get the battery voltage

        Returns touple:
        battery voltage, error
        """
        value = self.spi_read_16(self.SPI_MESSAGE_TYPE.GET_VOLTAGE_VCC)
        return (value / 1000.0)

    def set_servo(self, servo, us):
        """
        Set a servo position in microseconds

        Keyword arguments:
        servo -- The servo(s). SERVO_1 and/or SERVO_2.
        us -- The pulse width in microseconds (0-16666)
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_SERVO, servo,\
                    ((us >> 8) & 0xFF), (us & 0xFF)]
        reply = self.spi_transfer_array(outArray)

    def set_motor_power(self, port, power):
        """
        Set the motor power in percent

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        power -- The PWM power from -100 to 100, or MOTOR_FLOAT for float.
        """
        if(power > 127):
            power = 127
        if(power < -128):
            power = -128
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_MOTOR_PWM, port, int(power)]
        self.spi_transfer_array(outArray)

    def set_motor_position(self, port, position):
        """
        Set the motor target position in degrees

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        position -- The target position
        """
        position_raw = int(position * self.MOTOR_TICKS_PER_DEGREE)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_MOTOR_POSITION, port,\
                    ((position_raw >> 24) & 0xFF), ((position_raw >> 16) & 0xFF),\
                    ((position_raw >> 8) & 0xFF), (position_raw & 0xFF)]
        reply = self.spi_transfer_array(outArray)

    def set_motor_dps(self, port, dps):
        """
        Set the motor target speed in degrees per second

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        dps -- The target speed in degrees per second
        """
        dps = int(dps * self.MOTOR_TICKS_PER_DEGREE)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_MOTOR_DPS, int(port),\
                    ((dps >> 8) & 0xFF), (dps & 0xFF)]
        self.spi_transfer_array(outArray)

    def set_motor_limits(self, port, power = 0, dps = 0):
        """
        Set the motor speed limit

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        power -- The power limit in percent (0 to 100), with 0 being no limit (100)
        dps -- The speed limit in degrees per second, with 0 being no limit
        """
        dps = int(dps * self.MOTOR_TICKS_PER_DEGREE)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_MOTOR_LIMITS, int(port), int(power),\
                    ((dps >> 8) & 0xFF), (dps & 0xFF)]
        self.spi_transfer_array(outArray)

    def get_motor_status(self, port):
        """
        Read a motor status

        Keyword arguments:
        port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.

        Returns a list:
            flags -- 8-bits of bit-flags that indicate motor status:
                bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically disabled because the battery voltage is too low
                bit 1 -- OVERLOADED - The motors aren't close to the target (applies to position control and dps speed control).
            power -- the raw PWM power in percent (-100 to 100)
            encoder -- The encoder position
            dps -- The current speed in Degrees Per Second
        """
        if port == self.MOTOR_LEFT:
            message_type = self.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_LEFT
        elif port == self.MOTOR_RIGHT:
            message_type = self.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_RIGHT
        else:
            raise IOError("get_motor_status error. Must be one motor port at a time. MOTOR_LEFT or MOTOR_RIGHT.")
            return

        outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            power = int(reply[5])
            if power & 0x80:
                power = power - 0x100

            encoder = int((reply[6] << 24) | (reply[7] << 16) | (reply[8] << 8) | reply[9])
            if encoder & 0x80000000:
                encoder = int(encoder - 0x100000000)

            dps = int((reply[10] << 8) | reply[11])
            if dps & 0x8000:
                dps = dps - 0x10000

            return [reply[4], power, int(encoder / self.MOTOR_TICKS_PER_DEGREE), int(dps / self.MOTOR_TICKS_PER_DEGREE)]
        raise IOError("No SPI response")
        return

    def get_motor_encoder(self, port):
        """
        Read a motor encoder in degrees

        Keyword arguments:
        port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.

        Returns the encoder position in degrees
        """
        if port == self.MOTOR_LEFT:
            message_type = self.SPI_MESSAGE_TYPE.GET_MOTOR_ENCODER_LEFT
        elif port == self.MOTOR_RIGHT:
            message_type = self.SPI_MESSAGE_TYPE.GET_MOTOR_ENCODER_RIGHT
        else:
            raise IOError("Port(s) unsupported. Must be one at a time.")
            return 0

        encoder = self.spi_read_32(message_type)
        if encoder & 0x80000000:
            encoder = int(encoder - 0x100000000)
        return int(encoder / self.MOTOR_TICKS_PER_DEGREE)

    def offset_motor_encoder(self, port, offset):
        """
        Offset a motor encoder

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        offset -- The encoder offset

        Zero the encoder by offsetting it by the current position
        """
        offset = int(offset * self.MOTOR_TICKS_PER_DEGREE)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.OFFSET_MOTOR_ENCODER, int(port),\
                    ((offset >> 24) & 0xFF), ((offset >> 16) & 0xFF), ((offset >> 8) & 0xFF), (offset & 0xFF)]
        self.spi_transfer_array(outArray)

    def reset_motor_encoder(self, port):
        """
        Reset a motor encoder to 0

        Keyword arguments:
        port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
        """
        if port & self.MOTOR_LEFT:
            self.offset_motor_encoder(self.MOTOR_LEFT, self.get_motor_encoder(self.MOTOR_LEFT))

        if port & self.MOTOR_RIGHT:
            self.offset_motor_encoder(self.MOTOR_RIGHT, self.get_motor_encoder(self.MOTOR_RIGHT))

    def set_grove_type(self, port, type):
        """
        Set grove type

        Keyword arguments:
        port -- The grove port(s). GROVE_1 and/or GROVE_2.
        type -- The grove device type
        """
        for p in range(2):
            if ((port >> (p * 2)) & 3) == 3:
                self.GroveType[p] = type
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_TYPE, port, type]
        reply = self.spi_transfer_array(outArray)

    def set_grove_mode(self, pin, mode):
        """
        Set grove analog digital pin mode as INPUT/OUTPUT

        Keyword arguments:
        pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
        mode -- The pin mode. GROVE_INPUT_DIGITAL, GROVE_OUTPUT_DIGITAL, GROVE_INPUT_DIGITAL_PULLUP, GROVE_INPUT_DIGITAL_PULLDOWN, GROVE_INPUT_ANALOG, GROVE_OUTPUT_PWM, GROVE_INPUT_ANALOG_PULLUP, or GROVE_INPUT_ANALOG_PULLDOWN.
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_MODE, pin, mode]
        reply = self.spi_transfer_array(outArray)

    def set_grove_state(self, pin, state):
        """
        Set grove output pin LOW/HIGH

        Keyword arguments:
        pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
        state -- The pin state. GROVE_LOW or GROVE_HIGH.
        """
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_STATE, pin, state]
        reply = self.spi_transfer_array(outArray)

    def set_grove_pwm_duty(self, pin, duty):
        """
        Set grove output pin PWM

        Keyword arguments:
        pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
        duty -- The PWM duty cycle in percent. Floating point.
        """
        if(duty < 0):
            duty = 0
        if(duty > 100):
            duty = 100
        duty_value = int(duty * 10.0)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_PWM_DUTY, pin,\
                    ((duty_value >> 8) & 0xFF), (duty_value & 0xFF)]
        reply = self.spi_transfer_array(outArray)

    def set_grove_pwm_frequency(self, port, freq = 24000):
        """
        Set grove PWM frequency

        Keyword arguments:
        port -- The grove port(s). GROVE_1 and/or GROVE_2.
        freq -- The PWM frequency. Range is 3 through 48000Hz. Default is 24000 (24kHz).
        """
        if(freq < 3):
            freq = 3
        if(freq > 48000): # make sure it doesn't exceed 16 bit unsigned.
            freq = 48000  # limit to 48000, which is the highest frequency supported for 0.1% resolution.
        freq_value = int(freq)
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_PWM_FREQUENCY, port,\
                    ((freq_value >> 8) & 0xFF), (freq_value & 0xFF)]
        reply = self.spi_transfer_array(outArray)

    def grove_i2c_transfer(self, port, addr, outArr, inBytes = 0):
        """
        Conduct an I2C transaction

        Keyword arguments:
        port -- The grove port. GROVE_1 or GROVE_2.
        addr -- The I2C address of the slave to be addressed.
        outArr -- A list of bytes to send.
        inBytes -- The number of bytes to read.

        Returns:
        list of bytes read from the slave
        """
        # start an I2C transaction as soon as the bus is available
        Timeout = time.time() + 0.005 # timeout after 5ms of failed attempted starts
        Continue = False
        while not Continue:
            try:
                self.grove_i2c_start(port, addr, outArr, inBytes)
                Continue = True
            except (IOError, I2CError):
                if time.time() > Timeout:
                    raise IOError("grove_i2c_transfer error: Timeout trying to start transaction")

        DelayTime = 0
        if len(outArr):
            DelayTime += 1 + len(outArr)
        if inBytes:
            DelayTime += 1 + inBytes
        DelayTime *= (0.000115) # each I2C byte takes about 115uS at full speed (about 100kbps)
        # No point trying to read the values before they are ready.
        time.sleep(DelayTime) # delay for as long as it will take to do the I2C transaction.

        Timeout = time.time() + 0.005 # timeout after 5ms of failed attempted reads
        while True:
            try:
                # read the results as soon as they are available
                values = self.get_grove_value(port)
                return values
            except (ValueError, SensorError):
                if time.time() > Timeout:
                    raise IOError("grove_i2c_transfer error: Timeout waiting for data")

    def grove_i2c_start(self, port, addr, outArr, inBytes = 0):
        """
        Start an I2C transaction

        Keyword arguments:
        port -- The grove port. GROVE_1 or GROVE_2.
        addr -- The I2C address of the slave to be addressed.
        outArr -- A list of bytes to send.
        inBytes -- The number of bytes to read.
        """
        if port == self.GROVE_1:
            message_type = self.SPI_MESSAGE_TYPE.START_GROVE_I2C_1
            port_index = 0
        elif port == self.GROVE_2:
            message_type = self.SPI_MESSAGE_TYPE.START_GROVE_I2C_2
            port_index = 1
        else:
            raise RuntimeError("Port unsupported. Must get one at a time.")

        address = ((int(addr) & 0x7F) << 1)

        if inBytes > self.GROVE_I2C_LENGTH_LIMIT:
            raise RuntimeError("Read length error. Up to %d bytes can be read in a single transaction." % self.GROVE_I2C_LENGTH_LIMIT)

        outBytes = len(outArr)
        if outBytes > self.GROVE_I2C_LENGTH_LIMIT:
            raise RuntimeError("Write length error. Up to %d bytes can be written in a single transaction." % self.GROVE_I2C_LENGTH_LIMIT)

        outArray = [self.SPI_Address, message_type, address, inBytes, outBytes]
        outArray.extend(outArr)
        reply = self.spi_transfer_array(outArray)
        self.GroveI2CInBytes[port_index] = inBytes
        if(reply[3] != 0xA5):
            raise IOError("start_grove_i2c error: No SPI response")
        if(reply[4] != 0):
            raise I2CError("start_grove_i2c error: Not ready to start I2C transaction")

    def get_grove_value(self, port):
        """
        Get a grove port value

        Keyword arguments:
        port -- The grove port. GROVE_1 or GROVE_2.
        """
        if port == self.GROVE_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_1
            port_index = 0
        elif port == self.GROVE_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_2
            port_index = 1
        else:
            raise IOError("Port unsupported. Must get one at a time.")

        if self.GroveType[port_index] == self.GROVE_TYPE.IR_DI_REMOTE:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index] and reply[5] == 0):
                    return reply[6]
                else:
                    raise SensorError("get_grove_value error: Invalid value")
            else:
                raise IOError("get_grove_value error: No SPI response")

        elif self.GroveType[port_index] == self.GROVE_TYPE.IR_EV3_REMOTE:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index] and reply[5] == 0):
                    return [reply[6], reply[7], reply[8], reply[9]]
                else:
                    raise SensorError("get_grove_value error: Invalid value")
            else:
                raise IOError("get_grove_value error: No SPI response")

        elif self.GroveType[port_index] == self.GROVE_TYPE.US:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index] and reply[5] == 0):
                    value = (((reply[6] << 8) & 0xFF00) | (reply[7] & 0xFF))
                    if value == 0:
                        raise SensorError("get_grove_value error: Sensor not responding")
                    elif value == 1:
                        raise ValueError("get_grove_value error: Object not detected within range")
                    else:
                        return value
                else:
                    raise SensorError("get_grove_value error: Invalid value")
            else:
                raise IOError("get_grove_value error: No SPI response")

        elif self.GroveType[port_index] == self.GROVE_TYPE.I2C:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0]
            outArray.extend([0 for i in range(self.GroveI2CInBytes[port_index])])
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index]):
                    if(reply[5] == self.GROVE_STATE.VALID_DATA):  # no error
                        return reply[6:]
                    elif(reply[5] == self.GROVE_STATE.I2C_ERROR): # I2C bus error
                        raise I2CError("get_grove_value error: I2C bus error")
                    else:
                        raise ValueError("get_grove_value error: Invalid value")
                else:
                    raise SensorError("get_grove_value error: Grove type mismatch")
            else:
                raise IOError("get_grove_value error: No SPI response")
        value = self.spi_read_8(message_type)
        return value

    def get_grove_state(self, pin):
        """
        Get a grove input pin state

        Keyword arguments:
        pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
        """
        if pin == self.GROVE_1_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_STATE_1_1
        elif pin == self.GROVE_1_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_STATE_1_2
        elif pin == self.GROVE_2_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_STATE_2_1
        elif pin == self.GROVE_2_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_STATE_2_2
        else:
            raise IOError("Pin(s) unsupported. Must get one at a time.")

        outArray = [self.SPI_Address, message_type, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            if(reply[4] == self.GROVE_STATE.VALID_DATA): # no error
                return reply[5]
            else:
                raise ValueError("get_grove_state error: Invalid value")
        else:
            raise IOError("get_grove_state error: No SPI response")

    def get_grove_voltage(self, pin):
        """
        Get a grove input pin analog voltage

        Keyword arguments:
        pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
        """
        if pin == self.GROVE_1_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_1_1
        elif pin == self.GROVE_1_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_1_2
        elif pin == self.GROVE_2_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_2_1
        elif pin == self.GROVE_2_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_2_2
        else:
            raise IOError("Pin(s) unsupported. Must get one at a time.")

        outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            if(reply[4] == self.GROVE_STATE.VALID_DATA): # no error
                return ((((reply[5] << 8) & 0xFF00) | (reply[6] & 0xFF)) / 1000.0)
            else:
                raise ValueError("get_grove_voltage error: Invalid value")
        else:
            raise IOError("get_grove_voltage error: No SPI response")

    def get_grove_analog(self, pin):
        """
        Get a grove input pin 12-bit raw ADC reading

        Keyword arguments:
        pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
        """
        if pin == self.GROVE_1_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_1_1
        elif pin == self.GROVE_1_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_1_2
        elif pin == self.GROVE_2_1:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_2_1
        elif pin == self.GROVE_2_2:
            message_type = self.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_2_2
        else:
            raise IOError("Pin(s) unsupported. Must get one at a time.")

        outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0]
        reply = self.spi_transfer_array(outArray)
        if(reply[3] == 0xA5):
            if(reply[4] == self.GROVE_STATE.VALID_DATA): # no error
                return (((reply[5] << 8) & 0xFF00) | (reply[6] & 0xFF))
            else:
                raise ValueError("get_grove_analog error: Invalid value")
        else:
            raise IOError("get_grove_analog error: No SPI response")

    def reset_all(self):
        """
        Reset the GoPiGo3.
        """
        # reset all sensors
        self.set_grove_type(self.GROVE_1 + self.GROVE_2, self.GROVE_TYPE.CUSTOM)
        self.set_grove_mode(self.GROVE_1 + self.GROVE_2, self.GROVE_INPUT_DIGITAL)

        # Turn off the motors
        self.set_motor_power(self.MOTOR_LEFT + self.MOTOR_RIGHT, self.MOTOR_FLOAT)

        # Reset the motor limits
        self.set_motor_limits(self.MOTOR_LEFT + self.MOTOR_RIGHT, 0, 0)

        # Turn off the servos
        self.set_servo(self.SERVO_1 + self.SERVO_2, 0)

        # Turn off the LEDs
        self.set_led(self.LED_EYE_LEFT + self.LED_EYE_RIGHT + self.LED_BLINKER_LEFT + self.LED_BLINKER_RIGHT, 0, 0, 0)
