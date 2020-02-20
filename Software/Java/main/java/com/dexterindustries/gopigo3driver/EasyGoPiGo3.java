package com.dexterindustries.gopigo3driver;

import com.pi4j.io.spi.SpiChannel;
import com.pi4j.io.spi.SpiDevice;
import com.pi4j.io.spi.SpiFactory;

import java.io.IOException;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.Arrays;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.*;

import static com.dexterindustries.gopigo3driver.constants.SPI_MESSAGE_TYPE.*;

public class EasyGoPiGo3 extends GoPiGo3 {
    public static SpiDevice spi = null;

    private final byte[] spi_array_out = new byte[32]; //TODO: double check this size
    private byte[] spi_array_in = null;
    private int speed;
    private final int DEFAULT_SPEED = 300;
    private final int NO_LIMIT_SPEED = 1000;
    private int[] left_eye_color = {0, 255, 255};
    private int[] right_eye_color = {0, 255, 255};
    private boolean use_mutex = false;
    
    public EasyGoPiGo3() throws IOException {
    	super();
    	set_speed(DEFAULT_SPEED);
    	try {
    		load_robot_constants();
    	}
    	catch(Exception e) {
    		//No notification
    	}
    }
    
    /**
     * Load wheel diameter and wheel base width constants for the GoPiGo3 from file. These constants are used to calculate the amount of power each motor needs to have in order to achieve specific tasks.
     * The constructor automatically calls this method with the default file path. If you wish to use a different file, you must call this method individually.
     * 
     * Here's how the JSON config file must look like before reading it. Obviously, the supported format is JSON so that anyone can come in
     * and edit their own config file if they don't want to go through saving the values by using the API.
     * {
      		"wheel-diameter": 66.5,
      		"wheel-base-width": 117
       }
     * 
     * @param config_file_path Path to JSON config file that stores the wheel diameter and wheel base width for the GoPiGo3. Optional parameter, default is /home/pi/Dexter/gpg3_config.json
     * @throws IOException if file is not found or cannot be opened
     * @throws ParseException if the file format is incorrect
     */
    public void load_robot_constants(String config_file_path) throws IOException, ParseException {
    	JSONParser parser = new JSONParser();
    	JSONObject obj = (JSONObject) parser.parse(new FileReader(config_file_path));
    	double diameter = double_value(obj.get("wheel-diameter"));
    	double width = double_value(obj.get("wheel-base-width"));
    	if(diameter > 0 && width > 0) {
    		set_robot_constants(diameter, width);
    	}
    }
    
    /**
     * Load wheel diameter and wheel base width constants for the GoPiGo3 from the default file, located at /home/pi/Dexter/gpg3_config.json
     * 
     * Here's how the JSON config file must look like before reading it. Obviously, the supported format is JSON so that anyone can come in
     * and edit their own config file if they don't want to go through saving the values by using the API.
     * {
      		"wheel-diameter": 66.5,
      		"wheel-base-width": 117
       }
     * 
     * @throws IOException if file is not found or cannot be opened
     * @throws ParseException if the file format is incorrect
     */
    public void load_robot_constants() throws IOException, ParseException {
    	load_robot_constants("/home/pi/Dexter/gpg3_config.json");
    }
    
    /**
     * Set new wheel diameter and wheel base width values for the GoPiGo3.
     * 
     * @param wheel_diameter Diameter of the GoPiGo3 wheels as measured in centimeters.
     * @param wheel_base_width Distance between the centers of the two wheels as measured in centimeters.
     */
    private void set_robot_constants(double wheel_diameter, double wheel_base_width) {
    	WHEEL_DIAMETER = wheel_diameter;
    	WHEEL_BASE_WIDTH = wheel_base_width;
    	WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * Math.PI;
    	WHEEL_BASE_CIRCUMFERENCE = WHEEL_BASE_WIDTH * Math.PI;
    }
    
