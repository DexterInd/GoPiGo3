const AnalogSensor = require('./analogSensor');

class Led extends AnalogSensor {
    /**
     *
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('Led init');

        try {
            super(port, 'OUTPUT', gpg);
            this.setPin(1);
            this.setDescriptor('LED');
        } catch (err) {
            console.log('Error', err);
            throw new Error(err);
        }
    }

    /**
     *
     * @param {*} power
     */
    lightOn(power) {
        this.write(power);
    }

    /**
     *
     */
    lightMax() {
        this.lightOn(100);
    }

    /**
     *
     */
    lightOff() {
        this.write(0);
    }

    /**
     *
     */
    isOn() {
        return this.value > 0;
    }

    /**
     *
     */
    isOff() {
        return this.value === 0;
    }
}

module.exports = Led;
