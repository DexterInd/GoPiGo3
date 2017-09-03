const sleep = require('sleep');
const EasyGopigo3 = require('../../lib/easyGopigo3');

const gpg = new EasyGopigo3();
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
