package com.dexterindustries.gopigo3driver;

import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

/**
 * Created by jabrena on 20/7/17.
 */

public class GoPiGo3 {

    static final Logger LOG = Logger.getLogger(GoPiGo3.class.getName());
    // SPI device
    public static SpiDevice spi = null;

    private final byte[] spi_array_out = new byte[32]; //TODO: double check this size
    private byte[] spi_array_in = null;
    
    private byte[] GroveType = new byte[2]; //[0,0] by default
    private byte[] GroveI2CInBytes = new byte[2];
    
    public double WHEEL_DIAMETER           = 66.5; // wheel diameter (mm)
    public double WHEEL_BASE_WIDTH         = 117;  // distance (mm) from left wheel to right wheel. This works with the initial GPG3 prototype. Will need to be adjusted.
    public double WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * Math.PI; // The circumference of the circle the wheels will trace while turning (mm)
    public double WHEEL_CIRCUMFERENCE      = WHEEL_DIAMETER   * Math.PI; // The circumference of the wheels (mm)
  
    public double MOTOR_GEAR_RATIO = 120; // Motor gear ratio # 220 for Nicole's prototype
    public double ENCODER_TICKS_PER_ROTATION = 6;   // Encoder ticks per motor rotation (number of magnet positions) # 16 for early prototypes
    public double MOTOR_TICKS_PER_DEGREE = ((MOTOR_GEAR_RATIO * ENCODER_TICKS_PER_ROTATION) / 360.0); // encoder ticks per output shaft rotation degree
   
    
    public enum GROVE_TYPE { 
    	CUSTOM ((byte)1),
    	IR_DI_REMOTE ((byte)2),
    	IR_EV3_REMOTE ((byte)3),
    	US ((byte)4),
    	I2C ((byte)5);
    	
    	private final byte value;
    	
    	GROVE_TYPE(byte value) {
    		this.value = value;
    	}
    	
    	public byte value() { return value; };
    }
    
    public enum GROVE_STATE {
    	VALID_DATA ((byte)1),
    	NOT_CONFIGURED ((byte)2),
    	CONFIGURING ((byte)3),
    	NO_DATA ((byte)4),
    	I2C_ERROR ((byte)5);
    	
    	private final byte value;
    	
    	GROVE_STATE(byte value) {
    		this.value = value;
    	}
    	
    	public byte value() { return value; };
    }
    
    public GoPiGo3() throws IOException {

        // create SPI object instance for SPI for communication
        this.spi = SpiFactory.getInstance(SpiChannel.CS1,
                SpiDevice.DEFAULT_SPI_SPEED, // default spi speed 1 MHz
                SpiDevice.DEFAULT_SPI_MODE); // default spi mode 0
    }
    
    /**
     * Builder for output arrays
     * @author Ken Fogel
     * @param args
     */
    public void spiArrayBuilder(byte... args) {
        Arrays.fill(spi_array_out, (byte) 0);

        for (int x = 0; x < args.length; ++x) {
            spi_array_out[x] = args[x];
        }
    }
    
    public void spi_array_builder(byte... args) {
    	spiArrayBuilder(args);
    }

    /**
     * Run a specific motor
     * 
     *
     * @param power
     * @throws IOException
     */
    public void set_motor_power(byte motor, byte power) throws IOException {
       	spiArrayBuilder(ADDRESS, SET_MOTOR_PWM, motor, power);
        this.spi.write(spi_array_out);
    }
    
    /**
     * Sets motor target position in degrees
     * 
     * @param motor
     * @param position
     * @throws IOException
     */
    public void set_motor_position(byte motor, double position) throws IOException {
    	int position_raw = (int)(position * MOTOR_TICKS_PER_DEGREE);
       	byte firstByte = (byte)((position_raw >>> 24) & 0xFF);
       	byte secondByte = (byte)((position_raw >>> 16) & 0xFF);
       	byte thirdByte = (byte)((position_raw >>> 8) & 0xFF);
       	byte fourthByte = (byte)(position_raw & 0xFF);
       	spiArrayBuilder(ADDRESS, SET_MOTOR_POSITION, motor, firstByte, secondByte, thirdByte, fourthByte);
       	this.spi.write(spi_array_out);
    }
    
    /**
     * Run both motors
     * 
     * @author Ken Fogel
     * @param power
     * @throws IOException
     */
    public void setBothMotorsPower(byte power) throws IOException {
        spiArrayBuilder(ADDRESS, SET_MOTOR_PWM, (byte) 0x01, power);
        spi.write(spi_array_out);

        spi_array_out[2] = 2; // 1 | 2
        spi.write(spi_array_out);
    }
    
