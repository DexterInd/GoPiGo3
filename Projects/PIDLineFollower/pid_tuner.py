from __future__ import print_function
from __future__ import division

from curtsies import Input
from easygopigo3 import EasyGoPiGo3
from easy_line_follower import EasyLineFollower
from threading import Thread, Event
import signal

from time import sleep, time

def drawLogo():
    print("   _____       _____ _  _____         ____  ")
    print("  / ____|     |  __ (_)/ ____|       |___ \ ")
    print(" | |  __  ___ | |__) || |  __  ___     __) |")
    print(" | | |_ |/ _ \|  ___/ | | |_ |/ _ \   |__ < ")
    print(" | |__| | (_) | |   | | |__| | (_) |  ___) |")
    print("  \_____|\___/|_|   |_|\_____|\___/  |____/ ")
    print("                                            ")

def drawDescription():
    print("\nPress the following keys to run the features of the GoPiGo3/LineFollower.")
    print("Press on the appropriate keys to tune the PID parameters for the line follower.\n")

def drawMenu():
    """
    Prints all the key-bindings between the keys and the GoPiGo3/LineFollower's commands on the screen.
    """
    keybindings = {
        "<ESC>" : "Exit",
        "x" : "Move the GoPiGo3 forward",
        "<SPACE>" : "Stop the GoPiGo3 from moving",
        "u" : "Increase the Kp parameter",
        "j" : "Increase the Ki parameter",
        "n" : "Increase the Kd parameter",
        "i" : "Decrease the Kp parameter",
        "k" : "Decrease the Ki parameter",
        "m" : "Decrease the Kd parameter",
        "w" : "Calibrate the line follower on a white surface",
        "b" : "Calibrate the line follower on a black surface"
    }

    order_of_keys = ["<ESC>", "x", "<SPACE>", "u", "j", "n", "i", "k", "m", "w", "b"]
    try:
        for key in order_of_keys:
            print("\r[key {:8}] :  {}".format(key, keybindings[key]))
    except KeyError:
        print("Error: Keys found in order_of_keys don't match with those in keybindings.")

stopper = Event()

gpg = EasyGoPiGo3()
lf = EasyLineFollower()

stepSize = 0.1
loopFreq = 30.0
setPoint = 0.5
motorSpeed = 300
leftMotorSpeed = 0
rightMotorSpeed = 0
Kp = 0.0
Ki = 0.0
Kd = 0.0

integralArea = 0.0

def controller():
    global stopper, gpg, lf, stepSize, loopFreq, setPoint, leftMotorSpeed, rightMotorSpeed, motorSpeed, Kp, Ki, Kd
    global integralArea
    loopPeriod = 1 / loopFreq
    
    integralArea = 0.0
    previousError = 0.0

    while not stopper.is_set():
        start = time()

        # <0.5 when line is on the right
        # >0.5 when line is on the left
        current = lf.read('weighted-avg')

        # calculate correction
        error = current - setPoint
        if Ki < 0.0001 and Ki > -0.0001:
            integralArea = 0.0
        else:
            integralArea += error
        correction = Kp * error + Ki * integralArea + Kd * (error - previousError) 
        # print(Kp * error, Ki * integralArea, Kd * (error - previousError))
        previousError = error

        # calculate motor speedss
        leftMotorSpeed = int(motorSpeed - correction)
        rightMotorSpeed = int(motorSpeed + correction)
        if leftMotorSpeed <= 0: leftMotorSpeed = 1
        if leftMotorSpeed >= 300: leftMotorSpeed = 299
        if rightMotorSpeed <= 0: rightMotorSpeed = 1
        if rightMotorSpeed >= 300: rightMotorSpeed = 299

        # update motor speeds
        gpg.set_motor_limits(gpg.MOTOR_LEFT, dps=leftMotorSpeed)
        gpg.set_motor_limits(gpg.MOTOR_RIGHT, dps=rightMotorSpeed)

        # make the loop work at a given frequency
        end = time()
        delayDiff = end - start
        if loopPeriod - delayDiff > 0:
            sleep(loopPeriod - delayDiff)

def Main():

    drawLogo()
    drawDescription()
    drawMenu()

    refresh_rate = 20.0

    controlThread = Thread(target = controller)
    controlThread.start()

    global stopper, gpg, lf, stepSize, motorSpeed, leftMotorSpeed, rightMotorSpeed, Kp, Ki, Kd
    global integralArea
    with Input(keynames = "curtsies", sigint_event = True) as input_generator:
        while True:
            period = 1 / refresh_rate
            # if nothing is captured in [period] seconds
            # then send() function returns None
            key = input_generator.send(period)

            if key == "<ESC>":
                # exit
                stopper.set()
                break
            if key == "x":
                gpg.set_speed(motorSpeed)
                gpg.forward()
            if key == "<SPACE>":
                gpg.stop()
            if key == "u":
                Kp += 2.0
            if key == "j":
                Ki += 0.001
            if key == "n":
                Kd += 100.0
            if key == "i":
                Kp -= 2.0
            if key == "k":
                Ki -= 0.001
            if key == "m":
                Kd -= 100.0
            if key == "w":
                lf.set_calibration('white')
            if key == "b":
                lf.set_calibration('black')

            if key is not None:
                print('Kp={:3f} Ki={:3f} Kd={:3f} L={:3d} R={:3d} ErrorArea={:3f}'.format(Kp, Ki, Kd, leftMotorSpeed, rightMotorSpeed, integralArea))
    
    controlThread.join()

if __name__ == "__main__":
    signal.signal(signal.SIGTSTP, lambda signum, frame: print("Press the appropriate key for closing the app."))

    try:
        Main()
    except IOError as error:
        print(str(error))
        exit(1)

    exit(0)