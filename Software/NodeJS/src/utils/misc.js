const I2CMutex = require('./i2cMutex');

const i2cMutex = new I2CMutex();

module.exports = {
    I2CReady: true,

    twoDigitHex: (c) => {
        const hex = c.toString(16);
        return hex.length === 1 ? `0${hex}` : hex;
    },

    grabI2CRead: () => {
        if (i2cMutex.I2CMutexAcquire()) {
            this.I2CReady = false;
        }
    },
    releaseI2CRead: () => {
        i2cMutex.I2CMutexRelease();
        this.I2CReady = true;
    }
};
