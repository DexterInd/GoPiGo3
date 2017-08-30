// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const AnalogSensor = require('./analogSensor');

class SoundSensor extends AnalogSensor {
    /**
     * Creates a sound sensor
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('SoundSensor init');
        super(port, 'INPUT', gpg);
        this.setDescriptor('Sound sensor');
        this.setPin(1);
    }
}

module.exports = SoundSensor;
