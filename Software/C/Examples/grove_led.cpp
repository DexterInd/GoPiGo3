/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  This is an example for using an ultrasonic sensor and IR receiver with the GoPiGo3.
 *
 *  Hardware: Connect a grove LED to GPG3 AD1 port.
 *
 *  Results:  When you run this program, you should see the grove LED brightness pulsing up and down.
 *
 *  Example compile command:
 *    g++ -o program "grove_led.cpp"
 *  Example run command:
 *    sudo ./program
 *
 */

#include "GoPiGo3.cpp" // for GoPiGo3
#include <stdio.h>      // for printf
#include <unistd.h>     // for usleep
#include <signal.h>     // for catching exit signals

GoPiGo3 GPG;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

  GPG.detect(); // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.

  GPG.set_grove_type(GROVE_1, GROVE_TYPE_CUSTOM);
  GPG.set_grove_mode(GROVE_1_1, OUTPUT_PWM);

  int8_t i = 0;
  int8_t a = 1;
  while(true){
    GPG.set_grove_pwm_duty(GROVE_1_1, i);
    i += a;
    if(i == 100 || i == 0){
      a *= -1;
    }
    usleep(5000);
  }
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    GPG.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
