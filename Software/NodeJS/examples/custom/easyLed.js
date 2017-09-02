const sleep = require('sleep');
const EasyGopigo = require('../../lib/easyGopigo3');

const gpg = new EasyGopigo();
const myLed = gpg.initLed('AD1');

for (let i = 0, len = 100; i < len; i++) {
    myLed.lightMax();
    sleep.msleep(500);

    myLed.lightOn(30);
    sleep.msleep(500);

    myLed.lightOff();
    sleep.msleep(500);
}
