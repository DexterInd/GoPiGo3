/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  This is an example for using I2C with the GoPiGo3.
 *
 *  Hardware: Connect a PCA9570 I2C output expander to GPG3 AD1 port.
 *
 *  Results:  When you run this program, P0 output should toggle.
 *
 *  Example compile command:
 *    g++ -o i2c i2c.cpp ../GoPiGo3.cpp -I..
 *  Example run command:
 *    sudo ./i2c
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

  GPG.set_grove_type(GROVE_1, GROVE_TYPE_I2C);
  i2c_struct_t I2C1;
  I2C1.address = 0x24;
  I2C1.length_read = 3;
  I2C1.length_write = 1;
  uint8_t s = 0;
  while(true){
    I2C1.buffer_write[0] = s;
    int error = GPG.grove_i2c_transfer(GROVE_1, &I2C1);
    printf("Error: %d  bytes: %d %d %d\n", error, I2C1.buffer_read[0], I2C1.buffer_read[1], I2C1.buffer_read[2]);
    if(s == 0){
      s = 1;
    }else{
      s = 0;
    }
    usleep(50000);
  }
}

// Signal handler that will be called when Ctrl+C is pressed to stop the program
void exit_signal_handler(int signo){
  if(signo == SIGINT){
    GPG.reset_all();    // Reset everything so there are no run-away motors
    exit(-2);
  }
}
