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

#include "GoPiGoCommon.h"
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>
#include <stdio.h>            // for file and error output
#include <sys/time.h>         // for clock_gettime

#include <stdlib.h>

class GoPiGo3 {
  public:
	/// Constructor: set the address and open the spi file.
	/// Parameters:
	///  addr:  The spi address.
	GoPiGo3(uint8_t addr = 8);

	/// Constructor: set the address, using a pre-opened spi handle.
	/// Parameters:
	///   spiHandle: a preopened spi handle.
	///   addr:  The spi address.
	GoPiGo3(int spiHandle, uint8_t addr = 8);

	/// Destructor:  clean up everything!
	~GoPiGo3();

	/// Set up an SPI. Open the file, and define the configuration.
	/// Parameters:
	///   spi_ioc_transfer:  retiran
    static int spi_setup(struct spi_ioc_transfer&);

	/// Confirm that the GoPiGo3 is connected and up-to-date
	/// Optionally disable the detection of the GoPiGo3 hardware. This can be used for debugging
	/// and testing when the GoPiGo3 would otherwise not pass the detection tests
	/// Parameters:
	///   critical:  if true a detection fails, a fatal error is invoked.  Otherwise, an error
	///              value is returned from the function.
	/// Returns:  ERROR_NONE on success, otherwise an error value indicating the error.
	int     detect(bool critical = true);

	/// Get the manufacturer (should be "Dexter Industries")
    /// Parameters:
    ///  str: value to receive the manufactuer's name.
	/// Returns:  0 on success, non-zero othewise.
	int     get_manufacturer(char *str);

	/// Get the board name (should be "BrickPi3")
	/// Parameters:
    ///  str: value to receive the board name.
	/// Returns:  0 on success, non-zero othewise.
	int     get_board(char *str);

	/// Get the hardware version number
    /// Parameters:
    ///  str: value to receive the version.
	/// Returns:  0 on success, non-zero othewise.
	int     get_version_hardware(char *str);

	/// Get the firmware version number
    /// Parameters:
    ///  str: value to receive the version number.
	/// Returns:  0 on success, non-zero othewise.
	int     get_version_firmware(char *str);

	/// Read the 128-bit GoPiGo3 hardware serial number
    /// Parameters:
    ///  str: value to receive the id.
	/// Returns:  0 on success, non-zero othewise.
	int     get_id(char *str);

	/// Control the LED
    /// Parameters:
    ///   led -- The LED(s). LED_LEFT_EYE, LED_RIGHT_EYE, LED_LEFT_BLINKER, LED_RIGHT_BLINKER, and/or LED_WIFI.
    ///   red -- The LED's Red color component (0-255)
    ///   green -- The LED's Green color component (0-255)
    ///   blue -- The LED's Blue color component (0-255)
   	/// Returns:  0 on success, non-zero othewise.
	int     set_led(uint8_t led, uint8_t red, uint8_t green = 0, uint8_t blue = 0);

	/// Get the battery voltage.
	/// Returns: the battery voltage.
    float   get_voltage_battery();

    /// Get the battery voltage.
    /// Parameters:
    ///   voltage:  the returned value of the battery voltage
    /// Returns: 0 on success, otherwise an error code.
	int     get_voltage_battery(float &voltage);

	/// Get the voltages of the four power rails
	/// Returns: the voltage.
	float   get_voltage_5v();

	/// Get the voltages of the four power rails
    /// Parameters:
    ///   voltage:  the circuit voltage.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int     get_voltage_5v(float &voltage);

	/// Set a servo position in microseconds
	/// Parameters:
    ///   servo -- The servo(s). SERVO_1 and/or SERVO_2.
    ///   us -- The pulse width in microseconds (0-16666)
    /// Returns:
    ///   0 on success, an error value otherwise.
    int     set_servo(uint8_t servo, uint16_t us);

    /// Set the motor power in percent
	/// Parameters:
    ///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
    ///   power -- The PWM power from -100 to 100, or MOTOR_FLOAT for float.
    /// Returns:
    ///   0 on success, an error value otherwise.
    int     set_motor_power(uint8_t port, int8_t power);

	/// Set the motor target position to run to (go to the specified position)
	/// Parameters:
    ///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
    ///   position -- The target position
    /// Returns:
    ///   0 on success, an error value otherwise.
 	int     set_motor_position(uint8_t port, int32_t position);

 	/// Set the motor speed in degrees per second.
	/// Parameters:
    ///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
    ///   dps -- The target speed in degrees per second	int
    /// Returns:
    ///   0 on success, an error value otherwise.
    int set_motor_dps(uint8_t port, int16_t dps);

