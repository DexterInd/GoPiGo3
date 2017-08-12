// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const readlineSync = require('readline-sync');
const LineSensor = require('./lineFollow');

class LineThresholdSet {
    lineSensor;

    constructor() {
        console.log('LineThresholdSet init');
    }

    calibrate() {
        this.lineSensor = new LineSensor();
        this.whiteLineSetup();
        this.blackLineSetup();
    }

    getSensorVal() {
        let val;
        while (true) {
            val = this.lineSensor.readSensor();
            if (val[0] !== -1) {
                return val;
            }
        }
    }

    whiteLineSetup() {
        this.lineSensor.resetBuffer();

        console.log('WHITE LINE SETUP');
        readlineSync.question('Keep all the sensors over a white strip and press ENTER');
        console.log('--> Line sensor readings:');
        console.log(this.getSensorVal());
        const save = readlineSync.keyInYN('If the reading look good, press \'y\' and ENTER to continue, any other key to read again');
        if (save) {
            this.lineSensor.setWhiteLine();
        }
        console.log('Current White Line values:', this.lineSensor.getWhiteLine());
    }

    blackLineSetup() {
        this.lineSensor.resetBuffer();

        console.log('BLACK LINE SETUP');
        readlineSync.question('Keep all the sensors over a black strip and press ENTER');
        console.log('--> Line sensor readings:');
        console.log(this.getSensorVal());
        const save = readlineSync.keyInYN('If the reading look good, press \'y\' and ENTER to continue, any other key to read again');
        if (save) {
            this.lineSensor.setBlackLine();
        }
        console.log('Current Black Line values:', this.lineSensor.getBlackLine());
    }
}

module.exports = LineThresholdSet;
