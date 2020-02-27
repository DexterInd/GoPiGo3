package com.dexterindustries.gopigo3driver;

import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;
import java.util.Arrays;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

public class DigitalSensor extends Sensor {
	protected int value; //can be 0 or 1, or sometimes -1 when reading fails.
	/**
	 * Constructor for creating an analog connection to one of the ports on the GoPiGo3.
	 * 
	 * @param port can take the following string values: 
	 * "AD1" for digital and analog pinmodes
	 * "AD2" for digital and analog pinmodes
	 * 
	 * @param pinmode can take the following string values:
	 * "DIGITAL_INPUT" for digital inputs (the port can only detect 0 and 1)
	 * "DIGITAL_OUTPUT" for digital outputs (the port can only send 0 and 1)
	 * 
	 * @param gpg3 an instance of a gopigo3 object.
	 * @throws IOException
	 */
	public DigitalSensor(String port, String pinmode, GoPiGo3 gpg3, boolean use_mutex) throws IOException, InterruptedException {
		super(port, pinmode, gpg3, use_mutex);
	}
	
	/**
	 * Reads a value from the sensor.
	 * @return 0 and 1 are valid values. Returns a -1 if reading fails.
	 * @throws IOException
	 */
	public int read() throws IOException {
		try {
			value = gpg.get_grove_state(this.get_pin());
		}
		catch(Exception e){
			System.out.println("Digital read fail: "+e.toString());
			value = -1;
		}
		return value;
	}
}