// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const Sensor = require('./sensor');

class Remote extends Sensor {
    /**
     * Creates a remote sensor
     */

    keycodes = ['up', 'left', 'ok', 'right', 'down', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '0', '#'];

    constructor(port = 'AD1', gpg = null) {
        console.log('Remote init');
        super(port, 'IR', gpg);
        this.setDescriptor('Remote Control');
    }

    read() {
        let value;

        try {
            value = this.gpg.getGroveValue(this.getPortId());
        } catch (err) {
            console.log('Error', err);
            value = -1;
        }

        return value;
    }

    getRemoteCode() {
        let string = '';
        const key = this.read();

        if (key > 0 && key < this.keycodes.length + 1) {
            string = this.keycodes[key - 1];
        }

        return string;
    }
}

module.exports = Remote;
