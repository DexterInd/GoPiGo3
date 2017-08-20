// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const _ = require('lodash');
const sleep = require('sleep');
const utils = require('../utils/misc');

const Sensor = require('./sensor');
const DistanceSensorLib = require('di-sensors').sensors.DistanceSensor; 

/**
 * Wrapper to measure the distance in cms from the DI distance sensor.
        Connect the distance sensor to I2C port.
 */
class DistanceSensor extends Sensor {

    constructor(port = 'I2C', bus = 'GPG3_AD1', gpg) {
        super(port, 'OUTPUT', gpg);

        try {
            this.distanceSensor = new DistanceSensorLib(bus, null, {
                device: gpg
            });
        } catch (err) {
            throw new Error('Distance Sensor not found');
        }

        this.setDescriptor('Distance Sensor');
    }

    /**
     *
     */
    readMm() {
        let mm = 8190;
        // 8190 is what the sensor sends when it's out of range
        // we're just setting a default value

        const readings = [];
        let attempt = 0;

        // try 3 times to have a reading that is
        // smaller than 8m or bigger than 5 mm.
        // if sensor insists on that value, then pass it on
        while ((mm > 8000 || mm < 5) && attempt < 3) {
            try {
                utils.grabI2CRead();
                mm = this.distanceSensor.readRangeSingleMillimeters();
                utils.releaseI2CRead();
            } catch (err) {
                mm = 0;
            }
            attempt++;
            sleep.msleep(1000);
        }

        // add the reading to our last 3 readings
        // a 0 value is possible when sensor is not found
        if ((mm < 8000 && mm > 5) || mm === 0) {
            readings.push(mm);
        }
        if (readings.length > 3) {
            readings.pop();
        }

        // calculate an average and limit it to 5 > X > 3000
        if (readings.length > 1) { // avoid division by 0
            mm = Math.round(_.sum(readings) / parseFloat(readings.length));
        }
        if (mm > 3000) {
            mm = 3000;
        }

        return mm;
    }

    /**
     *
     */
    read() {
        return parseInt(this.readMm() / 10, 0);
    }

    /**
     *
     */
    readInches() {
        return this.read() / 2.54;
    }
}

module.exports = DistanceSensor;
