/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  C++ drivers for the GoPiGo3
 */

#ifndef GoPiGo3_h_
#define GoPiGo3_h_

#define FIRMWARE_VERSION_REQUIRED "1.0." // Firmware version needs to start with this

#define LONGEST_I2C_TRANSFER 32 // longest possible I2C read/write
#define LONGEST_SPI_TRANSFER (LONGEST_I2C_TRANSFER + 6) // at least 24 for spi_read_string 20 chars, and at least LONGEST_I2C_TRANSFER + 6 for I2C transactions

#define SPI_TARGET_SPEED 500000 // SPI target speed of 500kbps

#define SPIDEV_FILE_NAME "/dev/spidev0.1" // File name of SPI

#include <stdint.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdio.h>            // for printf
#include <string.h>           // for strstr
#include <sys/time.h>         // for clock_gettime
#include <unistd.h>
#include <stdexcept>

// Error values
#define ERROR_NONE                  0
#define ERROR_SPI_FILE             -1
#define ERROR_SPI_RESPONSE         -2
#define ERROR_WRONG_MANUFACTURER   -3
#define ERROR_WRONG_DEVICE         -4
#define ERROR_FIRMWARE_MISMATCH    -5
#define ERROR_GROVE_TYPE_MISMATCH  -6
#define ERROR_GROVE_DATA_ERROR     -7

int spi_file_handle = -1;                    // SPI file handle
struct spi_ioc_transfer spi_xfer_struct;     // SPI transfer struct
uint8_t spi_array_out[LONGEST_SPI_TRANSFER]; // SPI out array
uint8_t spi_array_in[LONGEST_SPI_TRANSFER];  // SPI in array

// Set up SPI. Open the file, and define the configuration.
int spi_setup(){
  spi_file_handle = open(SPIDEV_FILE_NAME, O_RDWR);

  if (spi_file_handle < 0){
    return ERROR_SPI_FILE;
  }

  spi_xfer_struct.cs_change = 0;               // Keep CS activated
  spi_xfer_struct.delay_usecs = 0;             // delay in us
  spi_xfer_struct.speed_hz = SPI_TARGET_SPEED; // speed
  spi_xfer_struct.bits_per_word = 8;           // bites per word 8

  return ERROR_NONE;
}

// Transfer length number of bytes. Write from outArray, read to inArray.
int spi_transfer_array(uint8_t length, uint8_t *outArray, uint8_t *inArray){
  spi_xfer_struct.len = length;
  spi_xfer_struct.tx_buf = (unsigned long)outArray;
  spi_xfer_struct.rx_buf = (unsigned long)inArray;

  if (ioctl(spi_file_handle, SPI_IOC_MESSAGE(1), &spi_xfer_struct) < 0) {
    return ERROR_SPI_FILE;
  }

  return ERROR_NONE;
}

// Function to call if an error occured that can not be resolved, such as failure to set up SPI
void fatal_error(const char *error){
  throw std::runtime_error(error);
}

//struct timespec _time;
struct timeval _time;
double get_time(){
  //clock_gettime(CLOCK_MONOTONIC_RAW, &_time);
  gettimeofday(&_time, NULL);
  return _time.tv_sec + (_time.tv_usec / 1000000);
}

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

enum GROVE_TYPE{
  GROVE_TYPE_CUSTOM = 1,
  GROVE_TYPE_IR_DI_REMOTE,
  GROVE_TYPE_IR_EV3_REMOTE,
  GROVE_TYPE_US,
  GROVE_TYPE_I2C
};

enum GROVE_STATUS{
  GROVE_STATUS_VALID_DATA,
  GROVE_STATUS_NOT_CONFIGURED,
  GROVE_STATUS_CONFIGURING,
  GROVE_STATUS_NO_DATA,
  GROVE_STATUS_I2C_ERROR
};

// LEDs
#define LED_EYE_LEFT      0x02
#define LED_EYE_RIGHT     0x01
#define LED_BLINKER_LEFT  0x04
#define LED_BLINKER_RIGHT 0x08
#define LED_LEFT_EYE      LED_EYE_LEFT
#define LED_RIGHT_EYE     LED_EYE_RIGHT
#define LED_LEFT_BLINKER  LED_BLINKER_LEFT
#define LED_RIGHT_BLINKER LED_BLINKER_RIGHT
#define LED_WIFI 0x80 // Used to indicate WiFi status. Should not be controlled by the user.

// Servo ports
#define SERVO_1 0x01
#define SERVO_2 0x02

// Motor ports
#define MOTOR_LEFT  0x01
#define MOTOR_RIGHT 0x02

// Motor Float. Value to pass to set_motor_power to make a motor float.
#define MOTOR_FLOAT -128

// Grove pins and ports
#define GROVE_1_1 0x01
#define GROVE_1_2 0x02
#define GROVE_2_1 0x04
#define GROVE_2_2 0x08
#define GROVE_1 (GROVE_1_1 + GROVE_1_2)
#define GROVE_2 (GROVE_2_1 + GROVE_2_2)

// Grove pin configurations
#define INPUT_DIGITAL 0
#define OUTPUT_DIGITAL 1
#define INPUT_DIGITAL_PULLUP 2
#define INPUT_DIGITAL_PULLDOWN 3
#define INPUT_ANALOG 4
#define OUTPUT_PWM 5
#define INPUT_ANALOG_PULLUP 6
#define INPUT_ANALOG_PULLDOWN 7

