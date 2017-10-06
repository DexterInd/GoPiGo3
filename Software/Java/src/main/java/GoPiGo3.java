import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;

/**
 * Created by jabrena on 20/7/17.
 */
public class GoPiGo3 {

    // SPI device
    public static SpiDevice spi = null;

    public static int MOTOR_LEFT = 1;
    public static int MOTOR_RIGHT = 2;

    public GoPiGo3() throws IOException {

        // create SPI object instance for SPI for communication
        this.spi = SpiFactory.getInstance(SpiChannel.CS1,
                SpiDevice.DEFAULT_SPI_SPEED, // default spi speed 1 MHz
                SpiDevice.DEFAULT_SPI_MODE); // default spi mode 0
    }


    public void runMotor(int motor, int power) throws IOException {

        //TODO Create a Builder
        byte command[] = new byte[] {
                (byte) 8,       // first byte, start bit
                (byte) 10,      // SET_MOTOR_PWM
                (byte) motor,   // 1 | 2
                (byte) power,   // 0 - 100
        };

        this.spi.write(command);
    }

    public void stopMotor(int motor) throws IOException {
        this.runMotor(motor, 0);
    }

    public void stopMotors() throws IOException {
        this.runMotor(MOTOR_LEFT, 0);
        this.runMotor(MOTOR_RIGHT, 0);
    }
}
