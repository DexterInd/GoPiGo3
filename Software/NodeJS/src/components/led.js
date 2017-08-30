// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const AnalogSensor = require('./analogSensor');

class Led extends AnalogSensor {
    /**
     *
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('Led init');

        try {
            super(port, 'OUTPUT', gpg);
            this.setDescriptor('LED');
            this.setPin(1);
        } catch (err) {
            console.log(err);
            throw new Error(err);
        }
    }

    /**
     *
     * @param {*} power
     */
    lightOn(power) {
        this.write(power);
    }

    /**
     *
     */
    lightMax() {
        this.lightOn(100);
    }

    /**
     *
     */
    lightOff() {
        this.write(0);
    }

    /**
     *
     */
    isOn() {
        return this.value > 0;
    }

    /**
     *
     */
    isOff() {
        return this.value === 0;
    }
}

module.exports = Led;
