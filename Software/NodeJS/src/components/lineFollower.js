// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const _ = require('lodash');
const LineSensor = require('./lineFollower/lineFollow');
const ValueError = require('../errors/valueError');
const Sensor = require('./sensor');

/**
 * The line follower detects the presence of a black line or its
      absence.
    You can use this in one of three ways.
    1. You can use readPosition() to get a simple position status:
        center, left or right.
        these indicate the position of the black line.
        So if it says left, the GoPiGo has to turn right
    2. You can use read() to get a list of the five sensors.
        each position in the list will either be a 0 or a 1
        It is up to you to determine where the black line is.
    3. You can use readRawSensors() to get raw values from all sensors
        You will have to handle the calibration yourself
 */
class LineFollower extends Sensor {

    lineSensor = new LineSensor();

    constructor(port = 'I2C', gpg) {
        try {
            super(port, 'INPUT', gpg);
            this.setDescriptor('Line Follower');
        } catch (err) {
            console.log(err);
            throw new ValueError('Line Follower Library not found');
        }
    }

    /**
     * Returns raw values from all sensors
        From 0 to 1023
        May return a list of -1 when there's a read error
     */
    readRawSensors() {
        const fiveVals = this.lineSensor.readSensor();

        if (fiveVals !== -1) {
            return fiveVals;
        }

        return [-1, -1, -1, -1, -1];
    }

    /**
     *
     */
    getWhiteCalibration() {
        return this.lineSensor.getWhiteLine();
    }

    /**
     *
     */
    getBlackCalibration() {
        return this.lineSensor.getBlackLine();
    }

    /**
     * Returns a list of 5 values between 0 and 1
        Depends on the line sensor being calibrated first
            through the Line Sensor Calibration tool
        May return all -1 on a read error
     */
    read() {
        return this.lineSensor.absoluteLinePos();
    }

    /**
     * Returns a string telling where the black line is, compared to
            the GoPiGo
        Returns: "left", "right", "center", "black", "white"
        May return "unknown"
        This method is not intelligent enough to handle intersections.
     */
    readPosition() {
        const fiveVals = this.read();

        if (
            _.isEqual(fiveVals, [0, 0, 1, 0, 0])
            ||
            _.isEqual(fiveVals, [0, 1, 1, 1, 0])
        ) {
            return 'center';
        }

        if (
            _.isEqual(fiveVals, [1, 1, 1, 1, 1])
        ) {
            return 'black';
        }

        if (
            _.isEqual(fiveVals, [0, 0, 0, 0, 0])
        ) {
            return 'white';
        }

        if (
            _.isEqual(fiveVals, [0, 1, 1, 0, 0])
            || _.isEqual(fiveVals, [0, 1, 0, 0, 0])
            || _.isEqual(fiveVals, [1, 0, 0, 0, 0])
            || _.isEqual(fiveVals, [1, 1, 0, 0, 0])
            || _.isEqual(fiveVals, [1, 1, 1, 0, 0])
            || _.isEqual(fiveVals, [1, 1, 1, 1, 0])
        ) {
            return 'left';
        }

        if (
            _.isEqual(fiveVals, [0, 0, 0, 1, 0])
            || _.isEqual(fiveVals, [0, 0, 1, 1, 0])
            || _.isEqual(fiveVals, [0, 0, 0, 0, 1])
            || _.isEqual(fiveVals, [0, 0, 0, 1, 1])
            || _.isEqual(fiveVals, [0, 0, 1, 1, 1])
            || _.isEqual(fiveVals, [0, 1, 1, 1, 1])
        ) {
            return 'right';
        }

        return 'unknown';
    }
}

module.exports = LineFollower;
