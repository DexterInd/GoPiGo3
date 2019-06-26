import signal
import pixy2
import cv2
import numpy as np
import math
import logging
import json

from easygopigo3 import EasyGoPiGo3
from threading import Thread
from multiprocessing import Queue as MQueue, Process, Event as MEvent
from time import sleep, time
from getkey import getkey, keys
from recordclass import recordclass

PID = recordclass('PID', 'Kp Ki Kd previous_error integral_area')

def get_angle_against_oy(v):
    x1, y1 = v[0:2]
    x2, y2 = v[2:4]
    dx = x2 - x1
    dy = y2 - y1

    radians = math.atan2(dy, dx)
    degrees = math.degrees(radians) + 90

    return degrees


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def calc_direction_from_lanes(lanes):
    v = np.sum(lanes, axis=0) / len(lanes)
    angle = get_angle_against_oy(v.flatten())
    magnitude = int(distance(v[0, :], v[1, :]))

    return angle, magnitude


def window_based_interpolation(magnitude, height, width):
    longest_line = math.sqrt(height ** 2 + width ** 2)
    percent_magnitude = int(100 * magnitude / longest_line)

    return percent_magnitude


def detect_lanes_from_vector_frame(frame, height, width):
    # region of interest
    a = (-26, height - 1)
    b = (17, 26) # 23
    c = (64, 26) # 58
    d = (width - 1 + 26, height - 1)
    roi = [a, b, c, d]
    pts1 = np.float32(roi)
    win_size = height = width = 500
    pts2 = np.float32([[0, height - 1], [0, 0], [width - 1, 0], [width - 1, height - 1]])

    # get perspective and warp the image
    transform = cv2.getPerspectiveTransform(pts1, pts2)

    # warped vectors
    warped_vectors = []

    for vector in frame:
        # check this to understand why the reshape has to be called
        # https://stackoverflow.com/a/46048098/2096747
        line = np.array([[vector.x0, vector.y0], [vector.x1, vector.y1]], dtype=np.float32)
        line = line.reshape(2, 1, -1)
        warped = cv2.perspectiveTransform(src=line, m=transform)
        warped = np.array(warped.reshape(2, 2), dtype=np.int32)
        warped_vectors.append(warped)

    # for vectors that are also placed outside the roi, just crop them
    filtered_vectors = []
    for vector in warped_vectors:
        x_col = vector[:, 0]
        y_col = vector[:, 1]
        if np.any((x_col >= 0) & (x_col < win_size)):
            if np.any((y_col >= 0) & (y_col < win_size)):
                y_col[y_col < 0] = 0
                y_col[y_col >= win_size] = win_size - 1
                x_col[x_col < 0] = 0
                x_col[x_col >= win_size] = win_size - 1
                filtered_vectors.append(vector)

    # remove vectors that only reside in the lower half horizontal plane of the roi
    thresholded_vectors = []
    for vector in filtered_vectors:
        y_col = vector[:, 1]
        if np.any(y_col >= (win_size // 2)):
            thresholded_vectors.append(vector)

    return thresholded_vectors, win_size, roi


def calculate_direction_and_magnitude(lanes, win_size, previous_angle, previous_magnitude):

    if len(lanes) > 0:
        angle, magnitude = calc_direction_from_lanes(lanes)
        magnitude = window_based_interpolation(magnitude, win_size, win_size)

        if angle is None:
            angle = previous_angle
        if angle < -90:
            angle = -90
        elif angle >= 90:
            angle = 90

        return angle, magnitude

    else:
        return previous_angle, previous_magnitude


def exponential_moving_average(in_data_point, previous_y_sum, alfa):

    new_y_sum = alfa * in_data_point + (1 - alfa) * previous_y_sum
    return new_y_sum

def video_worker(queue, event_stopper):

    scale = 5
    font = cv2.FONT_HERSHEY_SIMPLEX

    # while the event hasn't been set
    while not event_stopper.is_set():
        
        # get the data off of the queue
        if not queue.empty():
            data = queue.get()
        else:
            sleep(0.001)
            continue

        frame_index = data['frame_idx']
        frame = data['frame']
        height, width = data['resolution']
        fps = data['fps']
        angle = data['angle']
        magnitude = data['magnitude']
        lanes = data['lanes']
        win_size = data['win_size']

        nh = scale * height
        nw = scale * width

        # draw the vectors on the first image
        img = np.zeros([nh, nw], dtype=np.uint8)
        for vector in frame:
            cv2.line(img,
                     (vector.x0 * scale, vector.y0 * scale),
                     (vector.x1 * scale, vector.y1 * scale),
                     color=255, thickness=1)
            cv2.putText(img, 'Frame {}'.format(frame_index),
                        (int(0.1 * nh), int(0.1 * nw)), font, 0.5, 255, 1, cv2.LINE_AA)
            cv2.putText(img, 'FPS {}'.format(int(fps)),
                        (int(0.1 * nh), int(0.15 * nw)), font, 0.5, 255, 1, cv2.LINE_AA)
            cv2.putText(img, 'Angle {}'.format(int(angle)),
                        (int(1.0 * nh), int(0.1 * nw)), font, 0.5, 255, 1, cv2.LINE_AA)
            cv2.putText(img, 'Mag {}'.format(int(magnitude)),
                        (int(1.0 * nh), int(0.15 * nw)), font, 0.5, 255, 1, cv2.LINE_AA)

        # generated the warped image as seen from the bird's eye perspective
        warped = np.zeros([win_size, win_size], dtype=np.uint8)
        for lane in lanes:
            a = tuple(lane[0,:])
            b = tuple(lane[1,:])
            cv2.line(warped, a, b, color=255, thickness=1)

        # show them
        cv2.imshow('Pixy2 Stream - Lane Follower', img)
        cv2.imshow('Warped Image of the Lanes', warped)

        # and add a mandatory waiKey call
        cv2.waitKey(int(1000 / fps))

    # close all windows (2 of them)
    cv2.destroyAllWindows()

def runner(event_stopper):

    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as err:
        logger.exception(err)
        event_stopper.set()
        return

    # start another process to render the graphical representation
    # of what the camera sees
    queue = MQueue(5)
    video_process = Process(target=video_worker, args=(queue, event_stopper))
    video_process.start()

    try:

        # initialize devices
        pixy = pixy2.Pixy2I2C(address=0x54)
        gopigo3 = EasyGoPiGo3()
        logger.info('initialized pixy2 and gopigo3')

        # turn on the built-in LED for better visibility
        pixy.set_lamp(1)
        logger.info('turn on pixy2 lamp')

        # set it to follow white lanes
        pixy.set_mode(pixy2.LINE_MODE_WHITE_LINE)
        logger.info('set pixy2 line mode on white')

        # get the number of frames per second
        fps = pixy.get_fps()
        period = 1 / fps
        logger.info('pixy2 running at {} fps'.format(fps))

        # camera resolution
        width, height = pixy.get_resolution()
        logger.info('pixy2 camera width={} height={}'.format(width, height))

        # keep previous measurements for smoothing out the data
        previous_angle = 0
        previous_magnitude = 0
        previous_ema_angle = 0
        previous_ema_magnitude = 0
        frame_index = 0
        alfa = config['alfa']
        yotta = config['yotta'] # magnitude importance
        logger.info('alfa (exp. moving average factor) = {:3.2f}'.format(alfa))
        logger.info('yotta (magnitude importance) = {:3.2f}'.format(yotta))

        # the 2 PIDs
        c1 = PID(Kp=config['pid1']['Kp'], Ki=config['pid1']['Ki'], Kd=config['pid1']['Kd'], previous_error=0.0, integral_area=0.0)
        c2 = PID(Kp=config['pid2']['Kp'], Ki=config['pid2']['Ki'], Kd=config['pid2']['Kd'], previous_error=0.0, integral_area=0.0)
        pid_switch_point = config['pid-switch-point']
        logger.info('PID 1 = {}'.format(str(c1)))
        logger.info('PID 2 = {}'.format(str(c2)))
        logger.info('PID switchpoint = {}'.format(pid_switch_point))
        
        set_point = 0
        max_motor_speed = config['max-motor-speed']
        logger.info('max motor speed = {}'.format(max_motor_speed))

        while not event_stopper.is_set():

            # track each step's time
            start = time()

            # get the main features from the pixy2
            features = pixy.get_main_features(features=1)
            frame = None
            if features:
                if 'vectors' in features:
                    frame = features['vectors']
                else:
                    frame = []
                frame_index += 1
            else:
                gopigo3.stop()
                sleep(period)
                continue

            # calculate the heading of the lane and detect how long the lane is
            lanes, win_size, roi = detect_lanes_from_vector_frame(frame, height, width)
            angle, magnitude = calculate_direction_and_magnitude(lanes, win_size, previous_angle, previous_magnitude)

            # run the determined heading and magnitude through an exponential moving average function
            # this has the effect of smoothing the results and of ignoring the short term noise
            ema_angle = exponential_moving_average(angle, previous_ema_angle, alfa)
            ema_magnitude = exponential_moving_average(magnitude, previous_ema_magnitude, alfa)

            # save the measurements for the next iteration
            previous_angle = angle
            previous_magnitude = magnitude
            previous_ema_angle = ema_angle
            previous_ema_magnitude = ema_magnitude

            angle = ema_angle
            magnitude = ema_magnitude
            
            # push the processed information to the graphical renderer (on a separate process)
            if not queue.full():
                queue.put({
                    'frame_idx': frame_index,
                    'frame': frame,
                    'resolution': (height, width),
                    'fps': fps,
                    'angle': angle,
                    'magnitude': magnitude,
                    'lanes': lanes,
                    'win_size': win_size
                })

            # run the pid controller
            error = angle - set_point
            c1.integral_area += error
            c2.integral_area += error
            pid1 = True
            if magnitude < pid_switch_point:
                c = c1
                c2.integral_area = 0.0
            else:
                c = c2
                c1.integral_area = 0.0
                pid1 = False
            
            # calculate the correction
            correction = c.Kp * error + c.Ki * c.integral_area + c.Kd * (error - c.previous_error)
            c1.previous_error = error
            c2.previous_error = error

            # determine motor speeds
            left_motor_speed = int(((1 - yotta) + yotta * magnitude / 100) * max_motor_speed + correction)
            right_motor_speed = int(((1 - yotta) + yotta * magnitude / 100) * max_motor_speed - correction)

            logger.debug('using PID {} | angle: {:3d} magnitude: {:3d} | left speed: {:3d} right speed: {:3d}'.format(
                1 if pid1 else 0,
                int(angle),
                int(magnitude),
                left_motor_speed,
                right_motor_speed
            ))

            # actuate the motors
            gopigo3.set_motor_dps(gopigo3.MOTOR_LEFT, dps=left_motor_speed)
            gopigo3.set_motor_dps(gopigo3.MOTOR_RIGHT, dps=right_motor_speed)

            # make it run at a specific loop frequency
            # equal to camera's fps
            end = time()
            diff = end - start
            remaining_time = period - diff
            if remaining_time > 0:
                sleep(remaining_time)

        # and turn the built-in LED off when the program ends
        # and stop the gopigo3
        pixy.set_lamp(0)
        gopigo3.stop()

    except Exception as e:
        event_stopper.set()
        logger.exception(e)
    finally:
        video_process.join()

def main():

    event_stopper = MEvent()
    runner_thread = Thread(target=runner, args=(event_stopper,))
    runner_thread.start()

    # wait to get the exit key
    while getkey() != keys.ESC and not event_stopper.is_set():
        continue

    # and then stop the thread
    event_stopper.set()

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    signal.signal(signal.SIGINT, lambda signum, frame: print("Press ESC to close the app."))
    main()