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

#include "GoPiGo3.h"
#include <iostream>
#include <unistd.h>
#include <string.h>           // for strstr
#include <fcntl.h>

///Possible types for Grove setup
enum GROVE_TYPE{
  GROVE_TYPE_CUSTOM = 1,
  GROVE_TYPE_IR_DI_REMOTE,
  GROVE_TYPE_IR_EV3_REMOTE,
  GROVE_TYPE_US,
  GROVE_TYPE_I2C
};

///Possible return values for Grove operations.
enum GROVE_STATUS{
  GROVE_STATUS_VALID_DATA,
  GROVE_STATUS_NOT_CONFIGURED,
  GROVE_STATUS_CONFIGURING,
  GROVE_STATUS_NO_DATA,
  GROVE_STATUS_I2C_ERROR
};

/// File name of SPI
#define SPIDEV_FILE_NAME "/dev/spidev0.1"

///Max length for an error description.
#define ERROR_STRING_LENGTH 100

/// Constructor: set the address and open the spi file.
/// Parameters:
///  addr:  The spi address.
GoPiGo3::GoPiGo3(uint8_t addr)
{

 if((spi_file_handle = spi_setup(spi_xfer_struct)) == ERROR_SPI_FILE)
 {
   fatal_error("spi_setup error");
 }
 Address = addr;
 this->set_grove_type(GROVE_1 + GROVE_2, GROVE_TYPE_CUSTOM);
}

/// Constructor: set the address, using a pre-opened spi handle.
/// Parameters:
///   spiHandle: a preopened spi handle.
///   addr:  The spi address.
GoPiGo3::GoPiGo3(int spiHandle, uint8_t addr)
{
 this->spi_file_handle = spiHandle;
 SetSpiIocTransfer();
 Address = addr;
}

///Destructor:  clean up everything!
GoPiGo3::~GoPiGo3()
{
  if (this->spi_file_handle >= 0)
  {
    close(this->spi_file_handle);
  }
}

/// Set up an SPI. Open the file, and define the configuration.
/// Parameters:
///   spi_ioc_transfer:  returned transfer structure used for
///                      other spi operations.
int GoPiGo3::spi_setup(struct spi_ioc_transfer& xferStructure)
{
  int file_handle = open(SPIDEV_FILE_NAME, O_RDWR);

  if (file_handle >= 0)
  {
    xferStructure.cs_change = 0;
    xferStructure.delay_usecs = 0;
    xferStructure.speed_hz =  SPI_TARGET_SPEED;
    xferStructure.bits_per_word = 8;
  }
  else
  {
     file_handle = ERROR_SPI_FILE;
  }
  return file_handle;
}

/// Transfer length number of bytes.
/// Parameters:
///    length:  array length (both arrays must be of the same length).
///    outArray --  The array of values to write.
///    inArray -- The array of values to read.
int GoPiGo3::spi_transfer_array(uint8_t length, uint8_t *outArray, uint8_t *inArray)
{
  spi_xfer_struct.len = length;
  spi_xfer_struct.tx_buf = (unsigned long)outArray;
  spi_xfer_struct.rx_buf = (unsigned long)inArray;

  if (ioctl(spi_file_handle, SPI_IOC_MESSAGE(1), &spi_xfer_struct) < 0)
  {
      return ERROR_SPI_FILE;
  }
    return ERROR_NONE;
}

/// Set the transfer structure attributes.
/// Parameters:
///   cs_Change:  struct cs_Change value.
///   delay:  The call delay.
///   speed:  The target speed.
///   bits_per_word:  The word size.
void GoPiGo3::SetSpiIocTransfer (int cs_Change, int delay, int speed, int bits_per_word)
{
  spi_xfer_struct.cs_change = cs_Change;
  spi_xfer_struct.delay_usecs = delay;
  spi_xfer_struct.speed_hz =  speed;
  spi_xfer_struct.bits_per_word = bits_per_word;
}

/// Read an 8-bit value over SPI
/// Parameters:
///   msg_type: Message type to read.
///   value:  the returned value read.
///  Returns:
///   0 on success, error value on failure.
int GoPiGo3::spi_read_8(GPGSPI_MESSAGE_TYPE msg_type, uint8_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = (uint8_t)msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(5, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = spi_array_in[4];
  return ERROR_NONE;
}

/// Read an 16-bit value over SPI
/// Parameters:
///   msg_type: Message type to read.
///   value:  the returned value read.
///  Returns:
///   0 on success, error value on failure.
int GoPiGo3::spi_read_16(GPGSPI_MESSAGE_TYPE msg_type, uint16_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = (uint8_t)msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(6, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 8) | spi_array_in[5]);
  return ERROR_NONE;
}