    /**
     * Returns an array including the robot constants.
     * @return array of doubles of length 2. In this array, [0] is equal to the current wheel diameter constant and [1] is equal to the current wheel base width.
     */
    public double[] get_robot_constants() {
    	double[] i = new double[2];
    	i[0] = WHEEL_DIAMETER;
    	i[1] = WHEEL_BASE_WIDTH;
    	return i;
    }
    
    /**
     * Saves the current robot parameters to a json file that can be loaded later.
     * @param config_file_path Path to JSON config file that stores the wheel diameter and wheel base width for the GoPiGo3. Optional parameter, default is /home/pi/Dexter/GoPiGo3.json
     * @throws IOException when the file cannot be accessed, or if the file cannot be written to
     * @throws ParseException when the file is not in the correct format
     */
    @SuppressWarnings("unchecked") //compiler here gives a warning for obj.put() as the JSONObject classes uses generic types.
    //We know that we're only giving it String, double arguments that are going to be legal at runtime, so suppressing this warning is fine.
    public void save_robot_constants(String config_file_path) throws IOException, ParseException {
    	JSONParser parser = new JSONParser();
    	JSONObject obj = (JSONObject) parser.parse(new FileReader(config_file_path));
    	//first remove the existing values
    	obj.remove("wheel-diameter");
    	obj.remove("wheel-base-width");
    	//then add the new ones
    	double[] i = get_robot_constants();
    	obj.put("wheel-base-width", i[1]);
    	obj.put("wheel_diameter", i[0]);
    	//write the file
    	try(FileWriter writer = new FileWriter(config_file_path, false)) {
    		writer.write(obj.toJSONString());
    		writer.flush();
    	}
    	catch(IOException e) {
    		throw new IOException("File could not be written to.");
    	}
    }
    
    /**
     * Saves the current robot parameters to the default json file for future access.
     * 
     * @throws IOException when the file cannot be accessed, or if the file cannot be written to
     * @throws ParseException when the file is not in the correct format
     */
    public void save_robot_constants() throws IOException, ParseException {
    	save_robot_constants("/home/pi/Dexter/gpg3_config.json");
    }
    
    /**
     * Helper method that returns the value of an object as a double.
     * Used to avoid errors with round numbers in JSON being interpreted as long.
     * @param the object you wish to evauate
     * @return a double corresponding to the value of the object you pass. returns -1 if invalid.
     */
    private static double double_value(Object value) {
    	return 	(value instanceof Number ? ((Number)value).doubleValue() : -1.0);
    }
    
    /**
     * This method returns the battery voltage of the GoPiGo3.
     * 
     * @return the voltage as a double, in decimals. For a fully charged battery, this should be around 9.2 to 9.6V, but different batteries may vary.
     */
    public double volt() {
    	return get_voltage_battery();
    }
    
    /**
     * Sets the speed of both motors to a specified number in degrees per second (of the robot's wheel turning).
     * NOTE: This function on its own does not start the motors. You should call this function first to set the desired speed, then call forward().
     * WARNING: 0-1000 DPS is the preferred speed under standard conditions, but you may set it to any number you wish. 
     * Factors such as battery voltage and robot load may affect what speed the robot actually works at.
     * Experiments should be run by every user, as every situation is different.
     * 
     * @param in_speed The speed at which the robot is set to run. int values only. Generally should range between 0 to 1000. Any value above 32 767 will be capped down (not that the robot is capable of going at that speed under normal conditions).
     * @throws IOException if spi contact with the motor fails
     */
    public void set_speed(int in_speed) throws IOException {
    	if(in_speed > Short.MAX_VALUE) {
    		in_speed = Short.MAX_VALUE;
    	}
    	speed = in_speed;
    	set_motor_limits(MOTOR_BOTH, (byte)0, (short)speed);
    }

    
    /**
     * Gets the current speed the GoPiGo3 robot is current set to. Note that this is NOT necessarily the speed your robot is actually moving at in reality.
     * For example, you may call this method while the robot isn't moving.
     * @return	speed	the current speed
     */
    public int get_speed() {
    	return speed;
    }
    
