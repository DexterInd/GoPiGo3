// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const Lock = require('lockfile');
const sleep = require('sleep');

class I2cMutex {
    isAcquired = false;
    lockFile = '/run/lock/DexterLockI2C';

    I2CMutexAcquire() {
        const _this = this;

        while (this.isAcquired) {
            sleep.msleep(1);
        }

        this.isAcquired = false;

        while (!this.isAcquired) {
            Lock.lock(this.lockFile, (err) => {
                if (err) {
                    // already locked by a different process
                    sleep.msleep(1);
                }
                // lock
                console.log('I2C Acquired');
                _this.isAcquired = true;
            });
        }

        return this.isAcquired;
    }

    I2CMutexRelease() {
        const _this = this;

        Lock.unlock(this.lockFile, (err) => {
            if (err) {
                throw err;
            }
            // unlocked
            _this.isAcquired = false;
            sleep.msleep(1);
        });
    }
}

module.exports = I2cMutex;
