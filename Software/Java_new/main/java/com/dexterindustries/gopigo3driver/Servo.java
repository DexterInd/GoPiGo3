package com.dexterindustries.gopigo3driver;

import java.io.IOException;

public class Servo extends Sensor {
	private static int PULSE_WIDTH_RANGE = 1850;
	
	/**
	 * Constructor for initializing a servo object
	 * @param port can be either "SERVO1" or "SERVO2"
	 * @param gpg an instance of a gopigo3 object
	 * @param use_mutex when using multiple sensors in parallel, mutexes should be enabled.
	 * @throws IOException
	 * @throws InterruptedException
	 */
	public Servo(String port, GoPiGo3 gpg, boolean use_mutex) throws IOException, InterruptedException {
		super(port, "OUTPUT", gpg, use_mutex);
		set_descriptor("SERVO");
	}
	
	/**
	 * Rotates the servo to a specific angle.
	 * 
	 * The pulse width here is in microseconds and varies int he following way:
	 * 0 degrees = 575 uS.
	 * 180 degrees = 24250 uS.
	 * Thankfully, this function accepts inputs in degrees.
	 * @param servo_position the target position in degrees.
	 * @throws IOException
	 */
	public void rotate_servo(double servo_position) throws IOException {
		if(servo_position > 180) {
			servo_position = 180;
		}
		if(servo_position < 0) {
			servo_position = 0;
		}
		
		int pulsewidth = (int)((1500 - (PULSE_WIDTH_RANGE/2)) + ((PULSE_WIDTH_RANGE/180) * servo_position));
		gpg.set_servo(get_port_id(), pulsewidth);
	}
	
	/**
	 * Resets the servo straight ahead.
	 * @throws IOException
	 */
	public void reset_servo() throws IOException {
		rotate_servo(90);
	}
	
	/**
	 * Disables the servo. The purpose of this command is so that if you try to turn the servo manually, it won't resist you.
	 * @throws IOException
	 */
	public void disable_servo() throws IOException {
		gpg.set_servo(get_port_id(), 0);
	}
}
