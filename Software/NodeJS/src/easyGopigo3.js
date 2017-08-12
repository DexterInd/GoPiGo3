// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//
// Node.js interface for the GoPiGo3

const sleep = require('sleep');

const FirmwareVersionError = require('./errors/firmwareVersionError');

const LightSensor = require('./components/lightSensor');
const SoundSensor = require('./components/soundSensor');
const UltrasonicSensor = require('./components/ultraSonicSensor');
const Buzzer = require('./components/buzzer');
const Led = require('./components/led');
const ButtonSensor = require('./components/buttonSensor');
const LineFollow = require('./components/lineFollower/lineFollow');
const LineThresholdSet = require('./components/lineFollower/lineThresholdSet');
const Servo = require('./components/servo');
const DHTSensor = require('./components/dhtSensor');
const DistanceSensor = require('./components/distanceSensor');

const Gopigo = require('./gopigo3');

class EasyGoPiGo3 extends Gopigo {
    gopigo;
    DEFAULT_SPEED = 300;

    constructor() {
        try {
            super();
        } catch (err) {
            if (err instanceof FirmwareVersionError) {
                console.log('FATAL ERROR:\nTo update the firmware on Raspbian for Robots you need to run DI Software Update and choose Update Robot');
            }
            throw new Error(err);
        }

        this.sensor1 = null;
        this.sensor2 = null;
        this.setSpeed(this.DEFAULT_SPEED);
        this.leftEyeColor = [0, 255, 255];
        this.rightEyeColor = [0, 255, 255];
    }

