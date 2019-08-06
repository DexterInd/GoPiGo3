package com.dexterindustries.gopigo3driver;

import java.time.Duration;
import java.time.Instant;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

public class Demo {

    public static void main(String[] args) throws Exception {

        System.out.println("GoPiGo3 Demo");

        EasyGoPiGo3 platform = new EasyGoPiGo3();
        LoudnessSensor castafiore = platform.init_loudness_sensor("AD1");
        System.out.println(castafiore.read());
    }
}