	/// Set the motor PWM and speed limits. PWM limit applies to set_motor_position and set_motor_dps and speed limit applies to set_motor_position.
	/// Changed this!
    /// Parameters:
    ///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
    ///   power -- The power limit in percent (0 to 100), with 0 being no limit (100)
    ///   dps -- The speed limit in degrees per second, with 0 being no limit
    /// Returns:
    ///   0 on success, an error value otherwise.
	int     set_motor_limits(uint8_t port, uint8_t power = 0, uint16_t dps = 0);

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
    int     get_motor_status(uint8_t port, uint8_t &state, int8_t &power, int32_t &position, int16_t &dps);

	/// Offset the encoder position. By setting the offset to the current position, it effectively resets the encoder value.
    /// Parameters:
    ///   port -- The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
    ///   position -- The encoder offset
    /// Returns:
    ///   0 on success, an error value otherwise.
    int offset_motor_encoder(uint8_t port, int32_t position);

	/// Get the encoder position
	/// Parameters:
    ///   port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
	///   value --  the encoder position in degrees
    /// Returns:
    ///   0 on success, an error value otherwise.
	int get_motor_encoder(uint8_t port, int32_t &value);

	///Get the encoder value.
	/// Parameters:
    ///   port -- The motor port (one at a time). MOTOR_LEFT or MOTOR_RIGHT.
    /// Returns:
    ///   The encoder position in degrees
    int32_t get_motor_encoder(uint8_t port);

	/// Set grove port type
	/// Parameters:
    ///   port -- The grove port(s). GROVE_1 and/or GROVE_2.
    ///   type -- The grove device type
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      set_grove_type(uint8_t port, uint8_t type);

	/// Set grove pin(s) mode
    /// Parameters:
    ///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
    ///   mode -- The pin mode. GROVE_INPUT_DIGITAL, GROVE_OUTPUT_DIGITAL, GROVE_INPUT_DIGITAL_PULLUP, GROVE_INPUT_DIGITAL_PULLDOWN, GROVE_INPUT_ANALOG, GROVE_OUTPUT_PWM, GROVE_INPUT_ANALOG_PULLUP, or GROVE_INPUT_ANALOG_PULLDOWN.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      set_grove_mode(uint8_t pin, uint8_t mode);

	/// Set grove pin(s) output state. LOW or HIGH (0 or 1).
	/// Parameters:
    ///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
    ///   state -- The pin state. GROVE_LOW or GROVE_HIGH.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      set_grove_state(uint8_t pin, GROVE_STATE state);

	/// Set grove pin(s) PWM duty cycle. 0-100% with 0.1% precision.
    /// Parameters:
    ///   pin -- The grove pin(s). GROVE_1_1, GROVE_1_2, GROVE_2_1, and/or GROVE_2_2.
    ///   duty -- The PWM duty cycle in percent.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      set_grove_pwm_duty(uint8_t pin, float duty);

	/// Set grove port(s) PWM frequency. 3 - 48000 Hz
	/// Parameters:
    ///   port -- The grove port(s). GROVE_1 and/or GROVE_2.
    ///   freq -- The PWM frequency. Range is 3 through 48000Hz. Default is 24000 (24kHz).
    /// Returns:
    ///   0 on success, an error value otherwise.
    int      set_grove_pwm_frequency(uint8_t port, uint16_t freq = 24000);

	/// Perform an I2C transaction
	/// Parameters:
    ///   port -- The grove port. GROVE_1 or GROVE_2.
    ///   i2c_struct -- contains the setup parameters for the transfer, as well as the
    ///                 returned buffer.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      grove_i2c_transfer(uint8_t port, i2c_struct_t *i2c_struct);

	/// Start an I2C transaction
	/// Parameters:
    ///   port -- The grove port. GROVE_1 or GROVE_2.
    ///   i2c_struct -- contains the setup parameters for the transfer, as well as the
    ///                 returned buffer.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      grove_i2c_start(uint8_t port, i2c_struct_t *i2c_struct);

	/// Read grove value(s)
	/// Parameters:
    ///   port -- The grove port. GROVE_1 or GROVE_2.
    ///   value_ptr -- returned grove value
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      get_grove_value(uint8_t port, void *value_ptr);

	/// Read the grove pin state
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    /// Returns:
    ///   The grove state.
	GROVE_STATE get_grove_state(uint8_t pin);

	/// Read the grove pin state
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    ///   value -- The returned grove state.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      get_grove_state(uint8_t pin, GROVE_STATE &value);

	/// Read grove pin voltage
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    /// Returns:
    ///   The pin voltage.
    float    get_grove_voltage(uint8_t pin);

	/// Read grove pin voltage
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    ///   value -- The pin voltage.
    /// Returns:
    ///   0 on success, an error value otherwise.
 	int      get_grove_voltage(uint8_t pin, float &value);

    /// Get a grove input pin 12-bit raw ADC reading
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    /// Returns:
    ///   The ADC reading.
	uint16_t get_grove_analog(uint8_t pin);