    /**
     * Set the motor target speed in degrees per second
     * 
     * @param motor	The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param dps 	The speed limit in degrees per second, with 0 being no limit
     * @throws IOException
     */
    public void set_motor_dps(byte motor, int dps) throws IOException {
    	dps = (int)(dps * MOTOR_TICKS_PER_DEGREE);
    	byte firstByte = (byte)((dps >>> 8) & 0xFF);
    	byte secondByte = (byte)dps;
    	spiArrayBuilder(ADDRESS, SET_MOTOR_DPS, motor, firstByte, secondByte);
    	spi.write(spi_array_out);
    }
   
    /** 
     * Set the motor speed limit
     * 
     * @param motor	The motor port(s). MOTOR_LEFT and/or MOTOR_RIGHT.
     * @param power The power limit in percent (0 to 100), with 0 being no limit (100)
     * @param dps 	The speed limit in degrees per second, with 0 being no limit
     * @throws IOException
     */
    public void set_motor_limits(byte motor, byte power, int dps) throws IOException {
    	dps = (int)(dps * MOTOR_TICKS_PER_DEGREE);
    	byte firstByte = (byte)((dps >>> 8) & 0xFF);
    	byte secondByte = (byte)(dps & 0xFF);
    	spiArrayBuilder(ADDRESS, SET_MOTOR_LIMITS, motor, power, firstByte, secondByte);
    	spi.write(spi_array_out);
    }
   
    
    /**
     * Overloaded version of set_motor_limits for cases where there is no power limit
     * @param motor
     * @param dps
     * @throws IOException
     */
    public void set_motor_limits(byte motor, int dps) throws IOException {
    	set_motor_limits(motor, (byte)0, dps);
    }


    public void stopMotor(byte motor) throws IOException {
        this.set_motor_power(motor, (byte)0);
    }

    public void stopMotors() throws IOException {
        this.set_motor_power(MOTOR_LEFT, (byte) 0);
        this.set_motor_power(MOTOR_RIGHT, (byte) 0);
    }
    
    /**
     * Read a motor encoder in degrees
     * 
     * @param 	motor
     * @return	The position of the encoder
     * @throws 	IOException
     */
    public int get_motor_encoder(byte motor) throws IOException {
    	byte message_type;
    	if(motor == MOTOR_LEFT) {
    		message_type = GET_MOTOR_ENCODER_LEFT;
    	}
    	else if(motor == MOTOR_RIGHT) {
    		message_type = GET_MOTOR_ENCODER_RIGHT;
    	}
    	else {
    		throw new IOException("Port(s) unsupported. Must be one at a time.");
    	}
    	
    	int encoder = spi_read_32(message_type);
    	return (int)(encoder / MOTOR_TICKS_PER_DEGREE);
    }
    
    public void offset_motor_encoder(byte motor, int offset) throws IOException {
    	offset = (int)(offset * MOTOR_TICKS_PER_DEGREE);
    	spiArrayBuilder(ADDRESS, OFFSET_MOTOR_ENCODER, motor, (byte)((offset >>> 24) & 0xff), (byte)((offset >>> 16) & 0xff), (byte)((offset >>> 8) & 0xff), (byte)(offset & 0xff));
    	spi.write(spi_array_out);
    }
    
    public void reset_motor_encoder(byte motor) throws IOException {
    	if((motor & MOTOR_LEFT) > 0) {
    		offset_motor_encoder(MOTOR_LEFT, get_motor_encoder(MOTOR_LEFT));
    	}
    	
    	if((motor & MOTOR_RIGHT) > 0) {
    		offset_motor_encoder(MOTOR_RIGHT, get_motor_encoder(MOTOR_RIGHT));
    	}
    }
    
    /**
     * Retrieve the name of the manufacturer of the GoPiGo3. Should be Dexter
     * Industries
     * @author Ken Fogel
     * TODO: bugfix this function
     * @return
     */
    public String get_manufacturer() {
        return spi_read_string(GPGSPI_MESSAGE_GET_MANUFACTURER);
    }

