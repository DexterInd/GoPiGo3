package com.dexterindustries.gopigo3driver;

import java.io.IOException;

public class Buzzer extends AnalogSensor {
	int power = 50;
	/**
	 * Dictionary of frequencies for each musical note.
	 *
	 */
    public enum SCALE { 
    	A3 (220),
    	A3S (233),
    	B3 (247),
    	C4 (261),
    	C4S (277),
    	D4 (293),
    	D4S (311),
    	E4 (329),
    	F4 (370),
    	F4S (370),
    	G4 (392),
    	G4S (415),
    	A4 (440),
    	A4S (466),
    	B4 (494),
    	C5 (523),
    	C5S (554),
    	D5 (587),
    	D5S (622),
    	E5 (659),
    	F5 (698),
    	F5S (740),
    	G5 (784),
    	G5S (831);
    	
    	private final int value;
    	
    	SCALE(int value) {
    		this.value = value;
    	}
    	
    	public int value() { return value; };
    }

    /**
     * Constructor for initializing a buzzer object.
     * Normally, this should be called by the init_buzzer() function of EasyGoPiGo3.
	 * @param port can be either "AD1" or "AD2", depending on the port the LED is plugged into.
	 * @param gpg an instance of a gopigo3 object
	 * @param use_mutex when using multiple sensors in parallel, mutexes should be enabled.
	 * @throws IOException
	 * @throws InterruptedException
	 */
    public Buzzer(String port, GoPiGo3 gpg, boolean use_mutex) throws IOException, InterruptedException {
    	super(port, "OUTPUT", gpg, use_mutex);
    	set_pin(1);
    	set_descriptor("Buzzer");
    	freq = 329;
    	//sound_off();
    }
    
    /**
     * Sets a musical note to come from the buzzer.
     * You can use any number you wish for the musical note, but you can use the defined scale to make it easier.
     * In that case, the function call would look like this:
     * buzz.sound(Buzzer.SCALE.A4.value());
     * @param freq the frequency you wish the buzzer to sound at
     * @throws IOException
     */
    public void sound(int freq) throws IOException {
    	if(freq <= 0) {
    		power = 0;
    		freq = 0;
    	}
    	else {
    		power = 50;
    	}
    	
    	if (power == 50) {
    		write_freq(freq);
    	}
    	write(power);
    }
    
    /**
     * Shuts off the buzzer.
     * @throws IOException
     */
    public void sound_off() throws IOException {
    	sound(0);
    }
}
