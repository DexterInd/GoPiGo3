/*
*
* https://www.dexterindustries.com/GoPiGo/
* https://github.com/DexterInd/GoPiGo3
*
* Copyright (c) 2017 Dexter Industries
* Released under the MIT license (http://choosealicense.com/licenses/mit/).
* For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
*
* This code is an example for using the grove buzzer with the GoPiGo3.
*
* Hardware: Connect a grove buzzer to AD1 port.
*
* Results: When you run this program, the buzzer should repeat the scale of middle C through tenor C.
*
*/

const Gopigo = require('../lib/gopigo3');
const sleep = require('sleep');

const gpg = new Gopigo();
const scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25];

gpg.setGroveType(Gopigo.GROVE_1, Gopigo.GROVE_TYPE.CUSTOM);
gpg.setGroveMode(Gopigo.GROVE_1_1, Gopigo.GROVE_OUTPUT_PWM);
gpg.setGrovePwmDuty(Gopigo.GROVE_1_1, 50);

let note = 0;
const interval = setInterval(() => {
    gpg.setGrovePwmFrequency(Gopigo.GROVE_1, scale[note]);
    note++;
    if (note >= scale.length) {
        note = 0;
    }
}, 500);

console.log('Press any key to exit');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', () => {
    clearInterval(interval);
    gpg.resetAll();
    process.exit(0);
});
