// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const ValueError = require('../errors/valueError');
const utils = require('../utils/misc');
const DHT = require('di-sensors').sensors.DHT;

class DHTSensor {
    constructor(gpg = null, sensorType = DHT.DHT11) {
        try {
            const pin = 0;
            const address = null;
            this.dhtSensor = new DHT(pin, address, 'GPG3_AD1', sensorType, DHT.SCALE_C, {
                device: gpg
            });
        } catch (err) {
            throw new ValueError('DHT Sensor not found');
        }
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
        import done internally so it's done on a as needed basis only
     */
    readTemperature() {
        utils.grabI2CRead();
        const temp = this.dhtSensor.read()[0];
        utils.releaseI2CRead();

        return temp;
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
     */
    readHumidity() {
        utils.grabI2CRead();
        const humidity = this.dhtSensor.read()[1];
        utils.releaseI2CRead();

        return humidity;
    }

    /**
     *
     */
    readDht() {
        utils.grabI2CRead();
        const data = this.dhtSensor.read();
        utils.releaseI2CRead();

        return data;
    }
}

module.exports = DHTSensor;
