const sleep = require('sleep');
const EasyGopigo = require('../lib/easyGopigo3');

const gpg = new EasyGopigo();

/*
console.log('Move the motors forward freely for 1 second.');
gpg.forward();
sleep.sleep(1);

console.log('Stop the motors for 1 second.');
gpg.stop();
sleep.sleep(1);
*/

console.log('Press any key to exit');

process.stdin.setRawMode(true);
process.stdin.resume();
process.stdin.on('data', () => {
    gpg.stop();
    gpg.resetAll();
    process.exit(0);
});

console.log('Drive the motors 50 cm and then stop.');
gpg.driveCm(50, () => {
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
});

