package com.dexterindustries.gopigo3driver;

import java.io.IOException;

public class Led extends AnalogSensor {
	/**
	 * Constructor for initializing a Led object
	 * @param port can be either "AD1" or "AD2", depending on the port the LED is plugged into.
	 * @param gpg an instance of a gopigo3 object
	 * @param use_mutex when using multiple sensors in parallel, mutexes should be enabled.
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public Led(String port, GoPiGo3 gpg, boolean use_mutex) throws IOException, InterruptedException {
		super(port, "OUTPUT", gpg, use_mutex);
		set_descriptor("LED");
	}
	
	/**
	 * Sets the light to a specified power, in percent.
	 * @param power Number from 0 to 100 that represents the power you wish the LED to shine at. Decimals are permitted, but any increment smaller than 0.1 will be ignored.
	 * @throws IOException
	 */
	public void light_on(double power) throws IOException {
		write(power);
	}
	
	/**
	 * Sets the light to maximum brightness.
	 * @throws IOException
	 */
	public void light_max() throws IOException  {
		max_value = 100;
		write(100.0);
	}
	
	/**
	 * Turns the light off.
	 * @throws IOException
	 */
	public void light_off() throws IOException  {
		write(0.0);
	}
	
	/**
	 * Returns true if the LED is currently on, and false if it isn't. 
	 * @return a boolean representing the current state of the LED.
	 * @throws IOException
	 */
	public boolean is_on() throws IOException  {
		return (value > 0);
	}
	
	/**
	 * Returns true if the LED is currently off, and false if it isn't. 
	 * @return a boolean representing the current state of the LED.
	 * @throws IOException
	 */
	public boolean is_off() throws IOException  {
		return (value == 0);
	}
}
