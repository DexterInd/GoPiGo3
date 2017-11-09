// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const DigitalSensor = require('./digitalSensor');

class MotionSensor extends DigitalSensor {
    constructor(port = 'AD1', gpg = null) {
        console.log('MotionSensor init');
        super(port, 'DIGITAL_INPUT', gpg);
        this.setDescriptor('Motion sensor');
    }

    motionDetected() {
        return this.read() === 1;
    }
}

module.exports = MotionSensor;
