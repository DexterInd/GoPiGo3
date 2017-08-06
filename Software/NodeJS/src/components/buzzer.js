const AnalogSensor = require('./analogSensor');

/**
    Default port is AD1
    It has three methods:
    sound(power) -> will change incoming power to 0 or 50
    note: 50 duty cycle allows for musical tones
    soundOff() -> which is the same as _sound(0)
    soundOn() -> which is the same as _sound(50)
 */
class Buzzer extends AnalogSensor {

    scale = {
        'A3': 220,
        'A3#': 233,
        'B3': 247,
        'C4': 261,
        'C4#': 277,
        'D4': 293,
        'D4#': 311,
        'E4': 329,
        'F4': 349,
        'F4#': 370,
        'G4': 392,
        'G4#': 415,
        'A4': 440,
        'A4#': 466,
        'B4': 494,
        'C5': 523,
        'C5#': 554,
        'D5': 587,
        'D5#': 622,
        'E5': 659,
        'F5': 698,
        'F5#': 740,
        'G5': 784,
        'G5#': 831,
    }

    /**
     * Creates a sound sensor
     */
    constructor(port = 'AD1', gpg = null) {
        console.log('Buzzer init');
        try {
            super(port, 'OUTPUT', gpg);
            this.setPin(1);
            this.setDescriptor('Buzzer');
            this.power = 50;
            this.freq = 329;
            this.soundOff();
        } catch (err) {
            throw new Error(err);
        }
    }

    /**
     *
     * @param {*} freq
     */
    sound(freq) {
        let power;
        freq = isNaN(freq) ? 0 : parseInt(freq, 0);

        // limit duty cycles (aka power) values to either 0 or 50
        if (freq <= 0) {
            power = 0;
            freq = 0;
        } else {
            power = 50;
        }

        // if buzzer has to emit a sound then set frequency
        if (power === 50) {
            // translation_factor = ((40000 - 20) / 100)
            // freq = (freq * translation_factor) + 20
            this.writeFreq(freq);
        }

        // set duty cycle, either 0 or 50
        this.write(power);
    }

    /**
     * Makes buzzer silent
     */
    soundOff() {
        this.sound(0);
    }

    /**
     * Default buzzer sound. It will take the internal frequency as is
     */
    soundOn() {
        this.sound(this.freq);
    }
}

module.exports = Buzzer;
