const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();
const calibrator = gpg.calibrateLineFollower();

console.log('Calibration...');
calibrator.calibrate();
