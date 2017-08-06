const sleep = require('sleep');
const _ = require('lodash');

const ValueError = require('../errors/valueError');
const AnalogSensor = require('./analogSensor');

class UltraSonicSensor extends AnalogSensor {
    /**
     * Creates a sound sensor
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('Ultrasonic init');

        try {
            super(port, 'US', gpg);
            this.safeDistance = 500;
            this.setPin(1);
            this.setDescriptor('Ultrasonic sensor');
        } catch (err) {
            throw new Error(err);
        }
    }

    /**
     *
     */
    isTooClose() {
        let value = 0;

        try {
            value = this.gpg.getGroveValue(this.getPortId());
        } catch (err) {
            console.log('Error', err);
            value = 0;
        }

        if (value < this.getSafeDistance()) {
            return true;
        }

        return value;
    }

    /**
     *
     * @param {*} dist
     */
    setSafeDistance(dist) {
        this.safeDistance = parseInt(dist, 0);
    }

    /**
     *
     */
    getSafeDistance() {
        return this.safeDistance;
    }

    /**
     *
     */
    read() {
        const output = this.readMm();
        return output >= 15 && output <= 5010
                ? parseInt(Math.round(output / 10.0), 0)
                : output;
    }

    /**
     * Ultrasonic sensor is limited to 15-4300 range in mm
     *  Take 3 readings, discard any that's higher than 4300 or lower than 15
     *  If we discard 5 times, then assume there's nothing in front
     *      and return 501
     *
     *  Possible returns:
     *  0    :  sensor not found
     *  5010 :  object not detected
     *  between 15 and 4300 : actual distvarance read
     */
    readMm() {
        let output = 0;
        const readings = [];
        let skip = 0;
        let value = 0;

        while (readings.length < 3 && skip < 5) {
            try {
                value = this.gpg.getGroveValue(this.getPortId());
                console.log('Raw Value', value);
            } catch (err) {
                if (err instanceof ValueError) {
                    value = 5010; // assume open road ahead
                    sleep.msleep(50);
                } else {
                    console.log('Error', err);

                    skip++;
                    sleep.msleep(50);
                    continue;
                }
            }

            if (value <= 4300 && value >= 15) {
                readings.push(value);
            } else {
                skip++;
            }
        }

        if (skip >= 5) {
            // if value = 0 it means Ultrasonic Sensor wasn't found
            if (value === 0) {
                return 0;
            }

            // no special meaning to the number 5010
            return 5010;
        }

        _.each(readings, (reading) => {
            output += reading;
        });

        return parseInt(output / readings.length, 0);
    }

    /**
     *
     */
    readInches() {
        const output = this.read(); // cm reading
        return output === 501 ? output : parseInt(output / 2.54, 0);
    }
}

module.exports = UltraSonicSensor;