    /**
     * Resets the speed of the robot to its default value.
     * @throws IOException if spi contact with the motors fails.
     */
    public void reset_speed() throws IOException {
    	set_speed(DEFAULT_SPEED);
    }
     
    /**
     * This method brings the GoPiGo3 robot to a full stop. Used in conjunction with the other methods such as forward().
     * @throws IOException if spi contact with the motors fails.
     */
    public void stop() throws IOException {
    	set_motor_dps(MOTOR_BOTH, (short)0);
    }
    
    /**
     * Moves the robot forward at the speed set with set_speed().
     * Default speed is set to 300.
     * @throws IOException if spi contact with the motors fails.
     */
    public void forward() throws IOException  {
    	set_motor_dps(MOTOR_BOTH, NO_LIMIT_SPEED);
    }
    
    /**
     * Moves robot backward at the speed set with set_speed(). Essentially just a reverse of forward().
     * @throws IOException if spi contact with the motors fails.
     */
    public void backward() throws IOException  {
    	set_motor_dps(MOTOR_BOTH, (NO_LIMIT_SPEED * -1));
    }
    
    /**
     * Turns left in a very tight circle
     * ONLY the right motor will be engaged, while the left motor will be completely stopped.
     * @throws IOException
     */  
    public void left() throws IOException  {
    	set_motor_dps(MOTOR_RIGHT, (NO_LIMIT_SPEED));
    	set_motor_dps(MOTOR_LEFT, 0);
    }
    
    /**
     * Turns left in place.
     * The right motor will be engaged forward, while the left motor will be engaged at the same speed in reverse. This causes the robot to spin on itself without moving.
     * @throws IOException
     */  
    public void spin_left() throws IOException  {
    	set_motor_dps(MOTOR_RIGHT, (NO_LIMIT_SPEED));
    	set_motor_dps(MOTOR_LEFT, (NO_LIMIT_SPEED * -1));
    }
    
    /**
     * Turns right in a very tight circle
     * Only the left motor will be engaged, while the right motor will be completely stopped.
     * @throws IOException
     */
    public void right() throws IOException  {
    	set_motor_dps(MOTOR_LEFT, (NO_LIMIT_SPEED));
    	set_motor_dps(MOTOR_RIGHT, 0);
    }
    
    /**
     * Turns right in place.
     * The left motor will be engaged forward, while the right motor will be engaged at the same speed in reverse. This causes the robot to spin on itself without moving.
     *
     * @throws IOException
     */
    public void spin_right() throws IOException  {
    	set_motor_dps(MOTOR_LEFT, (NO_LIMIT_SPEED));
    	set_motor_dps(MOTOR_RIGHT, (NO_LIMIT_SPEED*-1));
    }
    
