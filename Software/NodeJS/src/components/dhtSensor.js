// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const DHT = require('di-sensors').DHT;

class DHTSensor {
    constructor(port, sensorType = 0, gpg) {
        this.gpg = gpg;
        const scale = 'c';
        this.dhtSensor = new DHT(sensorType, scale);
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
        import done internally so it's done on a as needed basis only
     */
    readTemperature() {
        const temp = this.dhtSensor.read()[0];
        return temp;
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
     */
    readHumidity() {
        const humidity = this.dhtSensor.read()[1];
        return humidity;
    }

    /**
     *
     */
    readDht() {
        const data = this.dhtSensor.read();
        return data;
    }
}

module.exports = DHTSensor;
