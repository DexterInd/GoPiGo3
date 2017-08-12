// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const Sensor = require('./sensor');

class DigitalSensor extends Sensor {

    constructor(port, pinMode, gpg) {
        console.log('DigitalSensor init');
        super(port, pinMode, gpg);
    }

    /**
     * Return values:
     *  0 or 1 are valid values
     *  -1 may occur when there's a reading error

     *  On a reading error, a second attempt will be made before
     *  returning a -1 value
     */
    read() {
        const getValue = () => this.gpg.getGroveState(this.getPin());

        try {
            this.value = getValue();
        } catch (err) {
            try {
                this.value = getValue();
            } catch (err2) {
                throw new Error(err2);
            }
        }

        return this.value;
    }

    /**
     * TODO: Missing documentation
     * @param {*} power
     */
    write(power) {
        this.power = power;
        // TODO: Not ported to GPG3 yet
        return 1;
    }
}

module.exports = DigitalSensor;