    /**
     * Resets both the encoders back to 0.
     * @param blocking if this is set to true, this method will halt the progress of the program until the encoders are finished resetting. Optional parameter (defaults to true)
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call. This ideally should never be happening as the encoders do need some time to execute the reset.
     */
    public void reset_encoders(boolean blocking) throws IOException, InterruptedException {
    	set_motor_power(MOTOR_BOTH, (byte)0);
    	int left_target = get_motor_encoder(MOTOR_LEFT);
    	int right_target = get_motor_encoder(MOTOR_RIGHT);
    	offset_motor_encoder(MOTOR_LEFT, left_target);
    	offset_motor_encoder(MOTOR_RIGHT, right_target);
    
    	
    	if(blocking) {
    		Thread.sleep(250);
    	}
    }
    /**
     * Resets both encoders to 0, and halts the progress of the program until the operation is done.
     * 
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call
     */
    public void reset_encoders() throws IOException, InterruptedException {
    	reset_encoders(true);
    }
    /**
     *  Move the GoPiGo3 forward / backward for dist amount of centimeters.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param dist The distance you want the robot to go, in cm
     * @param blocking	When set to true, will stop the method until the robot is finished moving.
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call
     */
    public void drive_cm(double dist, boolean blocking) throws IOException, InterruptedException {
    	double dist_mm = dist * 10;
    	double WheelTurnDegrees = ((dist_mm*360) / WHEEL_CIRCUMFERENCE);
    	int StartPositionLeft = get_motor_encoder(MOTOR_LEFT);
    	int StartPositionRight = get_motor_encoder(MOTOR_RIGHT);
    	double TargetPositionLeft = StartPositionLeft + WheelTurnDegrees;
    	double TargetPositionRight = StartPositionRight + WheelTurnDegrees;   	
    	set_motor_position(MOTOR_LEFT, TargetPositionLeft);
    	set_motor_position(MOTOR_RIGHT, TargetPositionRight);
    	
    	
    	if(blocking) {
    		while(target_reached(
    				TargetPositionLeft,
    				TargetPositionRight) == false) {
    			Thread.sleep(1);
    		}
    	}
    }
    /**
     *  Move the GoPiGo3 forward / backward for dist amount of centimeters, and halts the progress of the thread until it is complete.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param dist The distance you want the robot to go, in cm
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call
     */
    public void drive_cm(double dist) throws IOException, InterruptedException {
    	drive_cm(dist, true);
    }
    
    /**
     *  Move the GoPiGo3 forward / backward for dist amount of inches.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param dist The distance you want the robot to go, in cm
     * @param blocking	When set to true, will stop the method until the robot is finished moving.
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call
     */
    public void drive_inches(double dist, boolean blocking) throws IOException, InterruptedException {
    	drive_cm(dist*2.54, blocking);
    }
    
    /**
     *  Move the GoPiGo3 forward / backward for dist amount of inches, and halts the progress of the thread until it is complete.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param dist The distance you want the robot to go, in cm
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this thread is interrupted during the sleep call
     */
    public void drive_inches(double dist) throws IOException, InterruptedException {
    	drive_cm(dist*2.54, true);
    }
    
    /**
     * Move the GoPiGo3 forward / backward for (degrees/360) wheel rotations.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param degrees distance based on the number of wheel rotations made. Decimals are permitted.
     * @param blocking Set as blocking or non-blocking method
     * @throws IOException if spi connection to the motors fails
     * @throws InterruptedException if this thread is interrupted while it is waiting to reach the target
     */
    public void drive_degrees(double degrees, boolean blocking) throws IOException, InterruptedException {
    	int StartPositionLeft = get_motor_encoder(MOTOR_LEFT);
    	int StartPositionRight = get_motor_encoder(MOTOR_RIGHT);
    	double TargetPositionLeft = StartPositionLeft + degrees;
    	double TargetPositionRight = StartPositionRight + degrees;    	
    	set_motor_position(MOTOR_LEFT, TargetPositionLeft);
    	set_motor_position(MOTOR_RIGHT, TargetPositionRight);  	
    	if(blocking) {
    		while(target_reached(
    				TargetPositionLeft,
    				TargetPositionRight) == false) {
    			Thread.sleep(1);
    		}
    	}
    }
    
    /**
     * Move the GoPiGo3 forward / backward for (degrees/360) wheel rotations, and halts the execution of the rest of the program until this is completed.
     *  For moving the GoPiGo3 robot forward, the dist parameter has to be positive.
     *	For moving the GoPiGo3 robot backward, the dist parameter has to be negative.
     * @param degrees distance based on the number of wheel rotations made. Decimals are permitted.
     * @throws IOException if spi connection to the motors fails
     * @throws InterruptedException if this thread is interrupted while it is waiting to reach the target
     */
    public void drive_degrees(double degrees) throws IOException, InterruptedException {
    	drive_degrees(degrees, true);
    }
    
    
    /**
     *  Control each motor in order to get a variety of turning movements.
     *  Each motor is assigned a percentage of the current speed value. 
     *  While there is no limit on the values of left_percent and right_percent parameters,
     *  they are expected to be between -100 and 100.
     * @param left_percent	Percentage of current speed value that gets applied to left motor. The range is between **-100** (for backward rotation) and **100** (for forward rotation).
     * @param right_percent	Percentage of current speed value that gets applied to right motor. The range is between **-100** (for backward rotation) and **100** (for forward rotation).
     * @throws IOException
     */
    public void steer(int left_percent, int right_percent) throws IOException {
    	set_motor_dps(MOTOR_LEFT, (NO_LIMIT_SPEED * left_percent/100));
    	set_motor_dps(MOTOR_RIGHT, (NO_LIMIT_SPEED * right_percent/100));
    }
    