    volt() {
        return this.getVoltageBattery();
    }
    setSpeed(inSpeed) {
        this.speed = !isNaN(inSpeed) ? parseInt(inSpeed, 0) : this.DEFAULT_SPEED;
        this.setMotorLimits(
            this.MOTOR_LEFT + this.MOTOR_RIGHT,
            0,
            this.speed
        );
    }
    getSpeed() {
        return parseInt(this.speed, 0);
    }
    resetSpeed() {
        this.setSpeed(this.DEFAULT_SPEED);
    }
    /**
     * Stop the GoPiGo3 by setting the degrees per second speed
        of each motor to 0
     */
    stop() {
        this.setMotorDps(this.MOTOR_LEFT + this.MOTOR_RIGHT, 0);
    }
    backward() {
        this.setMotorDps(this.MOTOR_LEFT + this.MOTOR_RIGHT, this.getSpeed() * -1);
    }
    right() {
        this.setMotorDps(this.MOTOR_LEFT, this.getSpeed());
        this.setMotorDps(this.MOTOR_RIGHT, 0);
    }
    left() {
        this.setMotorDps(this.MOTOR_LEFT, 0);
        this.setMotorDps(this.MOTOR_RIGHT, this.getSpeed());
    }
    forward() {
        this.setMotorDps(this.MOTOR_LEFT + this.MOTOR_RIGHT, this.getSpeed());
    }
    driveCm(dist, blocking = true) {
        // dist is in cm
        // if dist is negative, this becomes a backward move
        const distMm = dist * 10;

        // the number of degrees each wheel needs to turn
        const wheelTurnDegrees = ((distMm / this.WHEEL_CIRCUMFERENCE) * 360);

        // get the starting position of each motor
        const startPositionLeft = this.getMotorEncoder(this.MOTOR_LEFT);
        const startPositionRight = this.getMotorEncoder(this.MOTOR_RIGHT);

        const destPositionLeft = startPositionLeft + wheelTurnDegrees;
        const destPositionRight = startPositionRight + wheelTurnDegrees;

        this.setMotorPosition(
            this.MOTOR_LEFT,
            destPositionLeft
        );
        this.setMotorPosition(
            this.MOTOR_RIGHT,
            destPositionRight
        );

        if (blocking) {
            while (!this.targetReached(
                destPositionLeft,
                destPositionRight
            )) {
                sleep.sleep(0.1);
            }
        }
    }
    driveInches(dist, blocking = true) {
        this.driveCm(dist * 2.54, blocking);
    }
    /**
     * these degrees are meant to be wheel rotations.
       360 degrees would be a full wheel rotation
       not the same as turn_degrees() which is a robot rotation
       degrees is in degrees, not radians
       if degrees is negative, this becomes a backward move
     *
     * @param {*} degrees
     * @param {*} blocking
     */
    driveDegrees(degrees, blocking = false) {
        // get the starting position of each motor
        const startPositionLeft = this.getMotorEncoder(this.MOTOR_LEFT);
        const startPositionRight = this.getMotorEncoder(this.MOTOR_RIGHT);

        const destPositionLeft = startPositionLeft + degrees;
        const destPositionRight = startPositionRight + degrees;

        this.setMotorPosition(
            this.MOTOR_LEFT,
            destPositionLeft
        );
        this.setMotorPosition(
            this.MOTOR_RIGHT,
            destPositionRight
        );

        if (blocking) {
            while (!this.targetReached(
                destPositionLeft,
                destPositionRight
            )) {
                sleep.sleep(0.1);
            }
        }
    }
    /**
     * check if both wheels have reached their target
     * @param {*} leftTargetDegrees
     * @param {*} rightTargetDegrees
     */
    targetReached(leftTargetDegrees, rightTargetDegrees) {
        const tolerance = 5;
        const minLefTarget = leftTargetDegrees - tolerance;
        const maxLeftTarget = leftTargetDegrees + tolerance;
        const minRightTarget = rightTargetDegrees - tolerance;
        const maxRighTarget = rightTargetDegrees + tolerance;

        const currentLeftPosition = this.getMotorEncoder(this.MOTOR_LEFT);
        const currentRightPosition = this.getMotorEncoder(this.MOTOR_RIGHT);

        if (
            currentLeftPosition > minLefTarget
            && currentLeftPosition < maxLeftTarget
            && currentRightPosition > minRightTarget
            && currentRightPosition < maxRighTarget
        ) {
            return true;
        }

        return false;
    }
    resetEncoders() {
        this.setMotorPower(this.MOTOR_LEFT + this.MOTOR_RIGHT, 0);
        this.offsetMotorEncoder(this.MOTOR_LEFT, this.getMotorEncoder(this.MOTOR_LEFT));
        this.offsetMotorEncoder(this.MOTOR_RIGHT, this.getMotorEncoder(this.MOTOR_RIGHT));
    }
    blinkerOn(id) {
        if (id === 1 || id === 'left') {
            this.setLed(this.LED_LEFT_BLINKER, 255);
        }
        if (id === 0 || id === 'right') {
            this.setLed(this.LED_RIGHT_BLINKER, 255);
        }
    }
    blinkerOff(id) {
        if (id === 1 || id === 'left') {
            this.setLed(this.LED_LEFT_BLINKER, 0);
        }
        if (id === 0 || id === 'right') {
            this.setLed(this.LED_RIGHT_BLINKER, 0);
        }
    }
    ledOn(id) {
        this.blinkerOn(id);
    }
    ledOff(id) {
        this.blinkerOff(id);
    }
    setLeftEyeColor(color) {
        if (color.length && color.length === 3) {
            this.leftEyeColor = color;
        } else {
            throw new Error('Eye color not valid');
        }
    }
    setRightEyeColor(color) {
        if (color.length && color.length === 3) {
            this.rightEyeColor = color;
        } else {
            throw new Error('Eye color not valid');
        }
    }
    setEyeColor(color) {
        this.setLeftEyeColor(color);
        this.setRightEyeColor(color);
    }
    openLeftEye() {
        this.setLed(
            this.LED_LEFT_EYE,
            this.leftEyeColor[0],
            this.leftEyeColor[1],
            this.leftEyeColor[2],
        );
    }
    openRightEye() {
        this.setLed(
            this.LED_RIGHT_EYE,
            this.rightEyeColor[0],
            this.rightEyeColor[1],
            this.rightEyeColor[2],
        );
    }
    openEyes() {
        this.openLeftEye();
        this.openRightEye();
    }
    closeLeftEye() {
        this.setLed(this.LED_LEFT_EYE, 0, 0, 0);
    }
    closeRightEye() {
        this.setLed(this.LED_RIGHT_EYE, 0, 0, 0);
    }
    closeEyes() {
        this.closeLeftEye();
        this.closeRightEye();
    }
    /**
     * this is the method to use if you want the robot to turn 90 degrees
       or any other amount. This method is based on robot orientation
       and not wheel rotation
       the distance in mm that each wheel needs to travel
     * @param {*} degrees
     * @param {*} blocking
     */
    turnDegrees(degrees, blocking = false) {
        const wheelTravelDistance = ((this.WHEEL_BASE_CIRCUMFERENCE * degrees) / 360);

        // the number of degrees each wheel needs to turn
        const wheelTurnDegrees = ((wheelTravelDistance / this.WHEEL_CIRCUMFERENCE) * 360);

        // get the starting position of each motor
        const startPositionLeft = this.getMotorEncoder(this.MOTOR_LEFT);
        const startPositionRight = this.getMotorEncoder(this.MOTOR_RIGHT);

        const destPositionLeft = startPositionLeft + wheelTurnDegrees;
        const destPositionRight = startPositionRight - wheelTurnDegrees;

        this.setMotorPosition(
            this.MOTOR_LEFT,
            destPositionLeft
        );
        this.setMotorPosition(
            this.MOTOR_RIGHT,
            destPositionRight
        );

        if (blocking) {
            while (!this.targetReached(
                destPositionLeft,
                destPositionRight
            )) {
                sleep.sleep(0.1);
            }
        }
    }

    //
    initLightSensor(port = 'AD1') {
        return new LightSensor(port, this);
    }
    initSoundSensor(port = 'AD1') {
        return new SoundSensor(port, this);
    }
    initUltrasonicSensor(port = 'AD1') {
        return new UltrasonicSensor(port, this);
    }
    initBuzzer(port = 'AD1') {
        return new Buzzer(port, this);
    }
    initLed(port = 'AD1') {
        return new Led(port, this);
    }
    initButtonSensor(port = 'AD1') {
        return new ButtonSensor(port, this);
    }
    initLineFollower() {
        return new LineFollow('I2C', this);
    }
    initServo(port = 'SERVO1') {
        return new Servo(port, this);
    }
    initDistanceSensor() {
        return new DistanceSensor('I2C', this);
    }
    initDhtSensor(sensorType = 0) {
        return new DHTSensor(this, sensorType);
    }
    initRemote(port = 'AD1') {
        // new Remote(port, this);
    }

    calibrateLineFollower() {
        return new LineThresholdSet('I2C', this);
    }
}

module.exports = EasyGoPiGo3;
