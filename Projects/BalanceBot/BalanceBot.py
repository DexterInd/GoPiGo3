#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo3/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information, see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for a balancing robot using the GoPiGo3.
# 
# Hardware:
#     * Connect a Dexter Industries IMU sensor to GoPiGo3 AD1 port.  
#     Gyro should be placed on the right hand side of the GoPiGo3, next to the por Servo 1, with the Arrow pointing forward.
#     * Connect a grove IR receiver to GoPiGo3 AD2 port.
#     IR Receiver should be placed across from the IMU.
#     * Sensor Mounts: Connect the IR Receiver and the IMU sensor using the Dexter Industries Sensor Mounts.
#     * IR Remote Control:  Control the robot using the Dexter Industries IR Remote Control
# 
# Results:  When you run this program, follow the instruction printed in the terminal.
# Note: This project is best run on a carpeted surface!

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import gopigo3  # import the GoPiGo3 drivers
import sys      # import sys for sys.exit()
from di_sensors import inertial_measurement_unit # import the IMU drivers

# Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
GPG = gopigo3.GoPiGo3()

# Clear previous configurations
GPG.reset_all()

# define which I2C bus the IMU is connected to.
imu = inertial_measurement_unit.InertialMeasurementUnit(bus = "GPG3_AD1")

# define which port the IR receiver is connected to.
PORT_SENSOR_IR = GPG.GROVE_2

# how fast to drive when being controlled by the remote (degrees per second)
DRIVE_SPEED = 175

# how fast to steer when being controlled by the remote (degrees per second)
STEER_SPEED = 100

# constants used to define how agressively the robot should respond to:
KGYROANGLE = 15    # overall angle
KGYROSPEED = 1.7   # sudden changes in angle
KPOS       = 0.07  # deviation from the target position
KSPEED     = 0.1   # the actual speed of the motor
KDRIVE     = -0.02 # the drive speed target (helps the robot start/stop driving)
KSTEER     = 0.25  # an error in the steering of the robot
KVOLTAGE   = 0.083 # voltage changes. configured for 12v, this constant helps the robot adapt to batteries with falling voltage.

# How fast to run the balance loop in Hz. Slower is less CPU intensive, but faster helps the balance bot to work better.
# Anything over about 100 won't make any difference since the IMU gyro sensor won't update any faster, and since it takes some time for the motors to physically respond.
LOOP_SPEED = 100

TIME_FALL_LIMIT = 2 # if the motors have been running at full power for 2 seconds, assume that the robot fell.

# a constant used to correct the delay to try to maintain a perfect loop speed (defined by LOOP_SPEED)
KCORRECTTIME = 0.001

# a constant used to correct/center the gyro accumulated angle so that gyro integral drift works itself out faster than it can accumulate.
KGYROANGLECORRECT = 0.1

WHEEL_DIAMETER = GPG.WHEEL_DIAMETER # wheel diameter in mm.

WHEEL_RATIO = (WHEEL_DIAMETER / 56) # tuned for 56mm wheels
LOOP_TIME = (1 / LOOP_SPEED)        # how many seconds each loop should take (at 100 Hz, this should be 0.01)

# call this function to turn off the motors and exit safely.
def SafeExit():
    GPG.reset_all()  # Unconfigure the sensors, disable the motors, and restore the LEDs to default.
    sys.exit()       # Exit the python program

def ReadyForBalance():
    # float the motors
    GPG.set_motor_power(GPG.MOTOR_LEFT + GPG.MOTOR_RIGHT, GPG.MOTOR_FLOAT)
    
    # create/access global variables
    global gyroAngle
    global mrcSum
    global motorPos
    global mrcDelta
    global mrcDeltaP1
    global mrcDeltaP2
    global mrcDeltaP3
    global motorDiffTarget
    global TimeOffset
    global tInterval
    global LastTime
    
    # wait for the 'OK' button to be pressed
    print("Stand robot up and then press 'OK' on the remote.")
    while GPG.get_grove_value(PORT_SENSOR_IR) != 3:
        time.sleep(0.1)
    
    # reset the encoders
    GPG.offset_motor_encoder(GPG.MOTOR_LEFT, GPG.get_motor_encoder(GPG.MOTOR_LEFT))
    GPG.offset_motor_encoder(GPG.MOTOR_RIGHT, GPG.get_motor_encoder(GPG.MOTOR_RIGHT))
    
    # set variables to 0
    gyroAngle = 0
    mrcSum = 0
    motorPos = 0
    mrcDelta = 0
    mrcDeltaP1 = 0
    mrcDeltaP2 = 0
    mrcDeltaP3 = 0
    motorDiffTarget = 0
    TimeOffset = 0
    tInterval = LOOP_TIME
    LastTime = time.time() - LOOP_TIME
    
    print("Balancing, so let go of the robot.")
    print("Use Up, Down, Left, and Right on the remote to drive the robot.")