    /**
     * Makes the GoPiGo3 robot turn at a specific angle while staying at the same spot.
     * This is the method you want to use if you want the robot to turn 90 degrees in place, for example.
     * @param degrees The degrees at which the GoPiGo3 has to turn. For rotating to the left, degrees should be negative, and for rotating to the right, degrees should be positive.
     * @param blocking set as blocking or non-blocking method. Optional parameter (defaults to true).
     * @throws IOException if spi connection fails
     * @throws InterruptedException if this method is interrupted while waiting to be completed
     */
    public void turn_degrees(double degrees, boolean blocking) throws IOException, InterruptedException {
    	//distance in mm each wheel needs to travel
    	double WheelTravelDistance = ((WHEEL_BASE_CIRCUMFERENCE * degrees) / 360);
    	
    	//the number of degrees each wheel needs to turn
    	double WheelTurnDegrees = ((WheelTravelDistance / WHEEL_CIRCUMFERENCE) * 360);
    	
    	//get the starting position of each motor
    	int StartPositionLeft = get_motor_encoder(MOTOR_LEFT);
    	int StartPositionRight = get_motor_encoder(MOTOR_RIGHT);
    	
    	//set each motor target
    	set_motor_position(MOTOR_LEFT, (StartPositionLeft + WheelTurnDegrees));
    	set_motor_position(MOTOR_RIGHT, (StartPositionRight - WheelTurnDegrees));
    	
    	if(blocking) {
    		while(target_reached((StartPositionLeft+WheelTurnDegrees), (StartPositionRight-WheelTurnDegrees)) == false) {
    			Thread.sleep(1);
    		}
    	}
    }
    
    /**
     * Makes the GoPiGo3 robot turn at a specific angle while staying at the same spot, and halts execution of the rest of the program until it is finished.
     * This is the method you want to use if you want the robot to turn 90 degrees in place, for example.
     * @param degrees The degrees at which the GoPiGo3 has to turn. For rotating to the left, degrees should be negative, and for rotating to the right, degrees should be positive.
     * @throws IOException
     * @throws InterruptedException
     */
    public void turn_degrees(double degrees) throws IOException, InterruptedException {
    	turn_degrees(degrees, true);
    }
    /**
     * Reads both encoder's postion in degrees. When the wheels do a full rotation, the value should change by 360.
     * @return an array of length 2 containing the value of both encoders. In this array, [0] represents the left encoder and [1] represents the right.
     */
    public int[] read_encoders() throws IOException {
    	int left_encoder = get_motor_encoder(MOTOR_LEFT);
    	int right_encoder = get_motor_encoder(MOTOR_RIGHT);
    	int[] a = {left_encoder,right_encoder};
    	return a;
    }
    
