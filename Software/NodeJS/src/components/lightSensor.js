// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const AnalogSensor = require('./analogSensor');

class LightSensor extends AnalogSensor {
    /**
     * Creates a light sensor from which we can read.
     *  Light sensor is by default on pin A1(A-one)
     *  self.pin takes a value of 0 when on analog pin (default value)
     *      takes a value of 1 when on digital pin
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('LightSensor init');
        super(port, 'INPUT', gpg);
        this.setDescriptor('Light sensor');
    }
}

module.exports = LightSensor;
