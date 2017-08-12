// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const Lock = require('lock-me');
const sleep = require('sleep');

class I2cMutex {
    DexterLockI2CHandle = false

    I2CMutexAcquire() {
        let acquired;

        while (this.DexterLockI2CHandle) {
            sleep(0.001);
        }

        this.DexterLockI2CHandle = true;
        acquired = false;

        const isAcquired = (err) => {
            if (err) {
                // already locked by a different process
                sleep(0.001);
            }
            // lock
            acquired = true;
        };

        while (!acquired) {
            this.DexterLockI2CHandle = new Lock();
            const lockfile = '/run/lock/DexterLockI2C';
            this.DexterLockI2CHandle(lockfile, isAcquired);
        }

        return acquired;
    }

    I2CMutexRelease() {
        if (this.DexterLockI2CHandle) {
            this.DexterLockI2CHandle.close((err) => {
                if (err) {
                    throw err;
                }
                // unlocked
                this.DexterLockI2C_handle = false;
                sleep(0.001);
            });
        }
    }
}

module.exports = I2cMutex;