    /**
     * Retrieve the firmware version 32 bit
     * @author Ken Fogel
     * @return
     */
    public String get_version_firmware() {
        int data;
        // assign error to the value returned by spi_read_32, and if not 0:
        data = spi_read(GPGSPI_MESSAGE_GET_FIRMWARE_VERSION);

        //return String.format("%d.%d.%d", (data / 1000000), ((data / 1000) % 1000), (data % 1000));
        return String.format("%d.%d.%d", (data), data, data);
    }
    /**
     * Retrieve the battery voltage
     * TODO: bugfix this function too
     * @return
     */
    public double get_voltage_battery() {
    	
    	int returnval = (spi_read_16(GET_VOLTAGE_VCC));
    	return (double)((double)returnval/1000);
    }
  
    
    /**
     * Set an LED
     * 
     * @param led	LED_LEFT_EYE, LED_RIGHT_EYE, LED_LEFT_BLINKER, LED_RIGHT_BLINKER, and/or LED_WIFI.
     * @param red	The LED's Red color component (0-255)
     * @param green	The LED's Green color component (0-255)
     * @param blue	The LED's Blue color component (0-255)
     * @throws IOException
     */
    public void set_led(int led, int red, int green, int blue) throws IOException {
    	if(led < 0 || led > 255) {
    		return;
    	}
    	
    	if(red > 255) {
    		red = 255;
    	}
    	if(green > 255) {
    		green = 255;
    	}
    	if(blue > 255) {
    		blue = 255;
    	}
    	
    	if(red < 0) {
    		red = 0;
    	}
    	if(green < 0) {
    		green = 0;
    	}
    	if(blue < 0) {
    		blue = 0;
    	}
    	
    	spiArrayBuilder(ADDRESS, SET_LED, (byte)led, (byte)red, (byte)green, (byte)blue);
    	spi.write(spi_array_out);
    }
    
    
    /**
     * Treats the return value from writing to the spi as a string. The string
     * begins at index 4 in the spi_array_in. If the spi_array_in[3] equals -91
     * then the information requested is invalid.
     * @author Ken Fogel
     * @param msg_type
     * @return
     */
    private String spi_read_string(byte msg_type) {

        Arrays.fill(spi_array_out, (byte) 0);
        StringBuilder str = new StringBuilder();
        spiArrayBuilder(ADDRESS, msg_type);
        try {
            spi_array_in = spi.write(spi_array_out);
        } catch (IOException ex) {
            LOG.log(Level.SEVERE, "Error writing to spi.", ex);
        }

        // Check for invalid value in array
        if (spi_array_in[3] != -91) {
            return "ERROR_SPI_RESPONSE";
        }

        // Convert array into a string
        for (int i = 0; i < (LONGEST_SPI_TRANSFER - 5); i++) {
            str.append((char) spi_array_in[i + 4]);
        }
        return str.toString();
    }
    

    /**
     * Read an 8-bit value over SPI
     * @author Ken Fogel
     * @param msg_type
     * @return
     */
    private int spi_read(byte msg_type) {

        Arrays.fill(spi_array_out, (byte) 0);
        spiArrayBuilder(ADDRESS, msg_type);
        try {
            spi_array_in = spi.write(spi_array_out);
        } catch (IOException ex) {
            LOG.log(Level.SEVERE, "Error writing to spi.", ex);
        }

        if (spi_array_in[3] != -91) {
            return ERROR_SPI_RESPONSE;
        }
        //LOG.log(Level.INFO, "8 spi_array_in[4]:{0}", (int) spi_array_in[4] & 0xff);
        return spi_array_in[4];
    }
    
    /**
     * Synonym to spi_read
     * 
     * @param msg_type
     * @return
     */
    private int spi_read_8(byte msg_type) {
    	return spi_read(msg_type);
    }
    
    /**
     * Read a 16-bit value over SPI
     * 
     * @param msg_type
     * @return
     */
    private int spi_read_16(byte msg_type) {

        Arrays.fill(spi_array_out, (byte) 0);
        spiArrayBuilder(ADDRESS, msg_type);
        try {
            spi_array_in = spi.write(spi_array_out);
        } catch (IOException ex) {
            LOG.log(Level.SEVERE, "Error writing to spi.", ex);
        }

        if (spi_array_in[3] != -91) {
            return ERROR_SPI_RESPONSE;
        }
        int returnval = (int) (((spi_array_in[4] << 8)&0xFF00)|(spi_array_in[5]&0x00FF));
        //LOG.log(Level.INFO, "8 spi_array_in[4]:{0}", (returnval & 0xff));
        return returnval;
    }
    
    /**
     * Read a 32-bit value over SPI
     * 
     * @param msg_type
     * @return
     */
    private int spi_read_32(byte msg_type) {

        Arrays.fill(spi_array_out, (byte) 0);
        spiArrayBuilder(ADDRESS, msg_type);
        try {
            spi_array_in = spi.write(spi_array_out);
        } catch (IOException ex) {
            LOG.log(Level.SEVERE, "Error writing to spi.", ex);
        }

        if (spi_array_in[3] != -91) {
            return ERROR_SPI_RESPONSE;
        }
        int returnval = (((spi_array_in[4]&0xff) << 24)| ((spi_array_in[4]&0xff) << 16) | ((spi_array_in[6]&0xff) << 8) | (spi_array_in[7]&0xff));
        //LOG.log(Level.INFO, "8 spi_array_in[4]:{0}", (returnval & 0xff));
        return returnval;
    }


