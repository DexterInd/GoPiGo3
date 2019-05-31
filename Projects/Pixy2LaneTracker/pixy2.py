import di_i2c
import logging
import struct

logger = logging.getLogger(__name__)

# for more on the serial interface (SPI, uart, I2C) check this link
# https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:porting_guide#general-format

LINE_REQUEST_GET_FEATURES = 0x30
LINE_RESPONSE_GET_FEATURES = 0x31
LINE_REQUEST_SET_MODE = 0x36
LINE_REQUEST_SET_VECTOR = 0x38
LINE_REQUEST_SET_NEXT_TURN_ANGLE = 0x3a
LINE_REQUEST_SET_DEFAULT_TURN_ANGLE = 0x3c
LINE_REQUEST_REVERSE_VECTOR = 0x3e

LINE_GET_MAIN_FEATURES = 0x00
LINE_GET_ALL_FEATURES = 0x01

LINE_MODE_TURN_DELAYED = 0x01
LINE_MODE_MANUAL_SELECT_VECTOR = 0x02
LINE_MODE_WHITE_LINE = 0x80

LINE_VECTOR = 0x01
LINE_INTERSECTION = 0x02
LINE_BARCODE = 0x04
LINE_ALL_FEATURES = (LINE_VECTOR | LINE_INTERSECTION | LINE_BARCODE)

LINE_FLAG_INVALID = 0x02
LINE_FLAG_INTERSECTION_PRESENT = 0x04

LINE_MAX_INTERSECTION_LINES = 6


def unpack_bytes(bytes_list,
                 big_endian=True):
    """
    Unpack integers from a given list of bytes.

    :param bytes_list: List of numbers of whose elements don't go over 255.
    :param big_endian: Whether it's big endian or little endian.
    :return: The unpacked number.
    """
    out = 0
    multiplier = 1
    if big_endian:
        bytes_list = bytes_list[::-1]
    for byte_number in bytes_list:
        out += byte_number * multiplier
        multiplier <<= 8

    return out


