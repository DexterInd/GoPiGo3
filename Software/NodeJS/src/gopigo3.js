// https://www.dexterindustries.com/GoPiGo/
// https://github.com/DexterInd/GoPiGo3
//
// Copyright (c) 2017 Dexter Industries
// Released under the MIT license (http://choosealicense.com/licenses/mit/).
// For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
//
// Node.js drivers for the GoPiGo3

const Utils = require('./utils/misc');
const Enumeration = require('./utils/enumeration');
const FirmwareVersionError = require('./errors/firmwareVersionError');
const I2CError = require('./errors/i2cError');
const ValueError = require('./errors/valueError');
const SensorError = require('./errors/sensorError');

const SPIDevice = require('spi-device');
const sleep = require('sleep');

class Gopigo3 {
    static FIRMWARE_VERSION_REQUIRED   = '0.3.x';
    // Make sure the top 2 of 3 numbers match
    static SPI_MAX_SPEED_HZ            = 500000;
    static SPI_MODE                    = 0b00;
    static SPI_BITS_PER_WORD           = 8;
    static WHEEL_BASE_WIDTH            = 117;
    // distance (mm) from left wheel to right wheel. This works with
    // the initial GPG3 prototype. Will need to be adjusted.
    static WHEEL_DIAMETER              = 66.5;
    // wheel diameter (mm)
    static WHEEL_BASE_CIRCUMFERENCE    = Gopigo3.WHEEL_BASE_WIDTH * Math.PI;
    // The circumference of the circle the wheels will trace while turning (mm)
    static WHEEL_CIRCUMFERENCE         = Gopigo3.WHEEL_DIAMETER * Math.PI;
    // The circumference of the wheels (mm)
    static MOTOR_GEAR_RATIO            = 120;
    // Motor gear ratio # 220 for Nicole's prototype
    static ENCODER_TICKS_PER_ROTATION  = 6;
    // Encoder ticks per motor rotation (number of magnet positions) # 16 for early prototypes
    static MOTOR_TICKS_PER_DEGREE = ((Gopigo3.MOTOR_GEAR_RATIO * Gopigo3.ENCODER_TICKS_PER_ROTATION) / 360.0);
    // encoder ticks per output shaft rotation degree

    static GROVE_I2C_LENGTH_LIMIT      = 16;

    static GPG_SPI;

    static SPI_MESSAGE_TYPE = new Enumeration(`
        NONE,
        
        GET_MANUFACTURER,
        GET_NAME,
        GET_HARDWARE_VERSION,
        GET_FIRMWARE_VERSION,
        GET_ID,

        SET_LED,

        GET_VOLTAGE_5V,
        GET_VOLTAGE_VCC,

        SET_SERVO,

        SET_MOTOR_PWM,

        SET_MOTOR_POSITION,
        SET_MOTOR_POSITION_KP,
        SET_MOTOR_POSITION_KD,

        SET_MOTOR_DPS,

        SET_MOTOR_LIMITS,

        OFFSET_MOTOR_ENCODER,

        GET_MOTOR_ENCODER_LEFT,
        GET_MOTOR_ENCODER_RIGHT,

        GET_MOTOR_STATUS_LEFT,
        GET_MOTOR_STATUS_RIGHT,

        SET_GROVE_TYPE,
        SET_GROVE_MODE,
        SET_GROVE_STATE,
        SET_GROVE_PWM_DUTY,
        SET_GROVE_PWM_FREQUENCY,

        GET_GROVE_VALUE_1,
        GET_GROVE_VALUE_2,
        GET_GROVE_STATE_1_1,
        GET_GROVE_STATE_1_2,
        GET_GROVE_STATE_2_1,
        GET_GROVE_STATE_2_2,
        GET_GROVE_VOLTAGE_1_1,
        GET_GROVE_VOLTAGE_1_2,
        GET_GROVE_VOLTAGE_2_1,
        GET_GROVE_VOLTAGE_2_2,
        GET_GROVE_ANALOG_1_1,
        GET_GROVE_ANALOG_1_2,
        GET_GROVE_ANALOG_2_1,
        GET_GROVE_ANALOG_2_2,

        START_GROVE_I2C_1,
        START_GROVE_I2C_2,
    `)

    static GROVE_TYPE = new Enumeration(`
        CUSTOM = 1,
        IR_DI_REMOTE,
        IR_EV3_REMOTE,
        US,
        I2C,
    `)