    public void set_grove_type(byte port, byte type) throws IOException {
    	for(byte p = 0; p < 2; p++) {
    		if(((port >> (p*2)) & 3) == 3) {
    			GroveType[p] = type;
    		}
    	}
    	spi_array_builder(ADDRESS, SET_GROVE_TYPE, port, type);
    	spi_array_in = spi.write(spi_array_out);
    }
    
    public void set_grove_mode(byte pin, byte mode) throws IOException {
    	spi_array_builder(ADDRESS, SET_GROVE_MODE, pin, mode);
    	spi_array_in = spi.write(spi_array_out);
    }
    
    /**
     * Get a grove input pin state
     * @param pin
     * @return
     * @throws IOException
     */
    public byte get_grove_state(byte pin) throws IOException {
    	byte message_type;
    	if(pin == GROVE_1_1) {
    		message_type = 	GET_GROVE_STATE_1_1;
    	}
    	else if(pin == GROVE_1_2) {
    		message_type = 	GET_GROVE_STATE_1_2;
    	}
    	else if(pin == GROVE_2_1) {
    		message_type = 	GET_GROVE_STATE_2_1;
    	}
    	else if(pin == GROVE_2_2) {
    		message_type = 	GET_GROVE_STATE_2_2;
    	}
    	else throw new IOException("get_grove_state error: Pin(s) unsupported. Must be one at a time.");
    	
    	spi_array_builder(ADDRESS, message_type, (byte)0, (byte)0, (byte)0, (byte)0);
    	spi_array_in = spi.write(spi_array_out);
    	if(spi_array_in[3] == 0xA5) {
    		if(spi_array_in[4] == GROVE_STATE.VALID_DATA.value()) { //no error
    			return spi_array_in[5];
    		}
    		else throw new IOException("get_grove_state error: Invalid value received");
    	}
    	else throw new IOException("get_grove_state error: No SPI Response");	
    }
    
    /**
     * Get a grove input pin 12-bit raw ADC reading
     * @param pin
     * @return
     * @throws IOException
     */
    public int get_grove_analog(byte pin) throws IOException {
    	byte message_type;
    	if(pin == GROVE_1_1) {
    		message_type = 	GET_GROVE_ANALOG_1_1;
    	}
    	else if(pin == GROVE_1_2) {
    		message_type = 	GET_GROVE_ANALOG_1_2;
    	}
    	else if(pin == GROVE_2_1) {
    		message_type = 	GET_GROVE_ANALOG_2_1;
    	}
    	else if(pin == GROVE_2_2) {
    		message_type = 	GET_GROVE_ANALOG_2_2;
    	}
    	else throw new IOException("get_grove_analog error: Pin(s) unsupported. Must be one at a time.");
    	
    	spi_array_builder(ADDRESS, message_type, (byte)0, (byte)0, (byte)0, (byte)0);
    	spi_array_in = spi.write(spi_array_out);
    	if(spi_array_in[3] == 0xA5) {
    		if(spi_array_in[4] == GROVE_STATE.VALID_DATA.value()) { //no error
    			int returnval = (((spi_array_in[5] << 8) & 0xFF00) | (spi_array_in[6] & 0xFF));
    			return returnval;
    		}
    		else throw new IOException("get_grove_analog error: Invalid value received");
    	}
    	else throw new IOException("get_grove_analog error: No SPI Response");	
    }
    
    /**
     * Set grove output pin PWM
     * @param pin
     * @param duty
     */
    public void set_grove_pwm_duty(byte pin, double duty) throws IOException {
    	if(duty < 0) { duty = 0; }
    	if(duty > 100) { duty = 100; }
    	int duty_value = (int)(duty*10.0);
    	byte firstByte = (byte)((duty_value >>> 8) & 0xFF);
    	byte secondByte = (byte)duty_value;
    	spi_array_builder(ADDRESS, SET_GROVE_PWM_DUTY, pin, firstByte, secondByte);
    	spi_array_in = spi.write(spi_array_out);
    }
    
    /**
     * Set grove PWM frequency
     * @param port
     * @param freq
     */
    public void set_grove_pwm_frequency(byte port, int freq) throws IOException {
    	if(freq < 3) { freq = 3; }
    	if(freq > 48000) { freq = 48000; }
    	byte firstByte = (byte)((freq >>> 8) & 0xFF);
    	byte secondByte = (byte)freq;
    	spi_array_builder(ADDRESS, SET_GROVE_PWM_FREQUENCY, port, firstByte, secondByte);
    	spi_array_in = spi.write(spi_array_out);
    }
}
