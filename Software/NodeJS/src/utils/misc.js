// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const I2CMutex = require('./i2cMutex');

const i2cMutex = new I2CMutex();

module.exports = {
    twoDigitHex: (c) => {
        const hex = c.toString(16);
        return hex.length === 1 ? `0${hex}` : hex;
    },

    grabI2CRead: () => true, // i2cMutex.I2CMutexAcquire(),
    releaseI2CRead: () => true // i2cMutex.I2CMutexRelease()
};