    static GROVE_STATE = new Enumeration(`
        VALID_DATA,
        NOT_CONFIGURED,
        CONFIGURING,
        NO_DATA,
        I2C_ERROR,
    `)

    static LED_EYE_LEFT        = 0x02;
    static LED_EYE_RIGHT       = 0x01;
    static LED_BLINKER_LEFT    = 0x04;
    static LED_BLINKER_RIGHT   = 0x08;
    static LED_LEFT_EYE        = Gopigo3.LED_EYE_LEFT;
    static LED_RIGHT_EYE       = Gopigo3.LED_EYE_RIGHT;
    static LED_LEFT_BLINKER    = Gopigo3.LED_BLINKER_LEFT;
    static LED_RIGHT_BLINKER   = Gopigo3.LED_BLINKER_RIGHT;
    static LED_WIFI            = 0x80;
    // Used to indicate WiFi status. Should not be controlled by the user.

    static SERVO_1             = 0x01;
    static SERVO_2             = 0x02;

    static MOTOR_LEFT          = 0x01;
    static MOTOR_RIGHT         = 0x02;

    static MOTOR_FLOAT         = -128;

    static GROVE_1_1           = 0x01;
    static GROVE_1_2           = 0x02;
    static GROVE_2_1           = 0x04;
    static GROVE_2_2           = 0x08;

    static GROVE_1             = Gopigo3.GROVE_1_1 + Gopigo3.GROVE_1_2;
    static GROVE_2             = Gopigo3.GROVE_2_1 + Gopigo3.GROVE_2_2;

    static GROVE_INPUT_DIGITAL          = 0;
    static GROVE_OUTPUT_DIGITAL         = 1;
    static GROVE_INPUT_DIGITAL_PULLUP   = 2;
    static GROVE_INPUT_DIGITAL_PULLDOWN = 3;
    static GROVE_INPUT_ANALOG           = 4;
    static GROVE_OUTPUT_PWM             = 5;
    static GROVE_INPUT_ANALOG_PULLUP    = 6;
    static GROVE_INPUT_ANALOG_PULLDOWN  = 7;

    static GROVE_LOW  = 0;
    static GROVE_HIGH = 1;

    GroveType = [0, 0];
    GroveI2CInBytes = [0, 0];

