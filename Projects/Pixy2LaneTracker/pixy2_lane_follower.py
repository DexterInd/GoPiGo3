import signal
import pixy2
import cv2
import numpy as np
import math

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
    # a = (0, height - 1)
    # b = (25, 30)
    # c = (53, 30)
    # d = (width - 1, height - 1)
    a = (-26, height - 1)
    b = (23, 26)
    c = (58, 26)
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

    while not event_stopper.is_set():

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

        warped = np.zeros([win_size, win_size], dtype=np.uint8)
        for lane in lanes:
            a = tuple(lane[0,:])
            b = tuple(lane[1,:])
            cv2.line(warped, a, b, color=255, thickness=1)

        cv2.imshow('Pixy2 Stream - Lane Follower', img)
        cv2.imshow('Warped Image of the Lanes', warped)
        cv2.waitKey(int(1000 / fps))

    cv2.destroyAllWindows()

def runner(event_stopper):

    queue = MQueue(5)
    video_process = Process(target=video_worker, args=(queue, event_stopper))
    video_process.start()

    try:

        # initialize devices
        pixy = pixy2.Pixy2I2C(address=0x54)
        gopigo3 = EasyGoPiGo3()

        # turn on the built-in LED for better visibility
        pixy.set_lamp(1)

        # set it to follow white lanes
        pixy.set_mode(pixy2.LINE_MODE_WHITE_LINE)

        # get the number of frames per second
        fps = pixy.get_fps()
        period = 1 / fps

        # camera resolution
        width, height = pixy.get_resolution()
        print(width, height)

        # keep previous measurements for smoothing out the data
        previous_angle = 0
        previous_magnitude = 0
        previous_ema_angle = 0
        previous_ema_magnitude = 0
        frame_index = 0
        alfa = 0.10 # 0.2
        yotta = 0.2 # magnitude importance

        # Kp = 1.75
        # Ki = 0.0016
        # Kd = 9.0
        #
        # Kp_surrogate = 12.0
        # Ki_surrogate = 0.004
        # Kd_surrogate = 2.0

        c1 = PID(Kp=1.75, Ki=0.0016, Kd=9.0, previous_error=0.0, integral_area=0.0)
        c2 = PID(Kp=12.0, Ki=0.0040, Kd=2.0, previous_error=0.0, integral_area=0.0)
        pid_switch_point = 63

        set_point = 0
        max_motor_speed = 350
        # previous_error = 0
        # integral_area = 0
        # integral_area_surrogate = 0

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

            lanes, win_size, roi = detect_lanes_from_vector_frame(frame, height, width)
            angle, magnitude = calculate_direction_and_magnitude(lanes, win_size, previous_angle, previous_magnitude)

            ema_angle = exponential_moving_average(angle, previous_ema_angle, alfa)
            ema_magnitude = exponential_moving_average(magnitude, previous_ema_magnitude, alfa)

            # save the measurements for the next iteration
            previous_angle = angle
            previous_magnitude = magnitude
            previous_ema_angle = ema_angle
            previous_ema_magnitude = ema_magnitude

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
            # integral_area += error
            # integral_area_surrogate += error
            # if magnitude >= 63:
            #     integral_area = 0.0
            #     correction = Kp_surrogate * error + Ki_surrogate * integral_area_surrogate + Kd_surrogate * (error - previous_error)
            # else:
            #     integral_area_surrogate = 0.0
            #     correction = Kp * error + Ki * integral_area + Kd * (error - previous_error)
            # previous_error = error
            c1.integral_area += error
            c2.integral_area += error
            if magnitude < pid_switch_point:
                c = c1
                c2.integral_area = 0.0
            else:
                c = c2
                c1.integral_area = 0.0
            correction = c.Kp * error + c.Ki * c.integral_area + c.Kd * (error - c.previous_error)

            left_motor_speed = int(((1 - yotta) + yotta * magnitude / 100) * max_motor_speed + correction)
            right_motor_speed = int(((1 - yotta) + yotta * magnitude / 100) * max_motor_speed - correction)

            # print(magnitude, left_motor_speed, right_motor_speed, correction)

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

    except Exception:
        event_stopper.set()
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
    signal.signal(signal.SIGINT, lambda signum, frame: print("Press ESC to close the app."))
    main()