    /**
     * Reads the encoders' position and averages them. 360 degrees represent 1 full rotation (or 360 degrees) of a wheel.
     * You can use this method, for example, to roughly check whether your robot has moved forward or not. If you need specific values, you should use read_encoders().
     * You can change the unit you wish to get your response as by varying the units parameter.
     * @param units	By default it's "cm", but it could also be "in" for inches. Anything else will return raw encoder average.
     * @return The average of the two wheel encoder values.
     */
    public double read_encoders_average(String units) throws IOException {
    	int left = get_motor_encoder(MOTOR_LEFT);
    	int right = get_motor_encoder(MOTOR_RIGHT);
    	double average = (left+right)/2;
    	if(units.equals("cm")) {
    		average = ((average/360) * WHEEL_CIRCUMFERENCE)/10;
    	}
    	else if(units.equals("in")) {
    		average = ((average/360) * WHEEL_CIRCUMFERENCE)/(10*2.54);
    	}
    	
    	return average;
    }
    
    /**
     * Control the GoPiGo so it will orbit around an object.  
     * 
     * Note that while in non-blocking mode the speed cannot be changed before the end of the orbit as it would negate all orbit calculations.
     * WARNING: After a non-blocking call, set_speed() has to be called again before any other movement.
     * @param degrees	Degrees to steer. 360 for full rotation. Negative for left turn.
     * @param radius_cm Radius in `cm` of the circle to drive. Default is 0 (turn in place).
     * @param blocking	Set it as a blocking or non-blocking method.
     * @throws IOException
     * @throws InterruptedException
     */
    public void orbit(double degrees, double radius_cm, boolean blocking) throws IOException, InterruptedException {
    	int speed = get_speed();
    	double radius = radius_cm * 10;
    	
    	//Total distance to drive in mm
    	double drive_distance = Math.PI * Math.abs(radius) * Math.abs(degrees) / 180; // /180 is shorter than radius * 2 / 360
    	
    	//The difference in mm to add to one motor and substract from the other
    	double drive_difference = ((WHEEL_BASE_CIRCUMFERENCE * degrees) / 360);
    	
    	//The number of degrees each wheel needs to turn on average to get the necessary distance
    	double distance_degrees = ((drive_distance / WHEEL_CIRCUMFERENCE) * 360);
    	
    	//The difference in motor travel in degrees
    	double difference_degrees = ((drive_difference / WHEEL_CIRCUMFERENCE) * 360);
    	
    	//The distance each wheel needs to turn
    	double left_target = distance_degrees + difference_degrees;
    	double right_target = distance_degrees - difference_degrees;
    	
    	byte MOTOR_FAST;
    	byte MOTOR_SLOW;
    	double fast_target;
    	double slow_target;
    	//if it's a left turn
    	if(degrees < 0) {
    		MOTOR_FAST = MOTOR_RIGHT;
    		MOTOR_SLOW = MOTOR_LEFT;
    		fast_target = right_target;
    		slow_target = left_target;
    	}
    	else {
    		MOTOR_FAST = MOTOR_LEFT;
    		MOTOR_SLOW = MOTOR_RIGHT;
    		fast_target = left_target;
    		slow_target = right_target;
    	}
    	
    	//determine driving direction from speed
    	int direction = 1;
    	int speed_with_direction = speed;
    	if (speed < 0) {
    		direction = -1;
    		speed_with_direction = speed*(-1);
    	}
    	
    	//calculate the driving speed for each motor
    	int fast_speed = speed_with_direction;
    	int slow_speed = (int)Math.abs((speed_with_direction * slow_target) / fast_target); //floored because speed can only be integers
    	
    	//set the motor speeds
    	set_motor_limits(MOTOR_FAST, fast_speed);
    	set_motor_limits(MOTOR_SLOW, slow_speed);
    	
    	//get the starting positions for each motor
    	int StartPositionLeft = get_motor_encoder(MOTOR_LEFT);
    	int StartPositionRight = get_motor_encoder(MOTOR_RIGHT);
    	
    	//set each motor target position
    	left_target = StartPositionLeft + (left_target * direction);
    	right_target = StartPositionRight + (right_target * direction);
    	set_motor_position(MOTOR_LEFT, left_target);
    	set_motor_position(MOTOR_RIGHT, right_target);
    	
    	if(blocking) {
    		while(target_reached(
    				left_target,
    				right_target) == false) {
    			Thread.sleep(1);
    		}
    		
    		//reset to original speed
    		//if non-blocking, the user is responsible for setting their own speed
    		set_speed(speed);
    	}
    	
    }
    
