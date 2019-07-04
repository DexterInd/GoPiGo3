package com.dexterindustries.gopigo3driver;

import java.time.Duration;
import java.time.Instant;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

public class Demo {

    public static void main(String[] args) throws Exception {

        System.out.println("GoPiGo3 Demo");

        EasyGoPiGo3 platform = new EasyGoPiGo3();
        
        platform.reset_encoders(true);
        System.out.println("Battery voltage: " + platform.volt());
        System.out.println("Driving forwards 60cm");
        platform.drive_cm(60, true);

        System.out.println("Turning around");
        platform.turn_degrees(180);
        

        platform.set_eye_color(150, 30, 60);
        System.out.println("Turning blinkers on");
        platform.blinker_on(1);
        platform.blinker_on("right");
        platform.open_eyes();
        
        System.out.println("Orbiting");
        platform.orbit(90, 30, true);
        
        System.out.println("Turning blinkers off");
        platform.blinker_off(0);
        platform.blinker_off("left");
        platform.close_eyes();
        
        System.out.println("Left motor pos: "+platform.get_motor_encoder(MOTOR_LEFT));
        System.out.println("Right motor pos: "+platform.get_motor_encoder(MOTOR_RIGHT));
		
        System.out.println("End demo");

    }

}
