package com.dexterindustries.gopigo3driver;

import java.io.IOException;

public class LoudnessSensor extends AnalogSensor {
	/**
	 * Constructor for initializing a ButtonSensor object
	 * @param port can be either "AD1" or "AD2", depending on the port the LED is plugged into.
	 * @param gpg an instance of a gopigo3 object
	 * @param use_mutex when using multiple sensors in parallel, mutexes should be enabled.
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public LoudnessSensor(String port, GoPiGo3 gpg, boolean use_mutex) throws IOException, InterruptedException {
		super(port, "INPUT", gpg, use_mutex);
		set_descriptor("LOUDNESS SENSOR");
	}
	
	
}
