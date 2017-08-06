const DigitalSensor = require('./digitalSensor');

class ButtonSensor extends DigitalSensor {
    constructor(port = 'AD1', gpg = null) {
        console.log('ButtonSensor init');
        super(port, 'DIGITAL_INPUT', gpg);
        this.setPin(1);
        this.setDescriptor('Button sensor');
    }

    /**
     *
     */
    isButtonPressed() {
        return this.read() === 1;
    }
}

module.exports = ButtonSensor;
