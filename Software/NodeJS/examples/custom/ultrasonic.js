const sleep = require('sleep');
const EasyGopigo3 = require('../../lib/easyGopigo3');

const gpg = new EasyGopigo3();
const sensor = gpg.initUltrasonicSensor('AD1');

console.log(sensor.read(), sensor.readMm(), sensor.readInches());
console.log('Is too close', sensor.isTooClose());