    /// Get a grove input pin 12-bit raw ADC reading
    /// Parameters:
    ///   pin -- The grove pin (one at a time). GROVE_1_1, GROVE_1_2, GROVE_2_1, or GROVE_2_2.
    ///   value -- the returned ADC reading.
    /// Returns:
    ///   0 on success, an error value otherwise.
	int      get_grove_analog(uint8_t pin, uint16_t &value);

	/// Reset the grove ports (unconfigure), motors (float with no limits), and LEDs.
	/// Returns:
	///   0 on success, the error value otherwise.
	///   Note:  on error, execution will halt on the error and return the
	///          error value of the first conguration that fails.
	int     reset_all();

	///Redirect stderr to another file. This is useful for debugging purposes,
	///directing error messages to a disk (or any other). file.
	inline void RedirectStdErr(const char* fileName) { stderr = freopen(fileName, "w+", stderr); };

  private:
	/// GoPiGo3 SPI address; set in the constructor.
	uint8_t Address;

    /// Grove type array:  initialized to:
    ///  GroveType[0] = GROVE_1 + GROVE_2
    ///  GroveType[1] = GROVE_TYPE_CUSTOM
	uint8_t GroveType[2];

    /// Array used for I2C transfers.
	uint8_t GroveI2CInBytes[2];

    /// Read an 8-bit value over SPI
    /// Parameters:
    ///   msg_type: Message type to read.
    ///   value:  the returned value read.
    ///  Returns:
    ///   0 on success, error value on failure.
	int spi_read_8(GPGSPI_MESSAGE_TYPE msg_type, uint8_t  &value);

    /// Read an 16-bit value over SPI
    /// Parameters:
    ///   msg_type: Message type to read.
    ///   value:  the returned value read.
    ///  Returns:
    ///   0 on success, error value on failure.
	int spi_read_16(GPGSPI_MESSAGE_TYPE msg_type, uint16_t &value);

    /// Read an 32-bit value over SPI
    /// Parameters:
    ///   msg_type: Message type to read.
    ///   value:  the returned value read.
    ///  Returns:
    ///   0 on success, error value on failure.
	int spi_read_32(GPGSPI_MESSAGE_TYPE msg_type, uint32_t &value);

    /// Read a string value over SPI
    /// Parameters:
    ///   msg_type: Message type to read.
    ///   str:  the returned string read.
    ///   chars: returned buffer size.
    ///  Returns:
    ///   0 on success, error value on failure.
	int spi_read_string(GPGSPI_MESSAGE_TYPE msg_type, char *str, uint8_t chars = 20);

    /// Write a 32-bit value over SPI
    /// Parameters:
    ///   msg_type: Message type to read.
    ///   value:  the value to write.
    ///  Returns:
    ///   0 on success, error value on failure.
	int spi_write_32(GPGSPI_MESSAGE_TYPE msg_type, uint32_t value);

  protected:
    ///The file handle for the SPI file.
	int spi_file_handle;

    ///The transfer structure.  Setup in the constructor call.
	struct spi_ioc_transfer spi_xfer_struct;

	///The input array for an spi_transfer_array call.
	uint8_t spi_array_out[LONGEST_SPI_TRANSFER];

	/// The array returned from an spi_transfer_array call.
	uint8_t spi_array_in[LONGEST_SPI_TRANSFER];

	/// Set the transfer structure attributes.
	/// Parameters:
    ///   cs_Change:  struct cs_Change value.
	///   delay:  The call delay.
	///   speed:  The target speed.
	///   bits_per_word:  The word size.
	void SetSpiIocTransfer(int cs_Change = 0, int delay = 0, int speed = SPI_TARGET_SPEED, int bits_per_word = 8);

	/// Transfer length number of bytes. Write from outArray, read to inArray.
	int spi_transfer_array(uint8_t length, uint8_t *outArray, uint8_t *inArray);

	/// Handles errors that cannot be resolved, such as failure to set up SPI.
	/// Prints the error string to stderr and ends the program.
	/// Parameters:
	///  error -- a character string denoting the error.
	inline void fatal_error(char *error)
	{
		fprintf(stderr, "%s\n", error);
		fclose(stderr);
		exit(-1);
	}

	/// Handles errors that cannot be resolved, such as failure to set up SPI
	/// Prints the error string to stderr and ends the program.
	/// Parameters:
	///  error -- a character string denoting the error.
	inline void fatal_error(const char *error)
	{
		fprintf(stderr, "%s\n", error);
		fclose(stderr);
		exit(-1);
	}

	///Get the current time as microseconds past a set base time.
	double get_time()
	{
		struct timeval _time;
		gettimeofday(&_time, NULL);
		return _time.tv_sec + (((double)_time.tv_usec) / 1000000.0);
	}
};

#endif
