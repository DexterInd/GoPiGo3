/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  This code is an example for using GoPiGo3 motors.
 *
 *  Results:  When you run this program, you should see the encoder value for each motor. Manually rotate the left motor, and the right motor will follow.
 *
 *  Example compile command:
 *    g++ -o program "motors.c"
 *  Example run command:
 *    sudo ./program
 *
 */

#include "GoPiGo3.cpp" // for GoPiGo3
#include <stdio.h>     // for printf
#include <unistd.h>    // for usleep
#include <signal.h>    // for catching exit signals

GoPiGo3 GPG;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C
  
  GPG.detect(); // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.
  
  // Reset the encoders
  GPG.offset_motor_encoder(MOTOR_LEFT, GPG.get_motor_encoder(MOTOR_LEFT));
  GPG.offset_motor_encoder(MOTOR_RIGHT, GPG.get_motor_encoder(MOTOR_RIGHT));
  
  while(true){
    // Read the encoders
    int32_t EncoderLeft = GPG.get_motor_encoder(MOTOR_LEFT);
    int32_t EncoderRight = GPG.get_motor_encoder(MOTOR_RIGHT);
    
    // Use the encoder value from the left motor to control the position of the right motor
    GPG.set_motor_position(MOTOR_RIGHT, EncoderLeft);
    
    // Display the encoder values
    printf("Encoder Left: %6d  Right: %6d\n", EncoderLeft, EncoderRight);
    
    // Delay for 20ms
    usleep(20000);
  }
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    GPG.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
