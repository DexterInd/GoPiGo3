const EasyGopigo3 = require('../../ib/easyGopigo3');

const gpg = new EasyGopigo3();
const sensor = gpg.initDhtSensor('SERIAL', 11);

console.log('DHT values', sensor.readDht());
