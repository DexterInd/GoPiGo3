import signal
import pixy2
import logging

from easygopigo3 import EasyGoPiGo3
from threading import Thread, Event
from recordclass import recordclass
from collections import namedtuple
from time import sleep, time
from getkey import getkey, keys
from scipy import interpolate

PixyBlock = namedtuple('PixyBlock', 'signature x_center y_center width height angle track_index age')
PID = recordclass('PID', 'Kp Ki Kd previous_error integral_area')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_signature_blocks(pixy, sigmap):
    data = pixy.get_blocks(sigmap=sigmap, maxblocks=255)
    blocks = None
    if data:
        blocks = [PixyBlock(*obj) for obj in data]
    return blocks

def exponential_moving_average(in_data_point, previous_y_sum, alfa):

    new_y_sum = alfa * in_data_point + (1 - alfa) * previous_y_sum
    return new_y_sum

def runner(event_stopper):
    try:
        pixy = pixy2.Pixy2I2C(address=0x54)
        gopigo3 = EasyGoPiGo3()
        
        target_signature = 1
        tracked_index = None
        
        # call it once and discard the data
        # this is meant to automatically switch to block detection
        get_signature_blocks(pixy, sigmap=target_signature)
        
        # pid controller & exponential moving average settings
        pid = PID(Kp=400.0, Ki=0.0, Kd=0.0, previous_error=0.0, integral_area=0.0)
        width, height = pixy.get_resolution()
        loop_frequency = 60
        period = 1 / loop_frequency
        alfa = 0.15 # 20%
        previous_ema_speed = 0.0
        after_how_many_cycles_to_stop = 30
        cycle = 0
        
        logger.info('set ' + str(pid))
        logger.info('exponential moving average alfa={}'.format(alfa))
        logger.info('stop motors after {} cycles of inactivity'.format(after_how_many_cycles_to_stop))
        logger.info('control loop running at {}Hz'.format(loop_frequency))
        
        # ratio-to-speed interpolation
        ratio_to_speed = interpolate.interp1d(x=[1, 30], y=[100, 350], fill_value=(0, 350), bounds_error=False)
        
        while not event_stopper.is_set():
            start = time()
            
            # get the detected blocks
            blocks = get_signature_blocks(pixy, sigmap=target_signature)
            
            # sleep if nothing is detected
            if not blocks:
                sleep(period)
                if cycle % after_how_many_cycles_to_stop == 0:
                    cycle = 1
                    gopigo3.stop()
                else:
                    cycle += 1
                continue
            # initialize the tracked_index if it's the case
            if not tracked_index:
                tracked_index = blocks[0].track_index
                logger.info('change tracked index to {}'.format(tracked_index))
            
            # select the best block based on our tracked index
            # if it ain't there, then pick a new one
            block = None
            for _block in blocks:
                if _block.track_index == tracked_index:
                    block = _block
            if not block:
                tracked_index = blocks[0].track_index
                block = blocks[0]
                logger.info('change tracked index to {}'.format(tracked_index))
            
            # gives us the error
            error = block.x_center / width - 0.5
            
            # calculate motor speeds based on how far away the object is
            block_to_image_ratio = height * width / (block.height * block.width)
            unaveraged_motor_speed = ratio_to_speed(block_to_image_ratio)
            base_motor_speed = exponential_moving_average(unaveraged_motor_speed, previous_ema_speed, alfa)
            previous_ema_speed = base_motor_speed
            
            # run the pid controller
            pid.integral_area += error
            correction = pid.Kp * error + pid.Ki * pid.integral_area + pid.Kd * pid.previous_error
            pid.previous_error = error
            
            # calculate motor speeds based on pid's correction
            left_motor_speed = int(base_motor_speed + correction)
            right_motor_speed = int(base_motor_speed - correction)
            logger.debug('motor speed left={} right={}'.format(left_motor_speed, right_motor_speed))
            
            # actuate the motors
            gopigo3.set_motor_dps(gopigo3.MOTOR_LEFT, dps=left_motor_speed)
            gopigo3.set_motor_dps(gopigo3.MOTOR_RIGHT, dps=right_motor_speed)
            
            end = time()
            remaining_time = period - (end - start)
            if remaining_time > 0:
                sleep(remaining_time)
            
        gopigo3.stop()
    
    except Exception:
        event_stopper.set()

def main():
    logger.debug('start runner thread')
    event_stopper = Event()
    runner_thread = Thread(target=runner, args=(event_stopper,))
    runner_thread.start()
    
    # wait to get the exit key
    while getkey() != keys.ESC and not event_stopper.is_set():
        continue
          
    # and then stop the thread
    event_stopper.set()
    
    logger.debug('stop runner thread')  

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda signum, frame: print("Press ESC to close the app."))
    main()