package com.dexterindustries.gopigo3driver;

import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;
import java.util.Arrays;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

public class AnalogSensor extends Sensor {
	protected double value = 0;
	protected int freq = 24000;
	protected int max_value = 4096;
	
	/**
	 * Constructor for creating an analog connection to one of the ports on the GoPiGo3.
	 * 
	 * @param port can take the following string values: 
	 * "AD1" for digital and analog pinmodes
	 * "AD2" for digital and analog pinmodes
	 * 
	 * @param pinmode can take the following string values:
	 * "INPUT" for general purpose input.
	 * "OUTPUT for general purpose output.
	 * "US" for the ultrasonic sensor
	 * "IR" for the infrared retriever
	 * 
	 * @param gpg3 an instance of a gopigo3 object.
	 * @throws IOException
	 */
	public AnalogSensor(String port, String pinmode, GoPiGo3 gpg3, boolean use_mutex) throws IOException, InterruptedException {
		super(port, pinmode, gpg3, use_mutex);
		Thread.sleep(10); //delay needed by at least the light sensor
	}
	
	/**
	 *  Reads analog value of the sensor that's connected to our GoPiGo3 robot.
	 *  
	 * @return	 12-bit number representing the voltage we get from the sensor. Range goes from 0V-5V.
	 */
	public double read() throws IOException {
		try {
			value = gpg.get_grove_analog(this.get_pin());
		}
		catch(Exception e){
			System.out.println("Analog read fail: "+e.toString());
			return 0;
		}
		return value;
	}
	
	/**
	 * Reads the value of the sensor that's connected to our GoPiGo3 robot, and outputs it as a percent.
	 * @return int representing the percent of max value read from the sensor
	 * @throws IOException
	 */
	public int read_percent() throws IOException {
		int reading_percent = (int)((read()*100) / max_value);
		if(reading_percent > 100) {
			reading_percent = 100;
		}
		return reading_percent;
	}
	
	/**
	 * Generates a PWM signal on the selected port.
	 * Good for simulating a DAC converter: for instance a LED is a good candidate.
	 * @param power Number from 0 to 100 that represents the duty cycle as a percentage of the frequency's period. Decimals are permitted, but any increment smaller than 0.1 will be ignored.
	 * @throws IOException
	 */
	public void write(double power) throws IOException {
		value = power;
		gpg.set_grove_pwm_duty(get_pin(), power);
	}
	
	/**
	 * Sets the frequency of the PWM signal.
	 * @param freq Frequency of the PWM signal you wish to set. Range goes from 3Hz to 48000Hz. Default value is set to 24000Hz.
	 * @throws IOException
	 */
	public void write_freq(int freq) throws IOException {
		this.freq = freq;
		gpg.set_grove_pwm_frequency(get_port_id(), freq);
	}
	
}