/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  Public definitions used for the C++ drivers for the GoPiGo3
 */

#ifndef GOPIGOCOMMON_H_INCLUDED
#define GOPIGOCOMMON_H_INCLUDED

#define FIRMWARE_VERSION_REQUIRED "0.3." // Firmware version needs to start with this
#define LONGEST_I2C_TRANSFER 16 // longest possible I2C read/write
#define LONGEST_SPI_TRANSFER 24 // spi_read_string 20 chars (LONGEST_I2C_TRANSFER + 6) // longest possible message for configuring for an I2C sensor
#define SPI_TARGET_SPEED 500000 // SPI target speed of 500kbps


#include <stdint.h>

/// Error values, returned from functions.
#define ERROR_NONE                  0
#define ERROR_SPI_FILE             -1
#define ERROR_SPI_RESPONSE         -2
#define ERROR_WRONG_MANUFACTURER   -3
#define ERROR_WRONG_DEVICE         -4
#define ERROR_FIRMWARE_MISMATCH    -5
#define ERROR_GROVE_TYPE_MISMATCH  -6
#define ERROR_GROVE_DATA_ERROR     -7


/// LED Set values.
#define LED_EYE_LEFT      0x02
#define LED_EYE_RIGHT     0x01
#define LED_BLINKER_LEFT  0x04
#define LED_BLINKER_RIGHT 0x08
#define LED_LEFT_EYE      LED_EYE_LEFT
#define LED_RIGHT_EYE     LED_EYE_RIGHT
#define LED_LEFT_BLINKER  LED_BLINKER_LEFT
#define LED_RIGHT_BLINKER LED_BLINKER_RIGHT
#define LED_WIFI          0x80 // Used to indicate WiFi status. Should not be controlled by the user.

/// Servo ports
#define SERVO_1 0x01
#define SERVO_2 0x02

/// Motor ports
#define MOTOR_LEFT  0x01
#define MOTOR_RIGHT 0x02

/// Motor Float. Value to pass to set_motor_power to make a motor float.
#define MOTOR_FLOAT -128

///Grove Ports
#define GROVE_1_1 0x01
#define GROVE_1_2 0x02
#define GROVE_2_1 0x04
#define GROVE_2_2 0x08


///GROVE TYPES
#define GROVE_1 (GROVE_1_1 + GROVE_1_2)
#define GROVE_2 (GROVE_2_1 + GROVE_2_2)

/// Grove pin configurations
#define INPUT_DIGITAL 0
#define OUTPUT_DIGITAL 1
#define INPUT_DIGITAL_PULLUP 2
#define INPUT_DIGITAL_PULLDOWN 3
#define INPUT_ANALOG 4
#define OUTPUT_PWM 5
#define INPUT_ANALOG_PULLUP 6
#define INPUT_ANALOG_PULLDOWN 7

/// Message types for use in spi data calls.
enum GPGSPI_MESSAGE_TYPE{
  GPGSPI_MESSAGE_NONE,

  GPGSPI_MESSAGE_GET_MANUFACTURER,
  GPGSPI_MESSAGE_GET_NAME,
  GPGSPI_MESSAGE_GET_HARDWARE_VERSION,
  GPGSPI_MESSAGE_GET_FIRMWARE_VERSION,
  GPGSPI_MESSAGE_GET_ID,

  GPGSPI_MESSAGE_SET_LED,

  GPGSPI_MESSAGE_GET_VOLTAGE_5V,
  GPGSPI_MESSAGE_GET_VOLTAGE_VCC,

  GPGSPI_MESSAGE_SET_SERVO,

  GPGSPI_MESSAGE_SET_MOTOR_PWM,

  GPGSPI_MESSAGE_SET_MOTOR_POSITION,
  GPGSPI_MESSAGE_SET_MOTOR_POSITION_KP,
  GPGSPI_MESSAGE_SET_MOTOR_POSITION_KD,

  GPGSPI_MESSAGE_SET_MOTOR_DPS,

  GPGSPI_MESSAGE_SET_MOTOR_LIMITS,

  GPGSPI_MESSAGE_OFFSET_MOTOR_ENCODER,

  GPGSPI_MESSAGE_GET_MOTOR_ENCODER_LEFT,
  GPGSPI_MESSAGE_GET_MOTOR_ENCODER_RIGHT,

  GPGSPI_MESSAGE_GET_MOTOR_STATUS_LEFT,
  GPGSPI_MESSAGE_GET_MOTOR_STATUS_RIGHT,

  GPGSPI_MESSAGE_SET_GROVE_TYPE,
  GPGSPI_MESSAGE_SET_GROVE_MODE,
  GPGSPI_MESSAGE_SET_GROVE_STATE,
  GPGSPI_MESSAGE_SET_GROVE_PWM_DUTY,
  GPGSPI_MESSAGE_SET_GROVE_PWM_FREQUENCY,

  GPGSPI_MESSAGE_GET_GROVE_VALUE_1,
  GPGSPI_MESSAGE_GET_GROVE_VALUE_2,
  GPGSPI_MESSAGE_GET_GROVE_STATE_1_1,
  GPGSPI_MESSAGE_GET_GROVE_STATE_1_2,
  GPGSPI_MESSAGE_GET_GROVE_STATE_2_1,
  GPGSPI_MESSAGE_GET_GROVE_STATE_2_2,
  GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_1,
  GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_2,
  GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_1,
  GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_2,
  GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_1,
  GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_2,
  GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_1,
  GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_2,

  GPGSPI_MESSAGE_START_GROVE_I2C_1,
  GPGSPI_MESSAGE_START_GROVE_I2C_2
};

/// Possible grove states.
enum GROVE_STATE {LOW = 0, HIGH = 1};

/// structure for I2C transactions
struct i2c_struct_t{
  uint8_t address;
  uint8_t length_write;
  uint8_t buffer_write[LONGEST_I2C_TRANSFER];
  uint8_t length_read;
  uint8_t buffer_read[LONGEST_I2C_TRANSFER];
};

/// structure for ultrasonic sensor
struct sensor_ultrasonic_t{
  uint16_t mm;
  float    cm;
  float    inch;
};

/// structure for infrared sensor configured for Go Box remote
struct sensor_infrared_gobox_t{
  uint8_t  button;
};

/// structure for infrared sensor configured for EV3 remote
struct sensor_infrared_ev3_t{
  uint8_t  remote[4];
};

#endif // GOPIGOCOMMON_H_INCLUDED
