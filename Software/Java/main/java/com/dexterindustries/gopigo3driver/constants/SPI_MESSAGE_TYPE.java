package com.dexterindustries.gopigo3driver.constants;
/**
 * This list is based on the enumerations found in the C version of this code.
 * It needs to be re-organized.
 *
 * https://www.dexterindustries.com/GoPiGo3/
 * https://github.com/DexterInd/GoPiGo3
 *
 * Portions Copyright (c) 2017 Dexter Industries Released under the MIT license
 * (http://choosealicense.com/licenses/mit/). For more information see
 * https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 * @author Ken Fogel
 */
public final class SPI_MESSAGE_TYPE {

    private SPI_MESSAGE_TYPE() {
    }

    public static final byte ADDRESS = 8;

    public static final byte NONE = 0;

    public static final byte GET_MANUFACTURER = 1;

    public static final byte GET_NAME = 2;
    public static final byte GET_HARDWARE_VERSION = 3;
    public static final byte GET_FIRMWARE_VERSION = 4;
    public static final byte GET_ID = 5;

    public static final byte SET_LED = 6;

    public static final byte GET_VOLTAGE_5V = 7;
    public static final byte GET_VOLTAGE_VCC = 8;

    public static final byte SET_SERVO = 9;

    public static final byte SET_MOTOR_PWM = 10;

    public static final byte SET_MOTOR_POSITION = 11;
    public static final byte SET_MOTOR_POSITION_KP = 12;
    public static final byte SET_MOTOR_POSITION_KD = 13;

    public static final byte SET_MOTOR_DPS = 14;

    public static final byte SET_MOTOR_LIMITS = 15;

    public static final byte OFFSET_MOTOR_ENCODER = 16;

    public static final byte GET_MOTOR_ENCODER_LEFT = 17;
    public static final byte GET_MOTOR_ENCODER_RIGHT = 18;

    public static final byte GET_MOTOR_STATUS_LEFT = 19;
    public static final byte GET_MOTOR_STATUS_RIGHT = 20;

    public static final byte SET_GROVE_TYPE = 21;
    public static final byte SET_GROVE_MODE = 22;
    public static final byte SET_GROVE_STATE = 23;
    public static final byte SET_GROVE_PWM_DUTY = 24;
    public static final byte SET_GROVE_PWM_FREQUENCY = 25;

    public static final byte GET_GROVE_VALUE_1 = 26;
    public static final byte GET_GROVE_VALUE_2 = 27;
    public static final byte GET_GROVE_STATE_1_1 = 28;
    public static final byte GET_GROVE_STATE_1_2 = 29;
    public static final byte GET_GROVE_STATE_2_1 = 30;
    public static final byte GET_GROVE_STATE_2_2 = 31;
    public static final byte GET_GROVE_VOLTAGE_1_1 = 32;
    public static final byte GET_GROVE_VOLTAGE_1_2 = 33;
    public static final byte GET_GROVE_VOLTAGE_2_1 = 34;
    public static final byte GET_GROVE_VOLTAGE_2_2 = 35;
    public static final byte GET_GROVE_ANALOG_1_1 = 36;
    public static final byte GET_GROVE_ANALOG_1_2 = 37;
    public static final byte GET_GROVE_ANALOG_2_1 = 38;
    public static final byte GET_GROVE_ANALOG_2_2 = 39;

    public static final byte START_GROVE_I2C_1 = 40;
    public static final byte START_GROVE_I2C_2 = 41;

    public static final byte LED_EYE_LEFT = 0x02;
    public static final byte LED_EYE_RIGHT = 0x01;
    public static final byte LED_BLINKER_LEFT = 0x04;
    public static final byte LED_BLINKER_RIGHT = 0x08;
    public static final byte LED_LEFT_EYE = LED_EYE_LEFT;
    public static final byte LED_RIGHT_EYE = LED_EYE_RIGHT;
    public static final byte LED_LEFT_BLINKER = LED_BLINKER_LEFT;
    public static final byte LED_RIGHT_BLINKER = LED_BLINKER_RIGHT;
    //public static final byte LED_WIFI = 0x80; // Used to indicate WiFi status. Should not be controlled by the user.

    public static final byte SERVO_1 = 0x01;
    public static final byte SERVO_2 = 0x02;

    public static final byte MOTOR_LEFT = 0x01;
    public static final byte MOTOR_RIGHT = 0x02;
    public static final byte MOTOR_BOTH = 0x03;

    public static final byte MOTOR_FLOAT = -128;

    public static final byte GROVE_1_1 = 0x01;
    public static final byte GROVE_1_2 = 0x02;
    public static final byte GROVE_2_1 = 0x04;
    public static final byte GROVE_2_2 = 0x08;

    public static final byte GROVE_1 = GROVE_1_1 + GROVE_1_2;
    public static final byte GROVE_2 = GROVE_2_1 + GROVE_2_2;