    constructor(addr = 8, detect = true) {
        try {
            Gopigo3.GPG_SPI = SPIDevice.openSync(0, 1, {
                'maxSpeedHz': Gopigo3.SPI_MAX_SPEED_HZ,
                'mode': Gopigo3.SPI_MODE,
                'bitsPerWord': Gopigo3.SPI_BITS_PER_WORD
            });
        } catch (err) {
            console.log(err);
            throw new Error(err);
        }

        /*
            Do any necessary configuration, and optionally detect the GoPiGo3
            * Optionally set the SPI address to something other than 8
            * Optionally disable the detection of the GoPiGo3 hardware.
            * This can be used for debugging
            and testing when the GoPiGo3 would otherwise not pass the detection tests.
        */

        Gopigo3.SPI_Address = addr;

        let manufacturer;
        let board;
        let vfw;

        if (detect) {
            try {
                manufacturer = this.getManufacturer();
                board = this.getBoard();
                vfw = this.getVersionFirmware();
                console.log(manufacturer, board, vfw);
            } catch (err) {
                console.log(err);
                throw new Error(`No SPI response. GoPiGo3 with address ${addr} not connected.`);
            }

            if (manufacturer !== 'Dexter Industries' || board !== 'GoPiGo3') {
                throw new Error(`GoPiGo3 with address ${addr} not connected.`);
            }

            if (
                vfw.split('.')[0] !== Gopigo3.FIRMWARE_VERSION_REQUIRED.split('.')[0]
                ||
                vfw.split('.')[1] !== Gopigo3.FIRMWARE_VERSION_REQUIRED.split('.')[1]
            ) {
                throw new FirmwareVersionError(`GoPiGo3 firmware needs to be version ${this.FIRMWARE_VERSION_REQUIRED} but is currently version ${vfw}`);
            }
        }
    }
    /**
     * Conduct a SPI transaction
     * Returns a list of the bytes read.
     * @param {*} data a list of bytes to send. The length of the list will
     * determine how many bytes are transferred.
     */
    spiTransferArray(data) {
        const dataBuff = new Buffer(data);
        const message = [{
            'sendBuffer': dataBuff,
            'receiveBuffer': new Buffer(data.length),
            'byteLength': dataBuff.byteLength,
            'chipSelectChange': false
        }];

        try {
            Gopigo3.GPG_SPI.transferSync(message);
        } catch (err) {
            console.log(err);
            throw new Error(err);
        }
        // console.log(message);
        return message[0].receiveBuffer || false;
    }
    /**
     * Read an 8-bit value over SPI
     * Returns touple:
     *  value, error
     * @param {*} messageType the SPI message type
     */
    spiRead8(messageType) {
        let output;
        const dataOut = [Gopigo3.SPI_Address, messageType, 0, 0, 0];
        const dataIn = this.spiTransferArray(dataOut);
        if (dataIn[3] === 0xA5) {
            output = parseInt(dataIn[4], 0);
        } else {
            throw new Error('No SPI response');
        }
        return output;
    }
    /**
     * Read a 16-bit value over SPI
     * Returns touple:
     * value, error
     * @param {*} messageType the SPI message type
     */
    spiRead16(messageType) {
        let output;
        const dataOut = [Gopigo3.SPI_Address, messageType, 0, 0, 0, 0];
        const dataIn = this.spiTransferArray(dataOut);
        if (dataIn[3] === 0xA5) {
            output = parseInt((dataIn[4] << 8) | dataIn[5], 0);
        } else {
            throw new Error('No SPI response');
        }
        return output;
    }
    /**
     * Read a 32-bit value over SPI
     * @param {*} messageType the SPI message type
     */
    spiRead32(messageType) {
        let out;
        const dataOut = [Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0, 0];
        const dataIn = this.spiTransferArray(dataOut);
        if (dataIn[3] === 0xA5) {
            out = parseInt(
                (dataIn[4] << 24) | (dataIn[5] << 16) | (dataIn[6] << 8) | dataIn[7], 0
            );
        } else {
            throw new Error('No SPI response');
        }
        return out;
    }
    /**
     * Send a 32-bit value over SPI
     * @param {*} messageType the SPI message type
     * @param {*} value the value to be sent
     */
    spiWrite32(messageType, value) {
        const dataOut = [
            Gopigo3.SPI_Address, messageType,
            ((value >> 24) & 0xFF),
            ((value >> 16) & 0xFF),
            ((value >> 8) & 0xFF),
            (value & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Read the 20 character GoPiGo3 manufacturer name

        Returns touple:
        GoPiGo3 manufacturer name string, error
     */
    getManufacturer() {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.GET_MANUFACTURER,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let name = '';

        if (dataIn[3] === 0xA5) {
            for (let i = 4, len = 24; i <= len; i++) {
                if (dataIn[i] !== 0) {
                    name += String.fromCharCode(dataIn[i]);
                } else  {
                    break;
                }
            }
        } else {
            throw new Error('No SPI response');
        }

        return name;
    }
    /**
     * Read the 20 character GoPiGo3 board name
     * Returns touple:
     * GoPiGo3 board name string, error
     */
    getBoard() {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.GET_NAME,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let name = '';

        if (dataIn[3] === 0xA5) {
            for (let i = 4, len = 24; i <= len; i++) {
                if (dataIn[i] !== 0) {
                    name += String.fromCharCode(dataIn[i]);
                } else  {
                    break;
                }
            }
        } else {
            throw new Error('No SPI response');
        }

        return name;
    }
    /**
     * Read the hardware version
     * Returns touple:
     * hardware version, error
     */
    getVersionHardware() {
        const version = this.spiRead32(Gopigo3.SPI_MESSAGE_TYPE.GET_HARDWARE_VERSION);
        const major = parseInt(version / 1000000, 0);
        const minor = parseInt((version / 1000) % 1000, 0);
        const patch = parseInt(version % 1000, 0);
        return `${major}.${minor}.${patch}`;
    }
    /**
     * Read the firmware version
     * Returns touple:
     * firmware version, error
     */
    getVersionFirmware() {
        const version = this.spiRead32(Gopigo3.SPI_MESSAGE_TYPE.GET_FIRMWARE_VERSION);
        const major = parseInt(version / 1000000, 0);
        const minor = parseInt((version / 1000) % 1000, 0);
        const patch = parseInt(version % 1000, 0);
        return `${major}.${minor}.${patch}`;
    }
    /**
     * Read the 128-bit GoPiGo3 hardware serial number
     * Returns touple:
     * serial number as 32 char HEX formatted string, error
     */
    getId() {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.GET_ID,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let id = '';

        if (dataIn[3] === 0xA5) {
            for (let i = 4, len = 19; i <= len; i++) {
                id += Utils.twoDigitHex(dataIn[i]);
            }
        } else {
            throw new Error('No SPI response');
        }

        return id;
    }
    /**
     * Set a LED
     * @param {*} led The LED(s). LED_LEFT_EYE, LED_RIGHT_EYE,
     * LED_LEFT_BLINKER, LED_RIGHT_BLINKER, and/or LED_WIFI.
     * @param {*} red The LED's Red color component (0-255)
     * @param {*} green The LED's Green color component (0-255)
     * @param {*} blue The LED's Blue color component (0-255)
     */
    setLed(led, red, green = 0, blue = 0) {
        if (led < 0 || led > 255) {
            return;
        }

        red = red > 255 ? 255 : red;
        green = green > 255 ? 255 : green;
        blue = blue > 255 ? 255 : blue;
        red = red < 0 ? 0 : red;
        green = green < 0 ? 0 : green;
        blue = blue < 0 ? 0 : blue;

        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_LED,
            led, red, green, blue
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Get the 5v circuit voltage
     *
     * Returns touple:
     * 5v circuit voltage, error
     */
    getVoltage5v() {
        const value = this.spiRead16(Gopigo3.SPI_MESSAGE_TYPE.GET_VOLTAGE_5V);
        return (value / 1000.0);
    }
    /**
     * Get the battery voltage
     * Returns touple:
     * battery voltage, error
     */
    getVoltageBattery() {
        const value = this.spiRead16(Gopigo3.SPI_MESSAGE_TYPE.GET_VOLTAGE_VCC);
        return (value / 1000.0);
    }
    /**
     * Set a servo position in microseconds
     * @param {*} servo The servo(s). SERVO_1 and/or SERVO_2.
     * @param {*} us The pulse width in microseconds (0-16666)
     */
    setServo(servo, us) {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_SERVO,
            servo, ((us >> 8) & 0xFF), (us & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set the motor power in percent
     * @param {*} port The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param {*} power The PWM power from -100 to 100, or MOTOR_FLOAT for float.
     */
    setMotorPower(port, power) {
        power = power > 127 ? 127 : power;
        power = power < 128 ? 128 : power;
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_MOTOR_PWM,
            port, parseInt(power, 0)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set the motor target position in degrees
     * @param {*} port The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param {*} position The target position
     */
    setMotorPosition(port, position) {
        const positionRaw = parseInt(position * Gopigo3.MOTOR_TICKS_PER_DEGREE, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_MOTOR_POSITION,
            parseInt(port, 0),
            ((positionRaw >> 24) & 0xFF), ((positionRaw >> 16) & 0xFF),
            ((positionRaw >> 8) & 0xFF), (positionRaw & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set the motor target speed in degrees per second
     * @param {*} port The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param {*} dps The target speed in degrees per second
     */
    setMotorDps(port, dps) {
        dps = parseInt(dps * Gopigo3.MOTOR_TICKS_PER_DEGREE, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_MOTOR_DPS,
            parseInt(port, 0),
            ((dps >> 8) & 0xFF),
            (dps & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set the motor speed limit
     * @param {*} port The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param {*} power The power limit in percent (0 to 100), with 0 being no limit (100)
     * @param {*} dps The speed limit in degrees per second, with 0 being no limit
     */
    setMotorLimits(port, power = 0, dps = 0) {
        dps = parseInt(dps * Gopigo3.MOTOR_TICKS_PER_DEGREE, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_MOTOR_LIMITS,
            parseInt(port, 0),
            power,
            ((dps >> 8) & 0xFF),
            (dps & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Read a motor status
     * Returns a list:
     *      flags -- 8-bits of bit-flags that indicate motor status:
     *         bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically
     *                  disabled because the battery voltage is too low
     *         bit 1 -- OVERLOADED - The motors aren't close to the target
     *                  (applies to position control and dps speed control).
     *     power -- the raw PWM power in percent (-100 to 100)
     *     encoder -- The encoder position
     *     dps -- The current speed in Degrees Per Second
     * @param {*} port The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
     */
    getMotorStatus(port) {
        let output;
        let messageType;
        let encoder;
        let dps;
        let power;

        if (port === Gopigo3.MOTOR_LEFT) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_LEFT;
        } else if (port === Gopigo3.MOTOR_RIGHT) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_RIGHT;
        } else {
            throw new Error('getMotorStatus error. Must be one motor port at a time. MOTOR_LEFT or MOTOR_RIGHT.');
        }

        const dataOut = [
            Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);

        if (dataIn[3] === 0xA5) {
            power = parseInt(dataIn[5], 0);
            if (power & 0x80) {
                power -= 0x100;
            }

            encoder = parseInt(
                (dataIn[6] << 24) | (dataIn[7] << 16) | (dataIn[8] << 8) | dataIn[9], 0
            );
            if (encoder & 0x80000000) {
                encoder = parseInt(encoder - 0x100000000, 0);
            }

            dps = parseInt((dataIn[10] << 8) | dataIn[11], 0);
            if (dps & 0x8000) {
                dps -= 0x10000;
            }

            output = [
                dataIn[4], power,
                parseInt(encoder / Gopigo3.MOTOR_TICKS_PER_DEGREE, 0),
                parseInt(dps / Gopigo3.MOTOR_TICKS_PER_DEGREE, 0)
            ];
        } else {
            throw new Error('No SPI response');
        }

        return output;
    }
    /**
     * Read a motor encoder in degrees
     * Returns the encoder position in degrees
     * @param {*} port The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
     */
    getMotorEncoder(port) {
        let messageType;

        if (port === Gopigo3.MOTOR_LEFT) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_LEFT;
        } else if (port === Gopigo3.MOTOR_RIGHT) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_MOTOR_STATUS_RIGHT;
        } else {
            throw new Error('getMotorEncoder error. Must be one motor port at a time. MOTOR_LEFT or MOTOR_RIGHT.');
        }

        let encoder = this.spiRead32(messageType);
        if (encoder & 0x80000000) {
            encoder = parseInt(encoder - 0x100000000, 0);
        }

        return parseInt(encoder / Gopigo3.MOTOR_TICKS_PER_DEGREE, 0);
    }
    /**
     * Offset a motor encoder
     * @param {*} port The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param {*} offset The encoder offset
     */
    offsetMotorEncoder(port, offset) {
        offset = parseInt(offset * Gopigo3.MOTOR_TICKS_PER_DEGREE, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.OFFSET_MOTOR_ENCODER,
            parseInt(port, 0),
            ((offset >> 24) & 0xFF),
            ((offset >> 16) & 0xFF),
            ((offset >> 8) & 0xFF),
            (offset & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set grove type
     * @param {*} port The grove port(s). GROVE_1 and/or GROVE_2.
     * @param {*} type The grove device type
     */
    setGroveType(port, type) {
        for (let i = 0, len = 2; i < len; i++) {
            if ((port >> (i * 2)) & 3 === 3) {
                this.GroveType[i] = type;
            }
        }
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_GROVE_TYPE,
            parseInt(port, 0), type
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set grove analog digital pin mode as INPUT/OUTPUT
     * @param {*} pin The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
     * @param {*} mode The pin mode. GROVE_INPUT_DIGITAL, GROVE_OUTPUT_DIGITAL,
     *                 GROVE_INPUT_DIGITAL_PULLUP, GROVE_INPUT_DIGITAL_PULLDOWN, GROVE_INPUT_ANALOG,
     *                 GROVE_OUTPUT_PWM, GROVE_INPUT_ANALOG_PULLUP, or GROVE_INPUT_ANALOG_PULLDOWN.
     */
    setGroveMode(pin, mode) {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_GROVE_MODE,
            pin, mode
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set grove output pin LOW/HIGH
     * @param {*} pin The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
     * @param {*} state The pin state. GROVE_LOW or GROVE_HIGH.
     */
    setGroveState(pin, state) {
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_GROVE_STATE,
            pin, state
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set grove output pin PWM
     * @param {*} pin The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
     * @param {*} duty The PWM duty cycle in percent. Floating point.
     */
    setGrovePwmDuty(pin, duty) {
        duty = duty < 0 ? 0 : duty;
        duty = duty > 100 ? 100 : duty;
        const dutyValue = parseInt(duty * 10.0, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_GROVE_PWM_DUTY, pin,
            ((dutyValue >> 8) & 0xFF), (dutyValue & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Set grove PWM frequency
     * @param {*} port The grove port(s). GROVE_1 and/or GROVE_2.
     * @param {*} freq The PWM frequency. Range is 3 through 48000Hz. Default is 24000 (24kHz).
     */
    setGrovePwmFrequency(port, freq = 24000) {
        freq = freq < 3 ? 3 : freq;
        freq = freq > 48000 ? 48000 : freq;
        // Make sure it doesn't exceed 16 bit unsigned.
        // Limit to 48000, which is the highest frequency supported for 0.1% resolution.
        const freqValue = parseInt(freq, 0);
        const dataOut = [
            Gopigo3.SPI_Address, Gopigo3.SPI_MESSAGE_TYPE.SET_GROVE_PWM_FREQUENCY,
            parseInt(port, 0),
            ((freqValue >> 8) & 0xFF),
            (freqValue & 0xFF)
        ];
        this.spiTransferArray(dataOut);
    }
    /**
     * Conduct an I2C transaction
     * Returns:
     * list of bytes read from the slave
     * @param {*} port The grove port. GROVE_1 or GROVE_2.
     * @param {*} addr The I2C address of the slave to be addressed.
     * @param {*} outArr A list of bytes to send.
     * @param {*} inBytes The number of bytes to read.
     */
    groveI2cTransfer(port, addr, outArr, inBytes = 0) {
        // Start an I2C transaction as soon as the bus is available

        let timeout = new Date().getTime() + 5; // + 0.005;
        // Timeout after 5ms of failed attempted starts
        let check = false;
        let delayTime = 0;
        let values;

        while (!check) {
            try {
                this.groveI2cStart(port, addr, outArr, inBytes);
                check = true;
            } catch (err) {
                console.log(err);
                const now = new Date().getTime();
                if (now > timeout) {
                    throw new I2CError('groveI2cTransfer error: Timeout trying to start transaction');
                }
            }
        }

        if (outArr.length) {
            delayTime += 1 + outArr.length;
        }
        if (inBytes) {
            delayTime += 1 + inBytes;
        }
        delayTime *= 115; // (0.000115);
        // Each I2C byte takes about 115uS at full speed (about 100kbps)
        // No point trying to read the values before they are ready.
        sleep.usleep(delayTime);
        // Delay for as long as it will take to do the I2C transaction.

        timeout = new Date().getTime() + 5; // 0.005;
        // Timeout after 5ms of failed attempted reads

        while (true) {
            try {
                // Read the results as soon as they are available
                values = this.getGroveValue(port);
            } catch (err) {
                console.log(err);
                if (new Date().getTime() > timeout) {
                    throw new ValueError('groveI2cTransfer error: Timeout waiting for data');
                }
            }
            return values;
        }
    }
    /**
     * Start an I2C transaction
     * @param {*} port The grove port. GROVE_1 or GROVE_2.
     * @param {*} addr The I2C address of the slave to be addressed.
     * @param {*} outArr A list of bytes to send.
     * @param {*} inBytes The number of bytes to read.
     */
    groveI2cStart(port, addr, outArr, inBytes = 0) {
        let messageType;
        let portIndex;

        if (port === Gopigo3.GROVE_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.START_GROVE_I2C_1;
            portIndex = 0;
        } else if (port === Gopigo3.GROVE_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.START_GROVE_I2C_2;
            portIndex = 1;
        } else {
            throw new Error('Port unsupported. Must get one at a time.');
        }

        const address = ((parseInt(addr, 0) & 0x7F) << 1);
        if (inBytes > Gopigo3.GROVE_I2C_LENGTH_LIMIT) {
            throw new Error(`Read length error. Up to ${this.GROVE_I2C_LENGTH_LIMIT} bytes can be read in a single transaction.`);
        }

        const outBytes = outArr.length;
        if (outBytes > Gopigo3.GROVE_I2C_LENGTH_LIMIT) {
            throw new Error(`Write length error. Up to ${this.GROVE_I2C_LENGTH_LIMIT} bytes can be read in a single transaction.`);
        }

        const dataOut = [
            Gopigo3.SPI_Address, messageType, address, inBytes, outBytes
        ];
        dataOut.concat(outArr);

        const dataIn = this.spiTransferArray(dataOut);

        this.GroveI2CInBytes[portIndex] = inBytes;

        if (dataIn[3] !== 0xA5) {
            throw new Error('No SPI response');
        }
        if (dataIn[4] !== 0) {
            throw new I2CError('groveI2cStart error: Not ready to start I2C transaction');
        }
    }
    /**
     * Get a grove port value
     * @param {*} port The grove port. GROVE_1 or GROVE_2.
     */
    getGroveValue(port) {
        let output;
        let messageType;
        let portIndex;
        let dataOut;
        let dataIn;

        if (port === Gopigo3.GROVE_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_1;
            portIndex = 0;
        } else if (port === Gopigo3.GROVE_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VALUE_2;
            portIndex = 1;
        } else {
            throw new Error('Port unsupported. Must get one at a time.');
        }

        if (this.GroveType[portIndex] === Gopigo3.GROVE_TYPE.IR_DI_REMOTE) {
            dataOut = [
                Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0
            ];
            dataIn = this.spiTransferArray(dataOut);
            if (dataIn[3] === 0xA5) {
                if (dataIn[4] === this.GroveType[portIndex] && dataIn[5] === 0) {
                    output = dataIn[6];
                } else {
                    console.log('IR DI REMOTE', dataIn);
                    throw new SensorError('getGroveValue error: Invalid value');
                }
            } else {
                throw new Error('getGroveValue error: No SPI response');
            }
        } else if (this.GroveType[portIndex] === Gopigo3.GROVE_TYPE.IR_EV3_REMOTE) {
            dataOut = [
                Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0, 0, 0, 0
            ];
            dataIn = this.spiTransferArray(dataOut);
            if (dataIn[3] === 0xA5) {
                if (dataIn[4] === this.GroveType[portIndex] && dataIn[5] === 0) {
                    output = [
                        dataIn[6], dataIn[7], dataIn[8], dataIn[9]
                    ];
                } else {
                    console.log('IR EV3 REMOTE', dataIn);
                    throw new SensorError('getGroveValue error: Invalid value');
                }
            } else {
                throw new Error('getGroveValue error: No SPI response');
            }
        } else if (this.GroveType[portIndex] === Gopigo3.GROVE_TYPE.US) {
            dataOut = [
                Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0, 0
            ];
            dataIn = this.spiTransferArray(dataOut);
            if (dataIn[3] === 0xA5) {
                if (dataIn[4] === this.GroveType[portIndex] && dataIn[5] === 0) {
                    const value = (((dataIn[6] << 8) & 0xFF00) | (dataIn[7] & 0xFF));
                    if (value === 0) {
                        throw new SensorError('getGroveValue error: Sensor not responding');
                    } else if (value === 1) {
                        throw new ValueError('getGroveValue error: Object not detected within range');
                    } else {
                        output = value;
                    }
                } else {
                    console.log('US', dataIn);
                    throw new SensorError('getGroveValue error: Invalid value');
                }
            } else {
                throw new Error('getGroveValue error: No SPI response');
            }
        } else if (this.GroveType[portIndex] === Gopigo3.GROVE_TYPE.I2C) {
            dataOut = [
                Gopigo3.SPI_Address, messageType, 0, 0, 0, 0
            ];
            for (let i = 0, len = this.GroveI2CInBytes[portIndex]; i < len; i++) {
                dataOut.push(0);
            }

            dataIn = this.spiTransferArray(dataOut);
            if (dataIn[3] === 0xA5) {
                if (dataIn[4] === this.GroveType[portIndex]) {
                    if (dataIn[5] === Gopigo3.GROVE_STATE.VALID_DATA) {
                        output = dataIn[6];
                    } else if (dataIn[5] === Gopigo3.GROVE_STATE.I2C_ERROR) {
                        throw new I2CError('getGroveValue error: I2C bus error');
                    } else {
                        console.log('I2C', dataIn);
                        console.log('check type', dataIn[4], this.GroveType[portIndex]);
                        console.log('valid data', dataIn[5], Gopigo3.GROVE_STATE.VALID_DATA);
                        console.log('I2C error', dataIn[5], Gopigo3.GROVE_STATE.I2C_ERROR);
                        throw new ValueError('getGroveValue error: Invalid value');
                    }
                } else {
                    throw new SensorError('getGroveValue error: Grove type mismatch');
                }
            } else {
                throw new Error('getGroveValue error: No SPI response');
            }
        }

        return output || this.spiRead8(messageType);
    }
    /**
     * Get a grove input pin state
     * @param {*} pin The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
     */
    getGroveState(pin) {
        let messageType;

        if (pin === Gopigo3.GROVE_1_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_STATE_1_1;
        } else if (pin === Gopigo3.GROVE_1_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_STATE_1_2;
        } else if (pin === Gopigo3.GROVE_2_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_STATE_2_1;
        } else if (pin === Gopigo3.GROVE_2_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_STATE_2_2;
        } else {
            throw new Error('Pin(s) unsupported. Must get one at a time.');
        }

        const dataOut = [
            Gopigo3.SPI_Address, messageType, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let output;

        if (dataIn[3] === 0xA5) {
            if (dataIn[4] === Gopigo3.GROVE_STATE.VALID_DATA) {
                output = dataIn[5];
            } else {
                console.log('GROVE STATE', dataIn);
                throw new ValueError('getGroveState error: Invalid value');
            }
        } else {
            throw new Error('getGroveState error: No SPI response');
        }

        return output;
    }
    /**
     * Get a grove input pin analog voltage
     * @param {*} pin The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
     */
    getGroveVoltage(pin) {
        let messageType;

        if (pin === Gopigo3.GROVE_1_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_1_1;
        } else if (pin === Gopigo3.GROVE_1_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_1_2;
        } else if (pin === Gopigo3.GROVE_2_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_2_1;
        } else if (pin === Gopigo3.GROVE_2_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_VOLTAGE_2_2;
        } else {
            throw new Error('Pin(s) unsupported. Must get one at a time.');
        }

        const dataOut = [
            Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let output;

        if (dataIn[3] === 0xA5) {
            if (dataIn[4] === Gopigo3.GROVE_STATE.VALID_DATA) {
                output = ((((dataIn[5] << 8) & 0xFF00) | (dataIn[6] & 0xFF)) / 1000.0);
            } else {
                console.log('GROVE VOLTAGE', dataIn);
                throw new ValueError('getGroveVoltage error: Invalid value');
            }
        } else {
            throw new Error('getGroveVoltage error: No SPI response');
        }

        return output;
    }
    /**
     * Get a grove input pin 12-bit raw ADC reading
     * @param {*} pin The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
     */
    getGroveAnalog(pin) {
        let messageType;

        if (pin === Gopigo3.GROVE_1_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_1_1;
        } else if (pin === Gopigo3.GROVE_1_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_1_2;
        } else if (pin === Gopigo3.GROVE_2_1) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_2_1;
        } else if (pin === Gopigo3.GROVE_2_2) {
            messageType = Gopigo3.SPI_MESSAGE_TYPE.GET_GROVE_ANALOG_2_2;
        } else {
            throw new Error('Pin(s) unsupported. Must get one at a time.');
        }

        const dataOut = [
            Gopigo3.SPI_Address, messageType, 0, 0, 0, 0, 0
        ];
        const dataIn = this.spiTransferArray(dataOut);
        let output;

        if (dataIn[3] === 0xA5) {
            if (dataIn[4] === Gopigo3.GROVE_STATE.VALID_DATA) {
                output = (((dataIn[5] << 8) & 0xFF00) | (dataIn[6] & 0xFF));
            } else {
                console.log('GROVE ANALOG', dataIn);
                throw new ValueError('getGroveAnalog error: Invalid value');
            }
        } else {
            throw new Error('getGroveAnalog error: No SPI response');
        }

        return output;
    }
    /**
     * Reset the GoPiGo3.
     */
    resetAll() {
        // Reset all sensors
        this.setGroveType(Gopigo3.GROVE_1 + Gopigo3.GROVE_2, Gopigo3.GROVE_TYPE.CUSTOM);
        this.setGroveMode(Gopigo3.GROVE_1 + Gopigo3.GROVE_2, Gopigo3.GROVE_INPUT_DIGITAL);

        // Turn off the motors
        this.setMotorPower(Gopigo3.MOTOR_LEFT + Gopigo3.MOTOR_RIGHT, Gopigo3.MOTOR_FLOAT);

        // Reset the motor limits
        this.setMotorLimits(Gopigo3.MOTOR_LEFT + Gopigo3.MOTOR_RIGHT, 0, 0);

        // Turn off the servos
        this.setServo(Gopigo3.SERVO_1 + Gopigo3.SERVO_2, 0);

        // Turn off the LEDs
        this.setLed(
            Gopigo3.LED_EYE_LEFT + Gopigo3.LED_EYE_RIGHT + Gopigo3.LED_BLINKER_LEFT + Gopigo3.LED_BLINKER_RIGHT,
            0, 0, 0
        );
    }
}

module.exports = Gopigo3;
