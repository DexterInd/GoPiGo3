// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

const ValueError = require('../errors/valueError');

const Sensor = require('./sensor');

/**
 * Wrapper to control the Servo Motors on the GPG3.
    Allows you to rotate the servo by feeding in the angle of rotation.
    Connect the Servo to the Servo1 and Servo2 ports of GPG3.
 */
class Servo extends Sensor {
    PULSE_WIDTH_RANGE = 1850;
    // Pulse width range in us corresponding to 0 to 180 degrees

    constructor(port = 'SERVO1', gpg) {
        try {
            super(port, 'OUTPUT', gpg);
            this.setDescriptor('GoPiGo3 Servo');
        } catch (err) {
            throw new ValueError('GoPiGo3 Servo not found');
        }
    }

    /**
     * This calculation will vary with servo and is an approximate angular movement of the servo
        Pulse Width varies between 575us to 24250us for a 60KHz Servo Motor which
        rotates between 0 to 180 degrees.

        0 degree ~= 575us
        180 degree ~= 2425us
        Pulse width Range= 2425-575 =1850
        => 1 degree rotation requires ~= 10.27us
     * @param {*} servoPosition
     */
    rotateServo(servoPosition) {
        servoPosition = servoPosition > 180 ? 180 : servoPosition;
        servoPosition = servoPosition < 0 ? 0 : servoPosition;

        const pulseWidth = Math.round(
            (1500 - (this.PULSE_WIDTH_RANGE / 2)) +
            ((this.PULSE_WIDTH_RANGE / 180) * servoPosition)
        );
        this.gpg.setServo(this.getPortId(), parseInt(pulseWidth, 0));
    }

    /**
     *
     */
    resetServo() {
        this.gpg.setServo(this.getPortId(), 0);
    }

}

module.exports = Servo;
