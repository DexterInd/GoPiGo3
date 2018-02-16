/*
 *  https://www.dexterindustries.com/GoPiGo3/
 *  https://github.com/DexterInd/GoPiGo3
 *
 *  Copyright (c) 2017 Dexter Industries
 *  Released under the MIT license (http://choosealicense.com/licenses/mit/).
 *  For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
 *
 *  This code is an example for reading GoPiGo3 information
 *
 *  Results: Print information about the attached GoPiGo3.
 *
 *  Example compile command:
 *    g++ -o info info.cpp ../GoPiGo3.cpp -I..
 *  Example run command:
 *    sudo ./info
 *
 */

#include <GoPiGo3.h>   // for GoPiGo3
#include <stdio.h>     // for printf

GoPiGo3 GPG; // Create a GoPiGo3 instance

int main(){
  char str[33]; // Room for the 32-character serial number string plus the NULL terminator.

  // Make sure that the GoPiGo3 is communicating and that the firmware is compatible with the drivers.
  // pass 'false' to detect() to make the error non-critical (return the error instead of exiting the program).
  if(GPG.detect(false) == ERROR_NONE){
    printf("\nGoPiGo3 info:\n");

    GPG.get_manufacturer(str);
    printf("  Manufacturer    : %s\n", str);

    GPG.get_board(str);
    printf("  Board           : %s\n", str);

    GPG.get_id(str);
    printf("  Serial Number   : %s\n", str);

    GPG.get_version_hardware(str);
    printf("  Hardware version: %s\n", str);

    GPG.get_version_firmware(str);
    printf("  Firmware version: %s\n", str);

    printf("  Battery voltage : %.3f\n", GPG.get_voltage_battery());
    printf("  5v voltage      : %.3f\n", GPG.get_voltage_5v());
  }else{
    printf("\nError communicating with GoPiGo3\n");
  }
}
