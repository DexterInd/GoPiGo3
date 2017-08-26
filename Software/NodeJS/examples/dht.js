const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();
const sensor = gpg.initDhtSensor('AD2', 11);

console.log('DHT values', sensor.readDht());