    /**
     * Checks if (wheels have rotated for a given number of degrees):
     * The left wheel has rotated for left_target_degrees degrees.
     * The right wheel has rotated for right_target_degrees degrees.
     * If both conditions are met, it returns true, otherwise it's false.
     * @param left_target_degrees target degrees for left whel
     * @param right_target_degrees target degrees for right wheel
     * @return a boolean indicating whether the wheels have reached your target or not
     * @throws IOException
     */
    public boolean target_reached(double left_target_degrees, double right_target_degrees) throws IOException {
    	int tolerance = 5;
    	double min_left_target = left_target_degrees - tolerance;
    	double max_left_target = left_target_degrees + tolerance;
    	double min_right_target = right_target_degrees - tolerance;
    	double max_right_target = right_target_degrees + tolerance;
    	
    	int current_left_position = get_motor_encoder(MOTOR_LEFT);
    	int current_right_position = get_motor_encoder(MOTOR_RIGHT);
    	
    	if((current_left_position > min_left_target) && (current_left_position < max_left_target) && (current_right_position > min_right_target) && (current_right_position < max_right_target)) {
    	return true;
    	}
    	return false;
    }
    
    /**
     * Turns *ON* one of the 2 red blinkers that GoPiGo3 has.
     * @param id 0/1 for the right/left led. String literals can also be used: "left" or "right"
     * @throws IOException if spi contacts fails.
     */
    public void blinker_on(int id) throws IOException {
    	if(id == 1) {
    		set_led(LED_LEFT_BLINKER, 255, 0, 0);
    	}
    	if(id == 0) {
    		set_led(LED_RIGHT_BLINKER, 255, 0, 0);
    	}
    }
    
    /**
     * Turns *ON* one of the 2 red blinkers that GoPiGo3 has.
     * @param "left" or "right" corresponding to either led. 0/1 can also be used. Other strings will have no effect.
     * @throws IOException if spi contacts fails.
     */
    public void blinker_on(String id) throws IOException {
    	if(id.equals("left")) {
    		set_led(LED_LEFT_BLINKER, 255, 0, 0);
    	}
    	if(id.equals("right")) {
    		set_led(LED_RIGHT_BLINKER, 255, 0, 0);
    	}
    }
    
    /**
     * Turns *OFF* one of the 2 red blinkers that GoPiGo3 has. 
     * @param id 0/1 for the right/left led. String literals can also be used: "left" or "right"
     * @throws IOException
     */
    public void blinker_off(int id) throws IOException {
    	if(id == 1) {
    		set_led(LED_LEFT_BLINKER, 0, 0, 0);
    	}
    	if(id == 0) {
    		set_led(LED_RIGHT_BLINKER, 0, 0, 0);
    	}
    }
    
    /**
     * Turns *OFF* one of the 2 red blinkers that GoPiGo3 has. 
     * @param id "left" or "right" corresponding to either led. 0/1 can also be used. Other strings will have no effect.
     * @throws IOException if spi contact fails
     */
    public void blinker_off(String id) throws IOException {
    	if(id.equals("left")) {
    		set_led(LED_LEFT_BLINKER, 0, 0, 0);
    	}
    	if(id.equals("right")) {
    		set_led(LED_RIGHT_BLINKER, 0, 0, 0);
    	}
    }
    
   /**
    * Turns *ON* Dexter mascot's left eye.
    * @throws IOException if spi contact fails
    */
   public void open_left_eye() throws IOException {
	   set_led(LED_LEFT_EYE, left_eye_color[0], left_eye_color[1], left_eye_color[2]);
   }
   
   /**
    * Turns *ON* Dexter mascot's right eye.
    * @throws IOException if spi contact fails
    */
   public void open_right_eye() throws IOException {
	   set_led(LED_RIGHT_EYE, right_eye_color[0], right_eye_color[1], right_eye_color[2]);
   }
   
