//
// UNSTABLE CLASS
// NOTE: Before using this class please implement the DHT Class
//

const ValueError = require('../errors/valueError');

const _ = require('lodash');
const math = require('mathjs');
const sleep = require('sleep');
const utils = require('../utils/misc');
const i2c = require('i2c-bus');
const fs = require('fs');

const i2c0Path  = '/dev/i2c-0';
const i2c1Path  = '/dev/i2c-1';

const SCALE_C = 'c';
const SCALE_F = 'f';

class DHTSensor {
    bus = 0;
    busNumber = 0;

    address = 0x06;
    readCmd = 40;
    unused = 0;

    /**
     *  Support for the Adafruit DHT sensor, blue or white
     */
    constructor(gpg = null, sensorType = 0) {
        try {
            this.gpg = gpg;
            this.sensorType = sensorType;
            this.portId = 1; // SERIAL

            if (fs.existsSync(i2c0Path)) {
                this.busNumber = 0;
            } else if (fs.existsSync(i2c1Path)) {
                this.busNumber = 1;
            } else {
                throw new Error('GrovePI could not determine your i2c device');
            }

            this.bus = i2c.openSync(this.busNumber);

            // here we keep the temperature values after removing outliers
            this.filteredTemperature = [];
            // here we keep the filtered humidity values after removing the outliers
            this.filteredHumidity = [];
        } catch (err) {
            throw new ValueError('DHT Sensor not found');
        }
    }

    convertCtoF(temp) {
        return ((temp * 9) / 5) + 32;
    }
    convertFtoC(temp) {
        return ((temp - 32) * 5) / 9;
    }
    getHeatIndex(temp, hum, scale) {
        // http://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml
        const needsConversion = typeof scale === 'undefined' || scale === SCALE_C;
        temp = needsConversion ? this.convertCtoF(temp) : temp;

        // Steadman's result
        let heatIndex = 0.5 * (temp + 61 + ((temp - 68) * 1.2) + (hum * 0.094));

        // regression equation of Rothfusz is appropriate
        if (temp >= 80) {
            const heatIndexBase =   (-42.379                                  +
                                    (2.04901523  * temp)                      +
                                    (10.14333127               * hum)         +
                                    (-0.22475541 * temp        * hum)         +
                                    (-0.00683783 * temp * temp)               +
                                    (-0.05481717               * hum * hum)   +
                                    (0.00122874  * temp * temp * hum)         +
                                    (0.00085282  * temp        * hum * hum)   +
                                    (-0.00000199 * temp * temp * hum * hum));
            // adjustment
            if (hum < 13 && temp <= 112) {
                heatIndex = heatIndexBase
                            - (((13 - hum) / 4)
                            * Math.sqrt((17 - Math.abs(temp - 95)) / 17)
                );
            } else if (hum > 85 && temp <= 87) {
                heatIndex = heatIndexBase + (((hum - 85) / 10) * ((87 - temp) / 5));
            } else {
                heatIndex = heatIndexBase;
            }
        }
        return needsConversion ? this.convertFtoC(heatIndex) : heatIndex;
    }

