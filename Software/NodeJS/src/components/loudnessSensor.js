// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const AnalogSensor = require('./analogSensor');

class LoudnessSensor extends AnalogSensor {
    constructor(port = 'AD1', gpg = null) {
        console.log('LoudnessSensor init');
        super(port, 'INPUT', gpg);
        this.setDescriptor('Loudness sensor');
        this.maxValue = 1024; // based on empirical tests
    }
}

module.exports = LoudnessSensor;
