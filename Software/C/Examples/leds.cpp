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
 *    g++ -o program "leds.cpp"
 *  Example run command:
 *    sudo ./program
 *
 */

#include "GoPiGo3.cpp" // for GoPiGo3
#include <stdio.h>     // for printf
#include <unistd.h>    // for usleep
#include <signal.h>    // for catching exit signals

GoPiGo3 GPG;

#define BRIGHTNESS_LIMIT 25

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

  GPG.detect(); // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.

  uint8_t i1 = 0;
  uint8_t i2 = BRIGHTNESS_LIMIT / 3;
  uint8_t i3 = (BRIGHTNESS_LIMIT * 2) / 3;
  int8_t a1 = 1;
  int8_t a2 = 1;
  int8_t a3 = 1;
  while(true){
    GPG.set_led(LED_EYE_LEFT, i1, i2, i3);
    GPG.set_led(LED_EYE_RIGHT, i2, i3, i1);
    GPG.set_led(LED_BLINKER_LEFT, i1);
    GPG.set_led(LED_BLINKER_RIGHT, i2);

    i1 += a1;
    if(i1 == BRIGHTNESS_LIMIT || i1 == 0){
      a1 *= -1;
    }
    i2 += a2;
    if(i2 == BRIGHTNESS_LIMIT || i2 == 0){
      a2 *= -1;
    }
    i3 += a3;
    if(i3 == BRIGHTNESS_LIMIT || i3 == 0){
      a3 *= -1;
    }

    // slow down
    usleep(25000);
  }
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    GPG.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
