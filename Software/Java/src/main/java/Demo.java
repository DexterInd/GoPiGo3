import java.time.Duration;
import java.time.Instant;

public class Demo {

    public static void main(String[] args) throws Exception {

        System.out.println("GoPiGo3 Demo");

        GoPiGo3 platform = new GoPiGo3();

        Instant start = Instant.now();

        //Motor Left Power 100
        System.out.println("Running left motor with Power 100");
        platform.runMotor(GoPiGo3.MOTOR_LEFT, 100);

        //Motor Right Power 100
        System.out.println("Running right motor with Power 100");
        platform.runMotor(GoPiGo3.MOTOR_RIGHT, 100);

        System.out.println("Delay 5 seconds");
        Thread.sleep(5000);

        System.out.println("Stop motors");
        platform.stopMotors();

        Instant end = Instant.now();
        System.out.println(Duration.between(start, end));

        System.out.println("End demo");

    }

}
