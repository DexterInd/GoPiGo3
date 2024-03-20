/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  This code is an example for using GoPiGo3 servos.
 *
 *  Results:  When you run this program, you should see the servos center.
 *
 *  To compile see: https://github.com/slowrunner/Carl/blob/master/Examples/cpp/Alan_Note.txt
 */

#include <GoPiGo3.h>   // for GoPiGo3
#include <stdio.h>     // for printf
#include <unistd.h>    // for usleep
#include <signal.h>    // for catching exit signals

GoPiGo3 GPG;

void exit_signal_handler(int signo);

int main(){
  signal(SIGINT, exit_signal_handler); // register the exit function for Ctrl+C

  GPG.detect(); // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.

  printf("\nReseting servos to center\n");

  // Reset the servos to center
  GPG.set_servo(SERVO_1,1500);
  // let one servo move at a time to keep load smaller
  usleep(200000);
  GPG.set_servo(SERVO_2,1500);
  usleep(200000);
  // Turn servo power off
  GPG.set_servo(SERVO_1,0);
  GPG.set_servo(SERVO_2,0);

  // while(true){
  //   usleep(2000);
  // }
  GPG.reset_all();
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    GPG.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
