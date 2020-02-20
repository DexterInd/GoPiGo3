package com.dexterindustries.gopigo3driver;

import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;
import java.util.Arrays;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

/**
 * Base class for all sensors. Should only be instantiated through the use of an EasyGoPiGo3 object.
 * 
 * 
 * WARNING:
 * 1. This class should only be used by the developers of the GoPiGo3 platform.
 * 2. The name of this class isn't representative of the devices it connects to - we also use this class to handle simple outputs such as LEDs.
 * @author Evangeline Joron-Parrot
 *
 */
public class Sensor {
	private String port;
	private String pinmode;
	private byte pin = (byte)1;
	private byte portID;
	protected GoPiGo3 gpg;
	private boolean use_mutex;
	private String descriptor;
	
	/**
	 * Constructor for creating a connection to one of the ports on the GoPiGo3.
	 * @param port can take the following string values: 
	 * "AD1" for digital and analog pinmodes
	 * "AD2" for digital and analog pinmodes
	 * "SERVO1" for OUTPUT pinmode
	 * "SERVO2" for OUTPUT pinmode
	 * "I2C" (pinmode is irrelevant here)
	 * "SERIAL" (pinmode is irrelevant here)
	 * 
	 * @param pinmode can take the following string values:
	 * "INPUT" for general purpose input.
	 * "OUTPUT for general purpose output.
	 * "DIGITAL_INPUT" for digital inputs (the port can only detect 0 and 1)
	 * "DIGITAL_OUTPUT" for digital outputs (the port can only send 0 and 1)
	 * "US" for the ultrasonic sensor
	 * "IR" for the infrared retriever
	 * 
	 * @param gpg3 an instance of a gopigo3 object.
	 * @param use_mutex should be set to true if your program uses multiple sensors at the same time, otherwise should be false.
	 * @throws IOException
	 */
	public Sensor(String port, String pinmode, GoPiGo3 gpg3, boolean use_mutex) throws IOException {
		this.gpg = gpg3;
		set_port(port);
		set_pin_mode(pinmode);
		this.use_mutex = use_mutex;
		reconfig_bus();
	}
	
	/**
	 * Constructor for creating a connection to one of the ports on the GoPiGo3.
	 * @param port can take the following string values: 
	 * "AD1" for digital and analog pinmodes
	 * "AD2" for digital and analog pinmodes
	 * "SERVO1" for OUTPUT pinmode
	 * "SERVO2" for OUTPUT pinmode
	 * "I2C" (pinmode is irrelevant here)
	 * "SERIAL" (pinmode is irrelevant here)
	 * 
	 * @param pinmode can take the following string values:
	 * "INPUT" for general purpose input.
	 * "OUTPUT for general purpose output.
	 * "DIGITAL_INPUT" for digital inputs (the port can only detect 0 and 1)
	 * "DIGITAL_OUTPUT" for digital outputs (the port can only send 0 and 1)
	 * "US" for the ultrasonic sensor
	 * "IR" for the infrared retriever
	 * 
	 * @param gpg3 an instance of a gopigo3 object.
	 * @throws IOException
	 */
	public Sensor(String port, String pinmode, GoPiGo3 gpg3) throws IOException {
		this.gpg = gpg3;
		set_port(port);
		set_pin_mode(pinmode);
		this.use_mutex = false;
		reconfig_bus();
	}
	
	/**
	 * Sets the bus properly. Sometimes this needs to be done even after initialization when two processes are trying to connect and one reinitializes the parts.
	 * @throws IOException
	 */
	public void reconfig_bus() throws IOException {
		if(pinmode.equals("INPUT")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.CUSTOM.value());
			gpg.set_grove_mode(portID, GROVE_INPUT_ANALOG);
		}
		else if(pinmode.equals("DIGITAL_INPUT")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.CUSTOM.value());
			gpg.set_grove_mode(portID, GROVE_INPUT_DIGITAL);
		}
		else if(pinmode.equals("OUTPUT")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.CUSTOM.value());
			gpg.set_grove_mode(portID, GROVE_OUTPUT_PWM);
		}
		else if(pinmode.equals("DIGITAL_OUTPUT")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.CUSTOM.value());
			gpg.set_grove_mode(portID, GROVE_OUTPUT_DIGITAL);
		}
		else if(pinmode.equals("US")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.US.value());
			
		}
		else if(pinmode.equals("IR")) {
			gpg.set_grove_type(portID, GoPiGo3.GROVE_TYPE.IR_DI_REMOTE.value());
		}
		
	}
	
	/**
	 * Selects one of the 2 available pins of the grove connector.
	 * @param pin 1 for the exterior pin of the grove connector, anything else for the interior.
	 */
	public void set_pin(int pin) {
		if(port.equals("AD1")) {
			if(pin == 1) {
				pin = GROVE_1_1;
			}
			else {
				pin = GROVE_1_2;
			}
		}
		else if(port.equals("AD2")) {
			if(pin == 1) {
				pin = GROVE_2_1;
			}
			else {
				pin = GROVE_2_2;
			}
		}
	}
	
	/**
	 * Returns the pin
	 * @return byte representing the pin
	 */
	public byte get_pin() {
		return pin;
	}
	
	/**
	 * Sets the port that is to be used by our new device.
	 * Again, we can't communicate with our device, 
	 * because the class doesn't have any methods for interfacing with it, 
	 * so we need to create a derived class that does this.
	 * @param port
	 */
	public void set_port(String port) {
		this.port = port;
		if(port.equals("AD1")) {
			this.portID = GROVE_1;
		}
		else if(port.equals("AD2")) {
			this.portID = GROVE_2;
		}
		else if(port.equals("SERIAL")) {
			this.portID = (byte)-1;
		}
		else if(port.equals("I2C")) {
			this.portID = (byte)-2;
		}
		else if(port.equals("SERVO1")) {
			this.portID = SERVO_1;
		}
		else if(port.equals("SERVO2")) {
			this.portID = SERVO_2;
		}
		else this.portID = (byte)-5;
	}
	
	/**
	 * Returns the port
	 * @return a string representing the port
	 */
	public String get_port() {
		return port;
	}
	/**
	 * Returns the port id
	 * @return a byte representing the port ID
	 */
	public byte get_port_id() {
		return portID;
	}
	/**
	 * Sets the descriptor of the object. Technically irrelevant except for toString().
	 * @param desc
	 */
	public void set_descriptor(String desc) {
		descriptor = desc;
	}
	/**
	 * Sets the pin mode.
	 * @param pinmode can take the following string values:
	 * "INPUT" for general purpose input.
	 * "OUTPUT for general purpose output.
	 * "DIGITAL_INPUT" for digital inputs (the port can only detect 0 and 1)
	 * "DIGITAL_OUTPUT" for digital outputs (the port can only send 0 and 1)
	 * "US" for the ultrasonic sensor
	 * "IR" for the infrared retriever
	 */
	public void set_pin_mode(String pinmode) {
		this.pinmode = pinmode;
	}
	
	/**
	 * Returns the pinmode
	 * @return a string representing the pin mode
	 */
	public String get_pin_mode() {
		return pinmode;
	}
	
	/**
	 * Prints out a short summary of the sensor's attributes.
	 * 
	 * @return a string with a summary of the object's attributes.
	 * The returned string is made of the following components:
	 * 	The descriptor
	 * 	The port name
	 * 	The pin identifier
	 * 	The port ID
	 * 
	 */
	@Override
	public String toString() {
		return (descriptor + " on port " + get_port() + "\nPinmode: "+ get_pin_mode() + "\nPortID: " + get_port_id());
	}
	
}