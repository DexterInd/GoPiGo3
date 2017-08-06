const AnalogSensor = require('./analogSensor');

class SoundSensor extends AnalogSensor {
    /**
     * Creates a sound sensor
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('SoundSensor init');
        super(port, 'INPUT', gpg);
        this.setPin(1);
        this.setDescriptor('Sound sensor');
    }
}

module.exports = SoundSensor;
