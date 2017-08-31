const sleep = require('sleep');
const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();

gpg.stop();

console.log('Move the motors forward freely for 1 second.');
gpg.forward();
sleep.sleep(1);

console.log('Stop the motors for 1 second.');
gpg.stop();
sleep.sleep(1);

console.log('Drive the motors 50 cm and then stop.');
gpg.driveCm(50, true);

console.log('Wait 1 second.');
sleep.sleep(1);

console.log('Turn right 1 second.');
gpg.right();
sleep.sleep(1);

console.log('Turn left 1 second.');
gpg.left();
sleep.sleep(1);

console.log('Stop!');
gpg.stop();

console.log('Done!');
