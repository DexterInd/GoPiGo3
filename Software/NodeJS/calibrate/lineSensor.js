const EasyGopigo3 = require('../lib/easyGopigo3');

const gpg = new EasyGopigo3();
const calibrator = gpg.calibrateLineFollower();

console.log('Calibration...');
calibrator.calibrate();