    //public static final byte GroveType[] = {0, 0};
    //public static final byte GroveI2CInBytes[] = {0, 0};
    public static final byte GROVE_INPUT_DIGITAL = 0;
    public static final byte GROVE_OUTPUT_DIGITAL = 1;
    public static final byte GROVE_INPUT_DIGITAL_PULLUP = 2;
    public static final byte GROVE_INPUT_DIGITAL_PULLDOWN = 3;
    public static final byte GROVE_INPUT_ANALOG = 4;
    public static final byte GROVE_OUTPUT_PWM = 5;
    public static final byte GROVE_INPUT_ANALOG_PULLUP = 6;
    public static final byte GROVE_INPUT_ANALOG_PULLDOWN = 7;

    public static final byte GROVE_LOW = 0;
    public static final byte GROVE_HIGH = 1;

    public static final byte LONGEST_I2C_TRANSFER = 32; // longest possible I2C read/write
    public static final byte LONGEST_SPI_TRANSFER = (LONGEST_I2C_TRANSFER + 6); // at least 24

    public static final byte GROVE_TYPE_US = 4;

    public static final byte GPGSPI_MESSAGE_NONE = 0;
    public static final byte GPGSPI_MESSAGE_GET_MANUFACTURER = 1;

    public static final byte GPGSPI_MESSAGE_GET_NAME = 2;
    public static final byte GPGSPI_MESSAGE_GET_HARDWARE_VERSION = 3;
    public static final byte GPGSPI_MESSAGE_GET_FIRMWARE_VERSION = 4;
    public static final byte GPGSPI_MESSAGE_GET_ID = 5;

    public static final byte GPGSPI_MESSAGE_SET_LED = 6;

    public static final byte GPGSPI_MESSAGE_GET_VOLTAGE_5V = 7;
    public static final byte GPGSPI_MESSAGE_GET_VOLTAGE_VCC = 8;

    public static final byte GPGSPI_MESSAGE_SET_SERVO = 9;

    public static final byte GPGSPI_MESSAGE_SET_MOTOR_PWM = 10;

    public static final byte GPGSPI_MESSAGE_SET_MOTOR_POSITION = 11;
    public static final byte GPGSPI_MESSAGE_SET_MOTOR_POSITION_KP = 12;
    public static final byte GPGSPI_MESSAGE_SET_MOTOR_POSITION_KD = 13;

    public static final byte GPGSPI_MESSAGE_SET_MOTOR_DPS = 14;

    public static final byte GPGSPI_MESSAGE_SET_MOTOR_LIMITS = 15;

    public static final byte GPGSPI_MESSAGE_OFFSET_MOTOR_ENCODER = 16;

    public static final byte GPGSPI_MESSAGE_GET_MOTOR_ENCODER_LEFT = 17;
    public static final byte GPGSPI_MESSAGE_GET_MOTOR_ENCODER_RIGHT = 18;

    public static final byte GPGSPI_MESSAGE_GET_MOTOR_STATUS_LEFT = 19;
    public static final byte GPGSPI_MESSAGE_GET_MOTOR_STATUS_RIGHT = 20;

    public static final byte GPGSPI_MESSAGE_SET_GROVE_TYPE = 21;
    public static final byte GPGSPI_MESSAGE_SET_GROVE_MODE = 22;
    public static final byte GPGSPI_MESSAGE_SET_GROVE_STATE = 23;
    public static final byte GPGSPI_MESSAGE_SET_GROVE_PWM_DUTY = 24;
    public static final byte GPGSPI_MESSAGE_SET_GROVE_PWM_FREQUENCY = 25;

    public static final byte GPGSPI_MESSAGE_GET_GROVE_VALUE_1 = 26;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_VALUE_2 = 27;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_STATE_1_1 = 28;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_STATE_1_2 = 29;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_STATE_2_1 = 30;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_STATE_2_2 = 31;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_1 = 32;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_2 = 33;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_1 = 34;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_2 = 35;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_1 = 36;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_2 = 37;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_1 = 38;
    public static final byte GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_2 = 39;

    public static final byte GPGSPI_MESSAGE_START_GROVE_I2C_1 = 40;
    public static final byte GPGSPI_MESSAGE_START_GROVE_I2C_2 = 41;

    public static final int ERROR_NONE = 0;
    public static final int ERROR_SPI_FILE = -1;
    public static final int ERROR_SPI_RESPONSE = -2;
    public static final int ERROR_WRONG_MANUFACTURER = -3;
    public static final int ERROR_WRONG_DEVICE = -4;
    public static final int ERROR_FIRMWARE_MISMATCH = -5;
    public static final int ERROR_GROVE_TYPE_MISMATCH = -6;
    public static final int ERROR_GROVE_DATA_ERROR = -7;

}
