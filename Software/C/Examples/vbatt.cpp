/*
 *  This code is an example for reading GoPiGo3 battery voltage
 *
 *  Results: Prints float battery voltage
 *
 */

#include <GoPiGo3.h>   // for GoPiGo3
#include <stdio.h>     // for printf

GoPiGo3 GPG; // Create a GoPiGo3 instance

int main(){

  // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.
  // pass 'false' to detect() to make the error non-critical (return the error instead of exiting the program).
  if(GPG.detect(false) == ERROR_NONE){
    printf("  Battery voltage : %.3f\n", GPG.get_voltage_battery());
    printf("  5v voltage      : %.3f\n", GPG.get_voltage_5v());
  }else{
    printf("\nError communicating with GoPiGo3\n");
  }
}
