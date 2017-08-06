const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();
const sensor = gpg.initDhtSensor(0);
console.log(sensor.readSensor());