try:
    print("GoPiGo3 BalanceBot.")
    
    # make sure voltage is high enough
    if GPG.get_voltage_battery() < 9:
        print("Battery voltage below 9v; too low to run reliably. Exiting.")
        SafeExit()
    
    # configure the IR remote
    GPG.set_grove_type(PORT_SENSOR_IR, GPG.GROVE_TYPE.IR_DI_REMOTE)
    
    ReadyForBalance()
    
    while True:
        try:
            # loop at exactly the speed specified by LOOP_SPEED, and set tInterval to the actual loop time
            CurrentTime = time.time()
            TimeOffset += ((tInterval - LOOP_TIME) * KCORRECTTIME) # use this to adjust for any overheads, so that it tries to loop at exactly the speed specified by LOOP_SPEED
            DelayTime = (LOOP_TIME - (CurrentTime - LastTime)) - TimeOffset
            if DelayTime > 0:
                time.sleep(DelayTime)
            CurrentTime = time.time()
            tInterval = (CurrentTime - LastTime)
            LastTime = CurrentTime
            #print(tInterval, TimeOffset)
            
            # get the remote button being pressed
            Button = GPG.get_grove_value(PORT_SENSOR_IR)
            
            # if an arrow is being pressed, drive or steer accordingly
            if Button == 1:
                motorControlDrive = DRIVE_SPEED
                motorControlSteer = 0
            elif Button == 5:
                motorControlDrive = -DRIVE_SPEED
                motorControlSteer = 0
            elif Button == 2:
                motorControlDrive = 0
                motorControlSteer = -STEER_SPEED
            elif Button == 4:
                motorControlDrive = 0
                motorControlSteer = STEER_SPEED
            else:
                motorControlDrive = 0
                motorControlSteer = 0
            
            # get the gyro rotation rate in degrees per second
            # Gyro should be placed on the right hand side of the GoPiGo3, next to the por Servo 1, with the Arrow pointing forward.
            gyroSpeed = imu.read_gyroscope()[2] # specifically use the Z axis
            
            # This line, if uncommented, allows you to place the gyro on top of the GoPiGo3, arrow pointing upwards.
            # gyroSpeed = -imu.read_gyroscope()[0] # specifically use the X axis
            
            # integrate the gyro to get robot angle
            gyroAngle += gyroSpeed * tInterval
            
            # correct for gyro integration errors (slowly work towards center)
            gyroAngle -= (gyroAngle * KGYROANGLECORRECT * tInterval)
            
            # get the current motor encoder positions
            mrcLeft = GPG.get_motor_encoder(GPG.MOTOR_LEFT)
            mrcRight = GPG.get_motor_encoder(GPG.MOTOR_RIGHT)
            
            # calculate motor speed
            mrcSumPrev = mrcSum
            mrcSum = mrcLeft + mrcRight
            mrcDelta = mrcSum - mrcSumPrev
            motorSpeed = mrcDelta / tInterval
            
            # adjust motor position/target
            motorPos += (mrcDelta - (motorControlDrive * tInterval))
            
            # calculate the motor power
            power = (((KGYROSPEED * gyroSpeed +               # (Deg/Sec from Gyro sensor
                     KGYROANGLE * gyroAngle) / WHEEL_RATIO +  # Deg from integral of gyro) / wheel ratio
                     KPOS       * motorPos +                  # From MotorRotaionCount of both motors
                     KDRIVE     * motorControlDrive +         # To improve start/stop performance
                     KSPEED     * motorSpeed) /               # Motor speed in Deg/Sec
                     (KVOLTAGE * GPG.get_voltage_battery()))  # To maintain similar performance over a voltage range
            
            # if the power is not maxed out, record the time
            if abs(power) < 100:
                tMotorPosOK = CurrentTime
            
            # calculate the speed for left and right motor, taking into account the desired turn
            motorDiffTarget += motorControlSteer * tInterval
            motorDiff = mrcLeft - mrcRight
            powerSteer = KSTEER * (motorDiffTarget - motorDiff)
            powerLeft = power + powerSteer
            powerRight = power - powerSteer
            
            # clip the motor power to +-100
            if  powerLeft  >  100:
                powerLeft  =  100
            if  powerLeft  < -100:
                powerLeft  = -100
            if  powerRight >  100:
                powerRight =  100
            if  powerRight < -100:
                powerRight = -100
            
            # set the motor power
            GPG.set_motor_power(GPG.MOTOR_LEFT , powerLeft)
            GPG.set_motor_power(GPG.MOTOR_RIGHT, powerRight)
            
            # if the motors have been running at full power for at least TIME_FALL_LIMIT, assume the robot fell.
            if (CurrentTime - tMotorPosOK) > TIME_FALL_LIMIT:
                print("Robot fell.")
                ReadyForBalance()
            
        except gopigo3.SensorError as error:
            print(error)
        except IOError as error:
            print(error)
    
except KeyboardInterrupt:
    print("\nCtrl+C. Exiting.")
    SafeExit()

except:
    print("Exception. Exiting.")
    SafeExit()
