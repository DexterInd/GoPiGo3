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
 *  Hardware: Connect a grove ultrasonic sensor to GPG3 AD1 port, and IR receiver to GPG3 AD2 port.
 *
 *  Results:  When you run this program, you should see the values for each sensor.
 *
 *  Example compile command:
 *    g++ -o sensors sensors.cpp ../GoPiGo3.cpp -I..
 *  Example run command:
 *    sudo ./sensors
 *
 */

#include <GoPiGo3.h>    // for GoPiGo3
#include <stdio.h>      // for printf
#include <unistd.h>     // for usleep
#include <signal.h>     // for catching exit signals

GoPiGo3 GPG;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

  GPG.detect(); // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.

  GPG.set_grove_type(GROVE_1, GROVE_TYPE_US);
  GPG.set_grove_type(GROVE_2, GROVE_TYPE_IR_DI_REMOTE);
  sensor_ultrasonic_t US;
  sensor_infrared_gobox_t IR;

  while(true){
    int USerror = GPG.get_grove_value(GROVE_1, &US);
    int IRerror = GPG.get_grove_value(GROVE_2, &IR);
    printf("US: Error %d  %4dmm    IR: Error %d  button %d\n", USerror, US.mm, IRerror, IR.button);
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
