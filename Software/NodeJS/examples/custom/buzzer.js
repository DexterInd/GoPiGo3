const EasyGopigo = require('../../lib/easyGopigo3');
const sleep = require('sleep');

const gpg = new EasyGopigo();
const sensor = gpg.initBuzzer('AD2');

console.log('🔊');
sensor.soundOn();
sleep.sleep(2);
sensor.soundOff();
