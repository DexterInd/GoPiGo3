// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const sleep = require('sleep');
const Sensor = require('./sensor');

class AnalogSensor extends Sensor {

    constructor(port, pinMode, gpg) {
        console.log('AnalogSensor init');

        super(port, pinMode, gpg);

        this.value = 0;
        this.freq = 24000;
        this.maxValue = 4096;

        // select the outwards pin of the grove connector
        this.setPin(1);

        // this delay is at least needed by the Light sensor
        // TODO: Why don't move it in the light sensor class then?
        sleep.msleep(1000);
    }

    /**
     * Read an analog value from a sensor.
     *  Will make up to two attempts to get a valid value
     *  If it succeeds, the valid value is returned
     *  Otherwise it prints an error statement and returns 0
     */
    read() {
        const getValue = () => this.gpg.getGroveAnalog(this.getPin());

        try {
            this.value = getValue();
        } catch (err) {
            console.log(err);
            try {
                this.value = getValue();
            } catch (err2) {
                console.log(err2);
                return 0;
            }
        }

        return this.value;
    }

    /**
     * Brings the sensor read to a percent scale
     */
    percentRead() {
        let percent = Math.round(this.read() * 100 / this.maxValue);

        if (percent > 100) {
            percent = 100;
        }

        return percent;
    }

    /**
     * TODO: Missing documentation
     * @param {*} power
     */
    write(power) {
        this.value = power;
        return this.gpg.setGrovePwmDuty(this.getPin(), power);
    }

    /**
     * TODO: Missing documentation
     * @param {*} freq
     */
    writeFreq(freq) {
        this.freq = freq;
        const output = this.gpg.setGrovePwmFrequency(this.getPortId(), this.freq);
        console.log('Analog write on %s at %s', this.getPortId(), this.freq);
        return output;
    }
}

module.exports = AnalogSensor;
