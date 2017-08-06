const sleep = require('sleep');
const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();
const myServo = gpg.initServo('SERVO2');

gpg.openLeftEye();
gpg.openRightEye();

myServo.rotateServo(10);

/*
for (let i = 90, len = 180; i < len; i++) {
    myServo.rotateServo(i);
    sleep.msleep(50);
}
*/

sleep.sleep(5);

gpg.closeLeftEye();
gpg.closeRightEye();
myServo.resetServo();
