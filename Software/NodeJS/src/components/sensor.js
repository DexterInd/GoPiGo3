// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//

/**
Base class for all sensors

Class Attributes:
    port : string - user-readable port identification
    portID : integer - actual port id
    pinmode : "INPUT" or "OUTPUT"
    pin : GROVE_1_1, GROVE_1_2, GROVE_2_1, GROVE_2_2
    descriptor = string to describe the sensor for printing purposes

Class methods:
    setPort / getPort
    setPinMode / getPinMode
 */
class Sensor {
    PORTS = {};

    constructor(port, pinMode, gpg) {
        console.log('Sensor init');
        console.log('Pin mode', pinMode);

        this.gpg = gpg;
        this.setPort(port);
        this.setPinMode(pinMode);

        try {
            // I2C sensors don't need a valid gpg
            switch (pinMode) {
            default:
            case 'INPUT':
                this.gpg.setGroveType(this.portId,
                                        this.gpg.GROVE_TYPE.CUSTOM);
                this.gpg.setGroveMode(this.portId,
                                        this.gpg.GROVE_INPUT_ANALOG);
                break;
            case 'DIGITAL_INPUT':
                this.gpg.setGroveType(this.portId,
                                        this.gpg.GROVE_TYPE.CUSTOM);
                this.gpg.setGroveMode(this.portId,
                                        this.gpg.GROVE_INPUT_DIGITAL);
                break;
            case 'OUTPUT':
                this.gpg.setGroveType(this.portId,
                                        this.gpg.GROVE_TYPE.CUSTOM);
                this.gpg.setGroveMode(this.portId,
                                        this.gpg.GROVE_OUTPUT_PWM);
                break;
            case 'DIGITAL_OUTPUT':
                this.gpg.setGroveType(this.portId,
                                        this.gpg.GROVE_TYPE.CUSTOM);
                this.gpg.setGroveMode(this.portId,
                                        this.gpg.GROVE_OUTPUT_DIGITAL);
                break;
            case 'US':
                this.gpg.setGroveType(this.portId,
                                        this.gpg.GROVE_TYPE.US);
                break;
            case 'IR':
                this.gpg.setGroveType(this.portId,
                                    this.gpg.GROVE_TYPE.IR_GO_BOX);
                break;
            }
        } catch (err) {
            console.log('Error', err);
        }
    }

    setPin(pin) {
        if (this.port === 'AD1') {
            if (pin === 1) {
                this.pin = this.gpg.GROVE_1_1;
            } else {
                this.pin = this.gpg.GROVE_1_2;
            }
        } else if (this.port === 'AD2') {
            if (pin === 1) {
                this.pin = this.gpg.GROVE_2_1;
            } else {
                this.pin = this.gpg.GROVE_2_2;
            }
        }
        console.log('Setting pin to', this.pin);
    }
    getPin() {
        return this.pin;
    }
    setPort(port) {
        this.port = port;

        switch (port) {
        case 'AD1':
            this.portId = this.gpg.GROVE_1;
            break;

        case 'AD2':
            this.portId = this.gpg.GROVE_2;
            break;

        case 'SERIAL':
            this.portId = 1;
            break;

        case 'I2C':
            this.portId = 2;
            break;

        case 'SERVO1':
            this.portId = this.gpg.SERVO_1;
            break;

        case 'SERVO2':
            this.portId = this.gpg.SERVO_2;
            break;

        default:
            this.portId = -5;
            break;
        }

        console.log('Port Id', this.portId);
    }
    getPort() {
        return this.port;
    }
    getPortId() {
        return this.portId;
    }
    setPinMode(pinMode) {
        this.pinMode = pinMode;
    }
    getPinMode() {
        return this.pinMode;
    }
    setDescriptor(descriptor) {
        this.descriptor = descriptor;
    }
}

module.exports = Sensor;