    readSensor() {
        /*
        let messageType;
        if (port === this.GROVE_1) {
            messageType = this.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_1;
            portIndex = 0;
        } else if (port === this.GROVE_2) {
            messageType = this.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_2;
            portIndex = 1;
        }

        const dataOut = [this.gpg.SPI_Address, messageType, this.sensorType, 0, 0];
        const dataIn = this.gpg.spiTransferArray(dataOut);
        */

        /*
        this.bus.i2cWriteSync(this.address, 4,
            [40, this.portId, this.sensorType, this.unused]
        );

        const buffer = new Buffer(9);
        this.bus.i2cReadSync(this.address, 9, buffer);

        const tempBytes = buffer.slice(1, 5).reverse();
        const humBytes = buffer.slice(5, 9).reverse();

        let hex;

        hex = `0x${tempBytes.toString('hex')}`;
        let temp = (hex & 0x7fffff | 0x800000) * 1.0 / (2 ** 23) * (2 ** ((hex >> 23 & 0xff) - 127));
        temp = +(Number(parseFloat(temp - 0.5).toFixed(2)));
        if (this.scale === this.SCALE_F) {
            temp = this.convertCtoF(temp);
        }

        hex = `0x${humBytes.toString('hex')}`;
        let hum = (hex & 0x7fffff | 0x800000) * 1.0 / (2 ** 23) * (2 ** ((hex >> 23 & 0xff) - 127));
        hum = +(Number(parseFloat(hum - 2).toFixed(2)));

        console.log(buffer, tempBytes, humBytes, `0x${tempBytes.toString('hex')}`, `0x${humBytes.toString('hex')}`);
        console.log(temp, hum);

        const heatIndex = +(Number(parseFloat(
            this.getHeatIndex(temp, hum, this.scale)).toFixed(2)
        ));
        // From: https://github.com/adafruit/DHT-sensor-library/blob/master/DHT.cpp

        return [temp, hum, heatIndex];
        */
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
        import done internally so it's done on a as needed basis only
     */
    readTemperature() {
        utils.grabI2CRead();
        // const temp = DHT.dht(this.sensorType)[0]
        const temp = 0;
        utils.releaseI2CRead();

        if (temp === -2) {
            return 'Bad reading, trying again';
        } else if (temp === -3) {
            return 'Run the program as sudo';
        }

        return temp;
    }

    /**
     * Return values may be a float, or error strings
        TODO: raise errors instead of returning strings
     */
    readHumidity() {
        utils.grabI2CRead();
        // const humidity = DHT.dht(this.sensorType)[1]
        const humidity = 0;
        utils.releaseI2CRead();

        if (humidity === -2) {
            return 'Bad reading, trying again';
        } else if (humidity === -3) {
            return 'Run the program as sudo';
        }

        return humidity;
    }

    /**
     *
     */
    readDht() {
        utils.grabI2CRead();
        // const data = DHT.dht(this.sensorType)
        const data = [0, 0];
        utils.releaseI2CRead();

        if (data[0] === -2 || data[1] === -2) {
            return 'Bad reading, trying again';
        } else if (data[0] === -3 || data[1] === -3) {
            return 'Run the program as sudo';
        }

        return data;
    }

    /**
     * Function which eliminates the noise by using a statistical model we determine the standard
     * ormal deviation and we exclude anything that goes beyond a threshold think of a
     * probability distribution plot - we remove the extremes the greater the std_factor,
     * the more "forgiving" is the algorithm with the extreme values
     * @param {*} values
     * @param {*} stdFactor
     */
    _eliminateNoise(values, stdFactor = 2) {
        const mean = math.mean(values);
        const standardDeviation = math.std(values);
        let output = [];

        if (standardDeviation === 0) {
            return values;
        }

        output = _.map(values, v => v > mean - (stdFactor * standardDeviation));
        output = _.map(output, v => v < mean - (stdFactor * standardDeviation));

        return output;
    }

    /**
     * Function for processing the data filtering, periods of time, yada yada
     * @param {*} sensorType
     */
    _readingValues(/* sensorType = 0 */) {
        const secondsWindow = 10;
        let values = [];
        const xTemps = [];
        const xHums = [];
        let temp;
        let humidity;

        // while is threading
        let counter = 0;
        while (counter < secondsWindow) { /* && is threading */
            temp = null;
            humidity = null;

            utils.grabI2CRead();
            try {
                // const data = DHT.dht(this.sensorType)
                const data = [0, 0];
                temp = data[0];
                humidity = data[1];
            } catch (err) {
                console.log('Error', err);
                console.log('We\'ve got IO Error');
            }
            utils.releaseI2CRead();

            if (!isNaN(temp) && !isNaN(humidity)) {
                xTemps.push(temp);
                xHums.push(humidity);
                values.push({
                    'temp': temp,
                    'hum': humidity
                });
                counter++;
            }
            sleep.sleep(1);
        }
        // end while is threading

        const denoisedTemp = this._eliminateNoise(xTemps);
        const denoisedHum = this._eliminateNoise(xHums);
        this.filteredTemperature.push(
            math.mean(denoisedTemp)
        );
        this.filteredHumidity.push(
            math.mean(denoisedHum)
        );

        values = [];
    }

    /**
     * Function used to Read the values continuously and displays values after normalising them
     */
    /*
    def continuous_read_dht(self):
        """
        Function used to Read the values continuously and displays values after normalising them
        """
        import threading

        try:
            # here we start the thread we use a thread in order to gather/process the data separately from the printing process
            data_collector = threading.Thread(target = self._readingValues)
            data_collector.start()

            while not self.event.is_set():
                if len(self.filtered_temperature) > 0:
                # or we could have used filtered_humidity instead

                    temperature = self.filtered_temperature.pop()
                    humidity = self.filtered_humidity.pop()

            # here you can do whatever you want with the variables: print them, file them out, anything
            print('{},Temperature:{:.01f}C, Humidity:{:.01f}%' .format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),temperature,humidity))

            # wait a second before the next check
            time.sleep(1)

            # wait until the thread is finished
            data_collector.join()

        except Exception as e:
            self.event.set()
            print ("continuous_read_dht: {}".format(e))
    */
    continuousRead() {
        try {
            // here we start the thread we use a thread in order to gather/process
            // the data separately from the printing process
            // TODO: Start threading
            /*
                Readings:
                temperature = this.filteredTemperature.pop()
                humidity = this.filteredHumidity.pop()
            */
        } catch (err) {
            // TODO: Stop threading
            console.log('continuousRead error', err);
        }
    }
}

module.exports = DHTSensor;
