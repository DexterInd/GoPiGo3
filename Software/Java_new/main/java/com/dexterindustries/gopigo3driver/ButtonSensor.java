package com.dexterindustries.gopigo3driver;

import java.io.IOException;

public class ButtonSensor extends DigitalSensor {
	/**
	 * Constructor for initializing a ButtonSensor object
	 * @param port can be either "AD1" or "AD2", depending on the port the LED is plugged into.
	 * @param gpg an instance of a gopigo3 object
	 * @param use_mutex when using multiple sensors in parallel, mutexes should be enabled.
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public ButtonSensor(String port, GoPiGo3 gpg, boolean use_mutex) throws IOException, InterruptedException {
		super(port, "DIGITAL_INPUT", gpg, use_mutex);
		set_descriptor("BUTTON");
	}
	
	/**
	 * Checks if the button is pressed.
	 * Note that in the case where SPI reading fails for whatever reason, this function will silently return false.
	 * @return true if the button is currently being hold down, false if it isn't.
	 * @throws IOException
	 */
	public boolean is_button_pressed() throws IOException {
		return (read() == 1);
	}
}
