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

import subprocess # for executing system calls
import spidev
import math       # import math for math.pi constant

FIRMWARE_VERSION_REQUIRED = "0.2.x" # Make sure the top 2 of 3 numbers match

GPG_SPI = spidev.SpiDev()
GPG_SPI.open(0, 1)
GPG_SPI.max_speed_hz = 500000
GPG_SPI.mode = 0b00
GPG_SPI.bits_per_word = 8


class Enumeration(object):
    def __init__(self, names):  # or *names, with no .split()
        number = 0
        for line, name in enumerate(names.split('\n')):
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


class GoPiGo3(object):
    WHEEL_BASE_WIDTH         = 128  # distance in mm from left wheel to right wheel
    WHEEL_DIAMETER           = 66.5 # wheel diameter in mm
    WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * math.pi # The circumference of the circle the wheels will trace while turning
    WHEEL_CIRCUMFERENCE      = WHEEL_DIAMETER   * math.pi # The circumference of the wheels

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
    """)

    GROVE_TYPE = Enumeration("""
        CUSTOM,
        IR_GO_BOX,
        IR_EV3,
    """)

    LED_LEFT_EYE     = 0x02
    LED_RIGHT_EYE     = 0x01
    LED_LEFT_BLINKER  = 0x04
    LED_RIGHT_BLINKER = 0x08
    LED_EYE_LEFT = LED_LEFT_EYE
    LED_EYE_RIGHT = LED_RIGHT_EYE
    LED_BLINKER_LEFT = LED_LEFT_BLINKER
    LED_BLINKER_RIGHT = LED_RIGHT_BLINKER
    LED_WIFI  = 0x80 # Used to indicate WiFi status. Should not be controlled by the user.

    SERVO_1 = 0x01
    SERVO_2 = 0x02

    MOTOR_LEFT  = 0x01
    MOTOR_RIGHT = 0x02

    MOTOR_FLOAT = -128

    #MOTOR_TICKS_PER_DEGREE = ((120.0 * 16.0) / 360.0) # encoder ticks per output shaft rotation degree
    MOTOR_TICKS_PER_DEGREE = ((220.0 * 16.0) / 360.0) # encoder ticks per output shaft rotation degree

    GROVE_1_1 = 0x01
    GROVE_1_2 = 0x02
    GROVE_2_1 = 0x04
    GROVE_2_2 = 0x08

    GROVE_1 = GROVE_1_1 + GROVE_1_2
    GROVE_2 = GROVE_2_1 + GROVE_2_2

    GroveType = [0, 0]

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

    def __init__(self, addr = 8, detect = True):
        """
        Do any necessary configuration, and optionally detect the GoPiGo3

        * Optionally set the SPI address to something other than 8
        * Optionally disable the detection of the GoPiGo3 hardware. This can be used for debugging
          and testing when the GoPiGo3 would otherwise not pass the detection tests.
        """

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

    def spi_transfer_array(self, data_out):
        """
        Conduct a SPI transaction

        Keyword arguments:
        data_out -- a list of bytes to send. The length of the list will determine how many bytes are transferred.

        Returns a list of the bytes read.
        """
        return GPG_SPI.xfer2(data_out)

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
        return ("%d.%d.%d" % ((version / 1000000), ((version / 1000) % 1000), (version % 1000)))

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
            speed = int(reply[5])
            if speed & 0x80:
                speed = speed - 0x100

            encoder = int((reply[6] << 24) | (reply[7] << 16) | (reply[8] << 8) | reply[9])
            if encoder & 0x80000000:
                encoder = int(encoder - 0x100000000)

            dps = int((reply[10] << 8) | reply[11])
            if dps & 0x8000:
                dps = dps - 0x10000

            return [reply[4], speed, int(encoder / self.MOTOR_TICKS_PER_DEGREE), int(dps / self.MOTOR_TICKS_PER_DEGREE)]
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

    def set_grove_type(self, port, type):
        """
        Set grove type

        Keyword arguments:
        port -- The grove port(s). GROVE_1 and/or GROVE_2.
        type -- The grove device type
        """
        for p in range(2):
            if port & (1 << p):
                self.GroveType[p] = type
        outArray = [self.SPI_Address, self.SPI_MESSAGE_TYPE.SET_GROVE_TYPE, port, type]
        reply = self.spi_transfer_array(outArray)

    def set_grove_mode(self, pin, mode):
        """
        Set grove analog digital pin mode as INPUT/OUTPUT

        Keyword arguments:
        pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
        mode -- The pin mode. GROVE_INPUT, GROVE_OUTPUT, GROVE_INPUT_DIGITAL_PULLUP, or GROVE_INPUT_DIGITAL_PULLDOWN.
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

    def set_grove_pwm_frequency(self, port, freq = 0):
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

        if self.GroveType[port_index] == self.GROVE_TYPE.IR_EV3:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index]):
                    return [reply[5], reply[6], reply[7], reply[8]]
                else:
                    raise SensorError("get_grove_value error: Invalid value")
            else:
                raise IOError("get_grove_value error: No SPI response")

        elif self.GroveType[port_index] == self.GROVE_TYPE.IR_GO_BOX:
            outArray = [self.SPI_Address, message_type, 0, 0, 0, 0]
            reply = self.spi_transfer_array(outArray)
            if(reply[3] == 0xA5):
                if(reply[4] == self.GroveType[port_index]):
                    return reply[5]
                else:
                    raise SensorError("get_grove_value error: Invalid value")
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
            return

        value = self.spi_read_8(message_type)
        return value

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
            return

        value = self.spi_read_16(message_type)
        return (value / 1000.0)

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
            return

        value = self.spi_read_16(message_type)
        return value

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
        self.set_led(self.LED_LEFT_EYE + self.LED_RIGHT_EYE + self.LED_LEFT_BLINKER + self.LED_RIGHT_BLINKER, 0, 0, 0)

#   Read the DHT sensor connected to the serial port 
    def dht(self,sensor_type=0):
        try:
                import Adafruit_DHT
                if sensor_type==0: #blue sensor
                    sensor = Adafruit_DHT.DHT11
                elif sensor_type==1: #white sensor
                    sensor = Adafruit_DHT.DHT22     
                pin = 15 #connected to the serial port on the GoPiGo, RX pin
                humidity, temperature = Adafruit_DHT.read_retry(sensor, pin,retries=3,delay_seconds=.1)
                if humidity is not None and temperature is not None:
                        return [temperature,humidity]
                else:
                        return [-2.0,-2.0]
        except RuntimeError:
                return [-3.0,-3.0]

