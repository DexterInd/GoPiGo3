/*
*
* https://www.dexterindustries.com/GoPiGo/
* https://github.com/DexterInd/GoPiGo3
*
* Copyright (c) 2017 Dexter Industries
* Released under the MIT license (http://choosealicense.com/licenses/mit/).
* For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
*
* This code is an example for using the GoPiGo3 software I2C busses.
*
* Hardware: Connect an I2C device to port AD1.
*
*/

const Gopigo3 = require('../lib/gopigo3');
const sleep = require('sleep');

const gpg = new Gopigo3();
const I2CSlaveAddress = 0x24;

console.log('Press any key to exit');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', () => {
    gpg.resetAll();
    process.exit(0);
});

gpg.setGroveType(Gopigo3.GROVE_1, Gopigo3.GROVE_TYPE.I2C);
let i = 0;

while (true) {
    gpg.groveI2cTransfer(Gopigo3.GROVE_1, I2CSlaveAddress, [i]);                     // write one byte
    console.log(i, gpg.groveI2cTransfer(Gopigo3.GROVE_1, I2CSlaveAddress, [], 16));  // read sixteen bytes

    sleep.msleep(100);

    i++;
    if (i > 15) {
        i = 0;
    }
}
