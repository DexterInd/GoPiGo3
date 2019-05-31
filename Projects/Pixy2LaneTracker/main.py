import logging
import pixy2
import json
from time import sleep

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    device = pixy2.Pixy2I2C(address=0x54)

    # set a mode
    device.set_mode(pixy2.LINE_MODE_WHITE_LINE)

    # get version from pixy2
    hw, sw = device.get_version()
    string = 'hw {} sw {}'.format(hw, sw)
    logger.info(string)

    # get resolution from pixy2
    resolution = device.get_resolution()
    string = 'width {} height {}'.format(*resolution)
    logger.info(string)

    # # set brightness for pixy2
    # for brightness in range(0, 150, 30):
    #     device.set_camera_brightness(brightness)
    #     sleep(0.5)

    # set servos pans
    for pan in range(0, 512, 128):
        tilt = pan
        device.set_servos(pan, tilt)
        sleep(0.3)

    # set the RGB LED
    for color_channel in range(0, 256 + 1, 64):
        r = g = b = color_channel
        device.set_led(r, g, b)
        sleep(0.1)

    # turn the lamp on an off
    counter = 0
    for i in range(11):
        device.set_lamp(counter % 2)
        counter += 1
        sleep(0.05)

    # get FPS
    fps = device.get_fps()
    logger.info('pixy2\'s camera FPS is {}'.format(fps))

    # get blocks
    retries = 10
    counter = 0
    while True:
        block = device.get_blocks(sigmap=255, maxblocks=255)
        sleep(0.1)
        counter += 1
        if block is not None:
            break
        if counter == retries:
            break
    if counter != retries:
        string = 'sign={} XC={} YC={} W={} H={} Angle={} Idx={} Age={}'.format(*block)
        logger.info(string)

    # get main features
    while True:
        features = device.get_main_features(features=1)
        if features is not None:
            break

    formatted = json.dumps(features, indent=2, sort_keys=True)
    logger.info(formatted)