   /**
    * Turns *ON* both of the Dexter mascot's eyes.
    * @throws IOException if spi contact fails
    */
   public void open_eyes() throws IOException {
	   open_left_eye();
	   open_right_eye();
   }
   /**
    * Turns *OFF* Dexter mascot's left eye.
    * @throws IOException if spi contact fails
    */
   public void close_left_eye() throws IOException {
	   set_led(LED_LEFT_EYE, 0, 0, 0);
   }
   /**
    * Turns *OFF* Dexter mascot's right eye.
    * @throws IOException if spi contact fails
    */
   public void close_right_eye() throws IOException {
	   set_led(LED_RIGHT_EYE, 0, 0, 0);
   }
   /**
    * Turns *OFF* both of the Dexter mascot's eyes.
    * @throws IOException if spi contact fails
    */
   public void close_eyes() throws IOException {
	   close_left_eye();
	   close_right_eye();
   }
   
   /**
    * Sets the LED color for Dexter mascot's left eye. Uses RGB values.
    * All values can reach between 0 and 255. Any smaller or higher values will be capped.
    * 
    * @param red value corresponding to the red color. 
    * @param green value corresponding to the green color.
    * @param blue value corresponding to the blue color.
    */
   public void set_left_eye_color(int red, int green, int blue) {
	   left_eye_color[0] = red;
	   left_eye_color[1] = green;
	   left_eye_color[2] = blue;
   }
   
   /**
    * Sets the LED color for Dexter mascot's right eye.
    * All values can reach between 0 and 255. Any smaller or higher values will be capped.
    * 
    * @param red balue corresponding to the red color. 
    * @param green value corresponding to the green color.
    * @param blue value corresponding to the blue color.
    */
   public void set_right_eye_color(int red, int green, int blue) {
	   right_eye_color[0] = red;
	   right_eye_color[1] = green;
	   right_eye_color[2] = blue;
   }
   
   /**
    * Sets the LED color for both of the Dexter mascot's eyes.
    * All values can reach between 0 and 255. Any smaller or higher values will be capped.
    * 
    * @param red value corresponding to the red color. 
    * @param green value corresponding to the green color.
    * @param blue value corresponding to the blue color.
    */
   public void set_eye_color(int red, int green, int blue) {
	   set_left_eye_color(red, green, blue);
	   set_right_eye_color(red, green, blue);
   }
   
   /**
    * Initializes a led object and returns it.
    * @param port Can be either "AD1" or "AD2".
    * @return an instance of a led object.
    */
   public Led init_led(String port) throws IOException, InterruptedException {
	   return new Led(port, this, use_mutex);
   }
   
   /**
    * Initializes a buzzer object and returns it.
    * @param port Can be either "AD1" or "AD2".
    * @return an instance of a led object.
    */
   public Buzzer init_buzzer(String port) throws IOException, InterruptedException {
	   return new Buzzer(port, this, use_mutex);
   }
   
   /**
    * Initializes a Servo object and returns it.
    * @param port Can be either "SERVO1" or "SERVO2".
    * @return an instance of a led object.
    */
   public Servo init_servo(String port) throws IOException, InterruptedException {
	   return new Servo(port, this, use_mutex);
   }
   
   /**
    * Initializes a ButtonSensor object and returns it.
    * @param port Can be either "AD1" or "AD2".
    * @return an instance of a led object.
    */
   public ButtonSensor init_button_sensor(String port) throws IOException, InterruptedException {
	   return new ButtonSensor(port, this, use_mutex);
   }
   
   /**
    * Initializes a LoudnessSensor object and returns it.
    * @param port Can be either "AD1" or "AD2".
    * @return an instance of a led object.
    */
   public LoudnessSensor init_loudness_sensor(String port) throws IOException, InterruptedException {
	   return new LoudnessSensor(port, this, use_mutex);	
   }
}