/// Read an 32-bit value over SPI
/// Parameters:
///   msg_type: Message type to read.
///   value:  the returned value read.
///  Returns:
///   0 on success, error value on failure.
int GoPiGo3::spi_read_32(GPGSPI_MESSAGE_TYPE msg_type, uint32_t &value){
  value = 0;
  spi_array_out[0] = Address;
  spi_array_out[1] = (uint8_t)msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(8, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  value = ((spi_array_in[4] << 24) | (spi_array_in[5] << 16) | (spi_array_in[6] << 8) | spi_array_in[7]);
  return ERROR_NONE;
}

/// Read a string value over SPI
/// Parameters:
///   msg_type: Message type to read.
///   str:  the returned string read.
///   chars: returned buffer size.
///  Returns:
///   0 on success, error value on failure.
int GoPiGo3::spi_read_string(GPGSPI_MESSAGE_TYPE msg_type, char *str, uint8_t chars){
  if((chars + 4) > LONGEST_SPI_TRANSFER){
    return -3;
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = (uint8_t)msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(chars + 4, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  for(uint8_t i = 0; i < chars; i++){
    str[i] = spi_array_in[i + 4];
  }
  return ERROR_NONE;
}

/// Write a 32-bit value over SPI
/// Parameters:
///   msg_type: Message type to read.
///   value:  the value to write.
///  Returns:
///   0 on success, error value on failure.
int GoPiGo3::spi_write_32(GPGSPI_MESSAGE_TYPE msg_type, uint32_t value){
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = ((value >> 24) & 0xFF);
  spi_array_out[3] = ((value >> 16) & 0xFF);
  spi_array_out[4] = ((value >> 8) & 0xFF);
  spi_array_out[5] = (value & 0xFF);
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

/// Confirm that the GoPiGo3 is connected and up-to-date
/// Optionally disable the detection of the GoPiGo3 hardware. This can be used for debugging
/// and testing when the GoPiGo3 would otherwise not pass the detection tests
/// Parameters:
///   critical:  if true a detection fails, a fatal error is invoked.  Otherwise, an error
///              value is returned from the function.
/// Returns:  ERROR_NONE on success, otherwise an error value indicating the error.
int GoPiGo3::detect(bool critical){
  char ErrorStr[ERROR_STRING_LENGTH];
  char str[21];
  int error;
  // assign error to the value returned by get_manufacturer, and if not 0:
  if(error = get_manufacturer(str)){
    if(critical){
      fatal_error("detect error: get_manufacturer failed. Perhaps the GoPiGo3 is not connected, or the address is incorrect.");
    }else{
      return error;
    }
  }
  if(strstr(str, "Dexter Industries") != str){
    if(critical){
      fatal_error("detect error: get_manufacturer string is not 'Dexter Industries'");
    }else{
      return ERROR_WRONG_MANUFACTURER;
    }
  }

  // assign error to the value returned by get_board, and if not 0:
  if(error = get_board(str)){
    if(critical){
      fatal_error("detect error: get_board failed");
    }else{
      return error;
    }
  }
  if(strstr(str, "GoPiGo3") != str){
    if(critical){
      fatal_error("detect error: get_board string is not 'GoPiGo3'");
    }else{
      return ERROR_WRONG_DEVICE;
    }
  }

  // assign error to the value returned by get_version_firmware, and if not 0:
  if(error = get_version_firmware(str)){
    if(critical){
      fatal_error("detect error: get_version_firmware failed");
    }else{
      return error;
    }
  }
  if(strstr(str, FIRMWARE_VERSION_REQUIRED) != str){
    if(critical){
      sprintf(ErrorStr, "detect error: GoPiGo3 firmware needs to be version %sx but is currently version %s", FIRMWARE_VERSION_REQUIRED, str);
      fatal_error(ErrorStr);
    }else{
      return ERROR_FIRMWARE_MISMATCH;
    }
  }
  return ERROR_NONE;
}

/// Get the manufacturer (should be "Dexter Industries")
/// Parameters:
///  str: value to receive the manufactuer's name.
/// Returns:  0 on success, non-zero othewise.
int GoPiGo3::get_manufacturer(char *str){
  return spi_read_string(GPGSPI_MESSAGE_GET_MANUFACTURER, str);
}

/// Get the board name (should be "BrickPi3")
/// Parameters:
///  str: value to receive the board name.
/// Returns:  0 on success, non-zero othewise.
int GoPiGo3::get_board(char *str){
  return spi_read_string(GPGSPI_MESSAGE_GET_NAME, str);
}

/// Get the hardware version number
/// Parameters:
///  str: value to receive the version.
/// Returns:  0 on success, non-zero othewise.
int GoPiGo3::get_version_hardware(char *str){
  uint32_t value;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_read_32(GPGSPI_MESSAGE_GET_HARDWARE_VERSION, value)){
    return error;
  }
  sprintf(str, "%d.%d.%d", (value / 1000000), ((value / 1000) % 1000), (value % 1000));
  return ERROR_NONE;
}

/// Get the firmware version number
/// Parameters:
///  str: value to receive the version number.
/// Returns:  0 on success, non-zero othewise.
int GoPiGo3::get_version_firmware(char *str){
  uint32_t value;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_read_32(GPGSPI_MESSAGE_GET_FIRMWARE_VERSION, value)){
    return error;
  }
  sprintf(str, "%d.%d.%d", (value / 1000000), ((value / 1000) % 1000), (value % 1000));
  return ERROR_NONE;
}

/// Read the 128-bit GoPiGo3 hardware serial number
/// Parameters:
///  str: value to receive the id.
/// Returns:  0 on success, non-zero othewise.
int GoPiGo3::get_id(char *str){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_GET_ID;
  // assign error to the value returned by spi_read_32, and if not 0:
  if(int error = spi_transfer_array(20, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  for(int i = 0; i < 16; i++){
    sprintf((str + (i * 2)), "%02X", spi_array_in[i + 4]);
  }
  return ERROR_NONE;
}

/// Control the LED
/// Parameters:
///   led -- The LED(s). LED_LEFT_EYE, LED_RIGHT_EYE, LED_LEFT_BLINKER, LED_RIGHT_BLINKER, and/or LED_WIFI.
///   red -- The LED's Red color component (0-255)
///   green -- The LED's Green color component (0-255)
///   blue -- The LED's Blue color component (0-255)
   /// Returns:  0 on success, non-zero othewise.
int GoPiGo3::set_led(uint8_t led, uint8_t red, uint8_t green, uint8_t blue){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_LED;
  spi_array_out[2] = led;
  spi_array_out[3] = red;
  spi_array_out[4] = green;
  spi_array_out[5] = blue;
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

/// Get the voltages of the four power rails
/// Returns: the voltage.
float GoPiGo3::get_voltage_5v(){
  float voltage;
  int res = get_voltage_5v(voltage);
  if(res)return res;
  return voltage;
}

/// Get the voltages of the four power rails
/// Parameters:
///   voltage:  the returned circuit voltage.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_voltage_5v(float &voltage){
  uint16_t value;
  int res = spi_read_16(GPGSPI_MESSAGE_GET_VOLTAGE_5V, value);
  voltage = value / 1000.0;
  return res;
}

/// Get the battery voltage.
/// Returns: the battery voltage.
float GoPiGo3::get_voltage_battery(){
  float voltage;
  int res = get_voltage_battery(voltage);
  if(res)return res;
  return voltage;
}

/// Get the battery voltage.
/// Parameters:
///   voltage:  the returned value of the battery voltage
/// Returns: 0 on success, otherwise an error code.
int GoPiGo3::get_voltage_battery(float &voltage){
  uint16_t value;
  int res = spi_read_16(GPGSPI_MESSAGE_GET_VOLTAGE_VCC, value);
  voltage = value / 1000.0;
  return res;
}

/// Set a servo position in microseconds
/// Parameters:
///   servo -- The servo(s). SERVO_1 and/or SERVO_2.
///   us -- The pulse width in microseconds (0-16666)
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_servo(uint8_t servo, uint16_t us){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_SERVO;
  spi_array_out[2] = servo;
  spi_array_out[3] = ((us >> 8) & 0xFF);
  spi_array_out[4] = (us & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

/// Set the motor power in percent
/// Parameters:
///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
///   power -- The PWM power from -100 to 100, or MOTOR_FLOAT for float.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_motor_power(uint8_t port, int8_t power)
{
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_PWM;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

/// Set the motor target position to run to (go to the specified position)
/// Parameters:
///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
///   position -- The target position
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_motor_position(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_POSITION;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  return spi_transfer_array(7, spi_array_out, spi_array_in);
}

/// Set the motor speed in degrees per second.
/// Parameters:
///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
///   dps -- The target speed in degrees per second	int
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_motor_dps(uint8_t port, int16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_DPS;
  spi_array_out[2] = port;
  spi_array_out[3] = ((dps >> 8) & 0xFF);
  spi_array_out[4] = (dps & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

/// Set the motor PWM and speed limits. PWM limit applies to set_motor_position and set_motor_dps and speed limit applies to set_motor_position.
/// Changed this!
/// Parameters:
///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
///   power -- The power limit in percent (0 to 100), with 0 being no limit (100)
///   dps -- The speed limit in degrees per second, with 0 being no limit
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_motor_limits(uint8_t port, uint8_t power, uint16_t dps){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_MOTOR_LIMITS;
  spi_array_out[2] = port;
  spi_array_out[3] = power;
  spi_array_out[4] = ((dps >> 8) & 0xFF);
  spi_array_out[5] = (dps & 0xFF);
  return spi_transfer_array(6, spi_array_out, spi_array_in);
}

/// Get the motor status. State, PWM power, encoder position, and speed (in degrees per second)
/// Parameters:
///   port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
///   state -- Bits of bit-flags that indicate motor status:
///            bit 0 -- LOW_VOLTAGE_FLOAT - The motors are automatically disabled because the battery voltage is too low
///            bit 1 -- OVERLOADED - The motors aren't close to the target (applies to position control and dps speed control).
///   power -- the raw PWM power in percent (-100 to 100)
///   position -- The encoder position
///   dps -- The current speed in Degrees Per Second
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps){
  uint8_t msg_type;
  switch(port){
    case MOTOR_LEFT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_STATUS_LEFT;
    break;
    case MOTOR_RIGHT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_STATUS_RIGHT;
    break;
    default:
      fatal_error("get_motor_status error. Must be one motor at a time. MOTOR_LEFT or MOTOR_RIGHT.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(12, spi_array_out, spi_array_in)){
    return error;
  }

  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }

  state    = spi_array_in[4];
  power    = spi_array_in[5];
  position = ((spi_array_in[6] << 24) | (spi_array_in[7] << 16) | (spi_array_in[8] << 8) | spi_array_in[9]);
  dps      = ((spi_array_in[10] << 8) | spi_array_in[11]);

  return ERROR_NONE;
}


/// Offset the encoder position. By setting the offset to the current position, it effectively resets the encoder value.
/// Parameters:
///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
///   position -- The encoder offset
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::offset_motor_encoder(uint8_t port, int32_t position){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_OFFSET_MOTOR_ENCODER;
  spi_array_out[2] = port;
  spi_array_out[3] = ((position >> 24) & 0xFF);
  spi_array_out[4] = ((position >> 16) & 0xFF);
  spi_array_out[5] = ((position >> 8) & 0xFF);
  spi_array_out[6] = (position & 0xFF);
  return spi_transfer_array(7, spi_array_out, spi_array_in);
}

/// Get the encoder position
/// Parameters:
///   port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
///   value --  the encoder position in degrees
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_motor_encoder(uint8_t port, int32_t &value){
  GPGSPI_MESSAGE_TYPE msg_type;
  switch(port){
    case MOTOR_LEFT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_ENCODER_LEFT;
    break;
    case MOTOR_RIGHT:
      msg_type = GPGSPI_MESSAGE_GET_MOTOR_ENCODER_RIGHT;
    break;
    default:
      fatal_error("get_motor_encoder error. Must be one motor at a time. MOTOR_LEFT or MOTOR_RIGHT.");
  }
  uint32_t Value;
  int res = spi_read_32(msg_type, Value);
  value = Value;
  return res;
}

///Get the encoder value.
/// Parameters:
///   port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
/// Returns:
///   The encoder position in degrees
int32_t GoPiGo3::get_motor_encoder(uint8_t port){
  int32_t value;
  get_motor_encoder(port, value);
  return value;
}

/// Set grove port type
/// Parameters:
///   port -- The grove port(s). GROVE_1 and/or GROVE_2.
///   type -- The grove device type
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_grove_type(uint8_t port, uint8_t type){
  if((port & GROVE_1) == GROVE_1){
    GroveType[0] = type;
  }
  if((port & GROVE_2) == GROVE_2){
    GroveType[1] = type;
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_TYPE;
  spi_array_out[2] = port;
  spi_array_out[3] = type;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

/// Set grove pin(s) mode
/// Parameters:
///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
///   mode -- The pin mode. GROVE_INPUT_DIGITAL, GROVE_OUTPUT_DIGITAL, GROVE_INPUT_DIGITAL_PULLUP, GROVE_INPUT_DIGITAL_PULLDOWN, GROVE_INPUT_ANALOG, GROVE_OUTPUT_PWM, GROVE_INPUT_ANALOG_PULLUP, or GROVE_INPUT_ANALOG_PULLDOWN.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_grove_mode(uint8_t pin, uint8_t mode){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_MODE;
  spi_array_out[2] = pin;
  spi_array_out[3] = mode;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

/// Set grove pin(s) output state. LOW or HIGH (0 or 1).
/// Parameters:
///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
///   state -- The pin state. GROVE_LOW or GROVE_HIGH.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_grove_state(uint8_t pin, GROVE_STATE state){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_STATE;
  spi_array_out[2] = pin;
  spi_array_out[3] = (uint8_t)state;
  return spi_transfer_array(4, spi_array_out, spi_array_in);
}

/// Set grove pin(s) PWM duty cycle. 0-100% with 0.1% precision.
/// Parameters:
///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
///   duty -- The PWM duty cycle in percent.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_grove_pwm_duty(uint8_t pin, float duty){
  if(duty > 100){
    duty = 100;
  }else if(duty < 0){
    duty = 0;
  }
  uint16_t duty_value = duty * 10;
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_PWM_DUTY;
  spi_array_out[2] = pin;
  spi_array_out[3] = ((duty_value >> 8) & 0xFF);
  spi_array_out[4] = (duty_value & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

/// Set grove port(s) PWM frequency. 3 - 48000 Hz
/// Parameters:
///   port -- The grove port(s). GROVE_1 and/or GROVE_2.
///   freq -- The PWM frequency. Range is 3 through 48000Hz. Default is 24000 (24kHz).
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::set_grove_pwm_frequency(uint8_t port, uint16_t freq){
  spi_array_out[0] = Address;
  spi_array_out[1] = GPGSPI_MESSAGE_SET_GROVE_PWM_FREQUENCY;
  spi_array_out[2] = port;
  spi_array_out[3] = ((freq >> 8) & 0xFF);
  spi_array_out[4] = (freq & 0xFF);
  return spi_transfer_array(5, spi_array_out, spi_array_in);
}

/// Perform an I2C transaction
/// Parameters:
///   port -- The grove port. GROVE_1 or GROVE_2.
///   i2c_struct -- contains the setup parameters for the transfer, as well as the
///                 returned buffer.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::grove_i2c_transfer(uint8_t port, i2c_struct_t *i2c_struct){
  double Timeout = get_time() + 0.005;
  bool Continue = false;
  int error;
  while(!Continue){
    if(error = grove_i2c_start(port, i2c_struct)){
      if(get_time() >= Timeout){
        return error;
      }
    }else{
      Continue = true;
    }
  }

  double DelayTime = 0;
  if(i2c_struct->length_write){
    DelayTime += 1 + i2c_struct->length_write;
  }
  if(i2c_struct->length_read){
    DelayTime += 1 + i2c_struct->length_read;
  }
  DelayTime *= 0.000115;         // each I2C byte takes about 115uS at full speed (about 100kbps)
  // No point trying to read the values before they are ready.
  usleep((DelayTime * 1000000)); // delay for as long as it will take to do the I2C transaction.
  Timeout = get_time() + 0.005;  // timeout after 5ms of failed attempted reads

  while(true){
    if(error = get_grove_value(port, i2c_struct)){
      if(get_time() >= Timeout){
        return error;
      }
    }else{
      return ERROR_NONE;
    }
  }
}

/// Start an I2C transaction
/// Parameters:
///   port -- The grove port. GROVE_1 or GROVE_2.
///   i2c_struct -- contains the setup parameters for the transfer, as well as the
///                 returned buffer.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::grove_i2c_start(uint8_t port, i2c_struct_t *i2c_struct){
  uint8_t msg_type;
  uint8_t port_index;
  switch(port){
    case GROVE_1:
      msg_type = GPGSPI_MESSAGE_START_GROVE_I2C_1;
      port_index = 0;
    break;
    case GROVE_2:
      msg_type = GPGSPI_MESSAGE_START_GROVE_I2C_2;
      port_index = 1;
    break;
    default:
      fatal_error("grove_i2c_start error. Must be one grove port at a time. GROVE_1 or GROVE_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  spi_array_out[2] = ((i2c_struct->address & 0x7F) << 1);

  if(i2c_struct->length_read > LONGEST_I2C_TRANSFER){
    i2c_struct->length_read = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[3] = i2c_struct->length_read;
  GroveI2CInBytes[port_index] = i2c_struct->length_read;

  if(i2c_struct->length_write > LONGEST_I2C_TRANSFER){
    i2c_struct->length_write = LONGEST_I2C_TRANSFER;
  }
  spi_array_out[4] = i2c_struct->length_write;

  for(uint8_t i = 0; i < i2c_struct->length_write; i++){
    spi_array_out[5 + i] = i2c_struct->buffer_write[i];
  }

  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array((5 + i2c_struct->length_write), spi_array_out, spi_array_in)){
    return error;
  }

  // If the fourth byte received is not 0xA5
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  // If the fifth byte received is not GROVE_STATUS_VALID_DATA
  if(spi_array_in[4] != GROVE_STATUS_VALID_DATA){
    return spi_array_in[4];
  }

  return ERROR_NONE;
}

/// Read grove value(s)
/// Parameters:
///   port -- The grove port. GROVE_1 or GROVE_2.
///   value_ptr -- returned grove value
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_grove_value(uint8_t port, void *value_ptr){
  uint8_t msg_type;
  uint8_t port_index;
  switch(port){
    case GROVE_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VALUE_1;
      port_index = 0;
    break;
    case GROVE_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VALUE_2;
      port_index = 1;
    break;
    default:
      fatal_error("get_grove_value error. Must be one grove port at a time. GROVE_1 or GROVE_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;

  uint8_t spi_transfer_length;

  // Determine the SPI transaction byte length based on the grove type
  switch(GroveType[port_index]){
    case GROVE_TYPE_IR_DI_REMOTE:
      spi_transfer_length = 7;
    break;
    case GROVE_TYPE_IR_EV3_REMOTE:
      spi_transfer_length = 10;
    break;
    case GROVE_TYPE_US:
      spi_transfer_length = 8;
    break;
    case GROVE_TYPE_I2C:
      spi_transfer_length = 6 + GroveI2CInBytes[port_index];
    break;
    default:
      return GROVE_STATUS_NOT_CONFIGURED;
    break;
  }

  // Get the grove value(s), and if error
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(spi_transfer_length, spi_array_out, spi_array_in)){
    return error;
  }
  // If the fourth byte received is not 0xA5
  if(spi_array_in[3] != 0xA5){
    return ERROR_SPI_RESPONSE;
  }
  // If the grove type is not what it should be
  if(spi_array_in[4] != GroveType[port_index]){
    printf("get_grove_value %d != %d for port index %d\n", spi_array_in[4], GroveType[port_index], port_index);
    return ERROR_GROVE_TYPE_MISMATCH;
  }
  // If the sensor value(s) is not valid (still configuring the grove port, or error communicating with grove device)
  if(spi_array_in[5] != GROVE_STATUS_VALID_DATA){
    return spi_array_in[5];
  }

  if(GroveType[port_index] == GROVE_TYPE_IR_DI_REMOTE){
    sensor_infrared_gobox_t *Value = (sensor_infrared_gobox_t*)value_ptr;
    Value->button = spi_array_in[6];
  }else if(GroveType[port_index] == GROVE_TYPE_IR_EV3_REMOTE){
    sensor_infrared_ev3_t *Value = (sensor_infrared_ev3_t*)value_ptr;
    Value->remote[0] = spi_array_in[6];
    Value->remote[1] = spi_array_in[7];
    Value->remote[2] = spi_array_in[8];
    Value->remote[3] = spi_array_in[9];
  }else if(GroveType[port_index] == GROVE_TYPE_US){
    sensor_ultrasonic_t *Value = (sensor_ultrasonic_t*)value_ptr;
    Value->mm = (((spi_array_in[6] << 8) & 0xFF00) | (spi_array_in[7] & 0xFF));
    Value->cm = Value->mm / 10.0;
    Value->inch = Value->mm / 25.4;
  }else if(GroveType[port_index] == GROVE_TYPE_I2C){
    i2c_struct_t *Value = (i2c_struct_t*)value_ptr;
    for(uint8_t b = 0; b < GroveI2CInBytes[port_index]; b++){
      Value->buffer_read[b] = spi_array_in[6 + b];
    }
  }
  return GROVE_STATUS_VALID_DATA;
}

/// Read the grove pin state
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
/// Returns:
///   The grove state.
GROVE_STATE GoPiGo3::get_grove_state(uint8_t pin){
  GROVE_STATE value;
  get_grove_state(pin, value);
  return value;
}

/// Read the grove pin state
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
///   value -- The returned grove state.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_grove_state(uint8_t pin, GROVE_STATE&value){
  value = LOW;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_STATE_2_2;
    break;
    default:
      fatal_error("get_grove_state error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  memset(spi_array_out, 0,sizeof(char) *6);
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(6, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = (GROVE_STATE)spi_array_in[5];
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

/// Read grove pin voltage
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
/// Returns:
///   The pin voltage.
float GoPiGo3::get_grove_voltage(uint8_t pin){
  float value;
  get_grove_voltage(pin, value);
  return value;
}

/// Read grove pin voltage
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
///   value -- The pin voltage.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_grove_voltage(uint8_t pin, float &value){
  value = 0;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_VOLTAGE_2_2;
    break;
    default:
      fatal_error("get_grove_voltage error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(7, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = (((spi_array_in[5] << 8) & 0xFF) | (spi_array_in[5] & 0xFF)) / 1000.0;
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

/// Get a grove input pin 12-bit raw ADC reading
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
/// Returns:
///   The ADC reading.
uint16_t GoPiGo3::get_grove_analog(uint8_t pin){
  uint16_t value;
  get_grove_analog(pin, value);
  return value;
}

/// Get a grove input pin 12-bit raw ADC reading
/// Parameters:
///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
///   value -- the returned ADC reading.
/// Returns:
///   0 on success, an error value otherwise.
int GoPiGo3::get_grove_analog(uint8_t pin, uint16_t &value){
  value = 0;
  uint8_t msg_type;
  switch(pin){
    case GROVE_1_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_1;
    break;
    case GROVE_1_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_1_2;
    break;
    case GROVE_2_1:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_1;
    break;
    case GROVE_2_2:
      msg_type = GPGSPI_MESSAGE_GET_GROVE_ANALOG_2_2;
    break;
    default:
      fatal_error("get_grove_analog error. Must be one pin at a time. GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.");
  }
  spi_array_out[0] = Address;
  spi_array_out[1] = msg_type;
  // assign error to the value returned by spi_transfer_array, and if not 0:
  if(int error = spi_transfer_array(7, spi_array_out, spi_array_in)){
    return error;
  }
  if(spi_array_in[3] == 0xA5){
    if(spi_array_in[4] == GROVE_STATUS_VALID_DATA){
      value = (((spi_array_in[5] << 8) & 0xFF) | (spi_array_in[5] & 0xFF));
      return ERROR_NONE;
    }else{
      return ERROR_GROVE_DATA_ERROR;
    }
  }else{
    return ERROR_SPI_RESPONSE;
  }
}

/// Reset the grove ports (unconfigure), motors (float with no limits), and LEDs.
/// Returns:
///   0 on success, the error value otherwise.
///   Note:  on error, execution will halt on the error and return the
///          error value of the first conguration that fails.
int GoPiGo3::reset_all(){
  int res1 = set_grove_type(GROVE_1 + GROVE_2, GROVE_TYPE_CUSTOM);
  int res2 = set_motor_power(MOTOR_LEFT + MOTOR_RIGHT, MOTOR_FLOAT);
  int res3 = set_motor_limits(MOTOR_LEFT + MOTOR_RIGHT, 0, 0);
  int res4 = set_led((LED_EYE_LEFT + LED_EYE_RIGHT + LED_BLINKER_LEFT + LED_BLINKER_RIGHT), 0, 0, 0);
  int res5 = set_grove_pwm_duty(GROVE_1 + GROVE_2, 0);
  int res6 = set_grove_pwm_frequency(GROVE_1 + GROVE_2);
  if(res1){
    return res1;
  }else if(res2){
    return res2;
  }else if(res3){
    return res3;
  }else if(res4){
    return res4;
  }else if(res5){
    return res5;
  }else if(res6){
    return res6;
  }
  return ERROR_NONE;
}
