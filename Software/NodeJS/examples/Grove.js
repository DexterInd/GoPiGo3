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

const Gopigo3 = require('../lib/gopigo3');
const sleep = require('sleep');

const gpg = new Gopigo3();

gpg.setGroveType(Gopigo3.GROVE_1, Gopigo3.GROVE_TYPE_CUSTOM);
gpg.setGroveType(Gopigo3.GROVE_2, Gopigo3.GROVE_TYPE_CUSTOM);

gpg.setGroveMode(Gopigo3.GROVE_1_1, Gopigo3.GROVE_OUTPUT_PWM);
gpg.setGroveMode(Gopigo3.GROVE_2, Gopigo3.GROVE_INPUT_ANALOG);

let duty = 10;
// let freq = 0;

const interval = setInterval(() => {
    duty++;
    if (duty > 90) {
        duty = 10;
    }
    gpg.setGrovePwmDuty(Gopigo3.GROVE_1_1, duty);
    gpg.setGrovePwmFrequency(Gopigo3.GROVE_1, gpg.getGroveAnalog(Gopigo3.GROVE_2_1));
}, 100);

console.log('Press any key to exit');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', () => {
    clearInterval(interval);
    gpg.resetAll();
    process.exit(0);
});