class Pixy2I2C():

    def __init__(self, address, bus="RPI_1"):
        self.i2c_bus = di_i2c.DI_I2C(bus, address, big_endian=False)

    def get_version(self):
        """
        Get the hardware and software version of the Pixy2.

        :return: hw, sw
        """
        out = [
            # 2 sync bytes, type packet, length payload
            174, 193, 14, 0
        ]
        logger.debug('get version from pixy2')
        inp = self.i2c_bus.transfer(out, 13)
        hw = unpack_bytes(inp[6:8], big_endian=False)
        major = inp[8]
        minor = inp[9]
        build = unpack_bytes(inp[10:12], big_endian=False)
        fw_type = inp[12]
        fw = '{}.{}.{}-{}'.format(major, minor, build, chr(fw_type))
        return hw, fw

    def get_resolution(self):
        """
        Return the width and height of the camera.

        :return: width, height (0-511)
        """
        out = [
            # 2 sync bytes, type packet, length payload, unused type
            174, 193, 12, 1, 0
        ]
        logger.debug('get resolution from pixy2')
        inp = self.i2c_bus.transfer(out, 10)
        width, height = struct.unpack('<HH', bytes(inp[6:10]))

        return width, height

    def set_camera_brightness(self, brightness):
        """
        Set camera brightness.

        :param brightness: A value between 0-255 that represents the brightness.
        :return: Nothing.
        """
        out = [
            # 2 sync bytes, type packet, length payload, brightness
            174, 193, 16, 1, brightness
        ]
        logger.debug('set pixy2 camera brightness to ' + str(brightness))
        self.i2c_bus.transfer(out, 10)

    def set_servos(self, s0, s1):
        """
        Set the servo pan/tilt on the Pixy2.

        :param s0: Servo pan between 0-511.
        :param s1: Servo tilt between 0-511.
        :return: Nothing.
        """
        out = [
            # 2 sync bytes, type packet, length payload
            174, 193, 18, 4
        ]
        # add s0 servo pan and s1 servo tilt
        out += list(struct.pack('<HH', s0, s1))
        logger.debug('set pixy2 s0={} and s1={} servo pan/tilt'.format(s0, s1))
        self.i2c_bus.transfer(out, 10)

    def set_led(self, red, green, blue):
        """
        Set the Pixy2's RGB LED.

        :param red: 0-255.
        :param green: 0-255.
        :param blue: 0-255.
        :return: Nothing
        """
        out = [
            174, 193, 20, 3, red, green, blue
        ]
        logger.debug('set pixy2 LED to RGB=({}, {}, {})'.format(red, green, blue))
        self.i2c_bus.transfer(out, 10)

    def set_lamp(self, on):
        """
        Turn on or off the Pixy2's lamp.

        :param on: True or False on whether the Pixy2's lamps is on or off.
        :return: Nothing.
        """
        out = [
            # 2 sync bytes, set lamp mode, data size,
            # upper to white LEDs, all channels of lower RGB LED
            174, 193, 22, 2, 1 if on == 1 else 0, 0
        ]
        on_str = 'on' if on == 1 else 'off'
        logger.debug('set pixy2 lamp ' + on_str)
        self.i2c_bus.transfer(out, 10)

    def get_fps(self):
        """
        Get the Pixy2's camera FPS.

        :return: The FPS as an integer.
        """
        out = [
            # 2 sync bytes, type packet, length payload
            174, 193, 24, 0
        ]
        logger.debug('get fps from pixy2')
        inp = self.i2c_bus.transfer(out, 10)
        fps = struct.unpack('<I', bytes(inp[6:10]))[0]

        return fps

    def get_blocks(self, sigmap, maxblocks):
        """
        Get detected blocks from the Pixy2.

        :param sigmap: Indicates which signatures to receive data from.
        0 for none, 255 for all, all the rest it's in between.
        :param maxblocks: Maximum blocks to return.
        0 for none, 255 for all of them, all the rest it's in between.
        :return: signature, X center of block (px) (0-315), Y center of block (px) (0-207), width
        of block (px) (0-316), height of block (px) (0-208), angle of color-code in degrees (-180 - 180)
        w/ 0 if not a color code, tracking index (0-255), age or the number of frames this
        block has been tracked for (0-255) - it stops incrementing at 255.
        :return: None if it hasn't detected any blocks.
        """
        out = [
            # 2 sync bytes, type packet, length payload,
            # sigmap, max blocks to return
            174, 193, 32, 2, sigmap, maxblocks
        ]
        inp = self.i2c_bus.transfer(out, 20)
        data = struct.unpack('<7H2B', bytes(inp[4:20]))

        check_sum = data[0]
        incoming = data[1:]
        if check_sum != sum(incoming):
            logger.debug('no block detected from pixy2 w/ sigmap={}, maxblocks={}'.format(sigmap, maxblocks))
            return None
        else:
            logger.debug('detected block from pixy2 w/ sigmap={}, maxblocks={}'.format(sigmap, maxblocks))
            return data[1:]

    def get_main_features(self, features):
        """
        
        :param features:
        :return:
        """
        # 2 sync bytes, type packet, length payload, request type, features
        out = [
            174, 193, 48, 2, features, 7
        ]
        logger.debug('detect main features on the pixy2')
        inp = self.i2c_bus.transfer(out, 4)
        payload_length = inp[3]
        inp = self.i2c_bus.read_list(reg=None, len=payload_length)

        # if we have detected something
        if payload_length > 2:
            check_sum = struct.unpack('<H', bytes(inp[:2]))[0]
        # otherwise just cancel the process
        else:
            logger.debug('no features detected on the pixy2')
            return None

        # if the checksum doesn't match
        if check_sum != sum(inp[2:]):
            logger.debug('checksum doesn\'t match for the main features')
            return None
        inp = inp[2:]

        # read the actual features (vectors, intersections, barcodes)
        length = len(inp)
        current = 0
        data_dict = {}
        # labels = {
        #     1: 'vector',
        #     2: 'intersection',
        #     4: 'barcode'
        # }
        labels = iter(['vector', 'intersection', 'barcode'])
        while current < length:
            ftype, flength = struct.unpack('<2B', bytes(inp[:2]))
            inp = inp[2:]
            print('type={}, fl={} list={} current={} length={}'.format(ftype, flength, len(inp[:flength]), current, length))
            data = struct.unpack('<' + str(flength) + 'B', bytes(inp[:flength]))

            # add the data to the output dictionary
            label = next(labels)
            data_dict[label] = data

            # and update the number of bytes read
            current += 2 + flength

        return data_dict

    def set_mode(self, mode):
        """
        :param mode: LINE_MODE_TURN_DELAYED or
        LINE_MODE_MANUAL_SELECT_VECTOR or LINE_MODE_WHITE_LINE.
        :return: Nothing.
        """
        out = [
            # 2 sync bytes
            174, 193, 54, 1, mode
        ]
        logger.debug('set pixy2 mode to 0x{:02X}'.format(mode))
        self.i2c_bus.transfer(out, 10)

    def set_next_turn(self, angle):
        pass

    def set_default_turn(self, angle):
        pass

    def set_vector(self, angle):
        pass

    def reverse_vector(self, angle):
        pass

    def get_rgb(self, x, y, r, g, b, saturate):
        pass