// Grove states
#define LOW 0
#define HIGH 1

// structure for I2C transactions
struct i2c_struct_t{
  uint8_t address;
  uint8_t length_write;
  uint8_t buffer_write[LONGEST_I2C_TRANSFER];
  uint8_t length_read;
  uint8_t buffer_read[LONGEST_I2C_TRANSFER];
};

// structure for ultrasonic sensor
struct sensor_ultrasonic_t{
  uint16_t mm;
  float    cm;
  float    inch;
};

// structure for infrared sensor configured for Go Box remote
struct sensor_infrared_gobox_t{
  uint8_t  button;
};

// structure for infrared sensor configured for EV3 remote
struct sensor_infrared_ev3_t{
  uint8_t  remote[4];
};

class GoPiGo3{
  public:
  // Set up the GoPiGo3
    GoPiGo3();

  // Confirm that the BrickPi3 is connected and up-to-date
    int     detect(bool critical = true);

  // Get the manufacturer (should be "Dexter Industries")
    int     get_manufacturer(char *str);
  // Get the board name (should be "BrickPi3")
    int     get_board(char *str);
  // Get the hardware version number
    int     get_version_hardware(char *str);
  // Get the firmware version number
    int     get_version_firmware(char *str);
  // Get the serial number ID that is unique to each BrickPi3
    int     get_id(char *str);

  // Control the LED
    int     set_led(uint8_t led, uint8_t red, uint8_t green = 0, uint8_t blue = 0);

  // Get the voltages of the four power rails
    // Get the voltage and return as floating point voltage
    float   get_voltage_5v     ();
    float   get_voltage_battery();
    // Pass the pass-by-reference float variable where the voltage will be stored. Returns the error code.
    int     get_voltage_5v     (float &voltage);
    int     get_voltage_battery(float &voltage);

  // Set a servo position in microseconds
    int     set_servo(uint8_t servo, uint16_t us);

  // Set the motor PWM power
    int     set_motor_power(uint8_t port, int8_t power);
  // Set the motor target position to run to (go to the specified position)
    int     set_motor_position(uint8_t port, int32_t position);
  // Set the motor speed in degrees per second.
    int     set_motor_dps(uint8_t port, int16_t dps);
  // Set the motor PWM and speed limits. PWM limit applies to set_motor_position and set_motor_dps and speed limit applies to set_motor_position.
    int     set_motor_limits(uint8_t port, uint8_t power, uint16_t dps);
  // Get the motor status. State, PWM power, encoder position, and speed (in degrees per second)
    int     get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps);
  // Offset the encoder position. By setting the offset to the current position, it effectively resets the encoder value.
    int     offset_motor_encoder(uint8_t port, int32_t position);
  // Get the encoder position
    // Pass the port and pass-by-reference variable where the encoder value will be stored. Returns the error code.
    int     get_motor_encoder(uint8_t port, int32_t &value);
    // Pass the port. Returns the encoder value.
    int32_t get_motor_encoder(uint8_t port);


  // Configure grove pin(s)/port(s)
    // Set grove port type
    int      set_grove_type(uint8_t port, uint8_t type);
    // Set grove pin(s) mode
    int      set_grove_mode(uint8_t pin, uint8_t mode);
    // Set grove pin(s) output state. LOW or HIGH (0 or 1).
    int      set_grove_state(uint8_t pin, uint8_t state);
    // Set grove pin(s) PWM duty cycle. 0-100% with 0.1% precision.
    int      set_grove_pwm_duty(uint8_t pin, float duty);
    // Set grove port(s) PWM frequency. 3 - 48000 Hz
    int      set_grove_pwm_frequency(uint8_t port, uint16_t freq = 24000);
  // Perform an I2C transaction
    int      grove_i2c_transfer(uint8_t port, i2c_struct_t *i2c_struct);
  // Start an I2C transaction
    int      grove_i2c_start(uint8_t port, i2c_struct_t *i2c_struct);
  // Read grove value(s)
    int      get_grove_value(uint8_t port, void *value_ptr);
  // Read grove pin state
    // return value
    uint8_t  get_grove_state(uint8_t pin);
    // get value with pass-by-reference, and return error code
    int      get_grove_state(uint8_t pin, uint8_t &value);
  // Read grove pin voltage
    // return floating point voltage
    float    get_grove_voltage(uint8_t pin);
    // get floating point value with pass-by-reference, and return error code
    int      get_grove_voltage(uint8_t pin, float &value);
  // Read grove pin raw ADC analog value
    // return the value
    uint16_t get_grove_analog(uint8_t pin);
    // get value with pass-by-reference, and return error code
    int      get_grove_analog(uint8_t pin, uint16_t &value);

  // Reset the grove ports (unconfigure), motors (float with no limits), and LEDs.
    int     reset_all();

  private:
    // GoPiGo3 SPI address
    uint8_t Address;

    uint8_t GroveType[2];
    uint8_t GroveI2CInBytes[2];

    int spi_read_8 (uint8_t msg_type, uint8_t  &value);
    int spi_read_16(uint8_t msg_type, uint16_t &value);
    int spi_read_32(uint8_t msg_type, uint32_t &value);
    int spi_read_string(uint8_t msg_type, char *str, uint8_t chars = 20);
    int spi_write_32(uint8_t msg_type, uint32_t value);
};

#endif