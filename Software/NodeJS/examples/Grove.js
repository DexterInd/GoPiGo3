/*
*
* https://www.dexterindustries.com/GoPiGo/
* https://github.com/DexterInd/GoPiGo3
*
* Copyright (c) 2017 Dexter Industries
* Released under the MIT license (http://choosealicense.com/licenses/mit/).
* For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
*
* This code is an example for demonstrating grove devices with the GoPiGo3.
*
* Hardware: Connect a grove buzzer to port AD1, and a grove potentiometer to port AD2.
*
* Results: When you run this program, the position of the potentiometer will determine the tone of the buzzer.
*
*/

const Gopigo = require('../lib/gopigo3');
const sleep = require('sleep');

const gpg = new Gopigo();

gpg.setGroveType(Gopigo.GROVE_1, Gopigo.GROVE_TYPE_CUSTOM);
gpg.setGroveType(Gopigo.GROVE_2, Gopigo.GROVE_TYPE_CUSTOM);

gpg.setGroveMode(Gopigo.GROVE_1_1, Gopigo.GROVE_OUTPUT_PWM);
gpg.setGroveMode(Gopigo.GROVE_2, Gopigo.GROVE_INPUT_ANALOG);

let duty = 10;
// let freq = 0;

const interval = setInterval(() => {
    duty++;
    if (duty > 90) {
        duty = 10;
    }
    gpg.setGrovePwmDuty(Gopigo.GROVE_1_1, duty);
    gpg.setGrovePwmFrequency(Gopigo.GROVE_1, gpg.getGroveAnalog(Gopigo.GROVE_2_1));
}, 100);

console.log('Press any key to exit');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', () => {
    clearInterval(interval);
    gpg.resetAll();
    process.exit(0);
});
