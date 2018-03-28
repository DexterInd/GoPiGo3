#!/usr/bin/env python
#
# https://www.dexterindustries.com/GoPiGo/
# https://github.com/DexterInd/GoPiGo3
#
# Copyright (c) 2017 Dexter Industries
# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GoPiGo3/blob/master/LICENSE.md
#
# This code is an example for reading GoPiGo3 information
#
# Results: Print information about the attached GoPiGo3.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import gopigo3 # import the GoPiGo3 drivers

try:
    GPG = gopigo3.GoPiGo3() # Create an instance of the GoPiGo3 class. GPG will be the GoPiGo3 object.
    
    # Each of the following GPG.get functions return a list of 2 values
    print("Manufacturer    : ", GPG.get_manufacturer()    ) # read and display the serial number
    print("Board           : ", GPG.get_board()           ) # read and display the serial number
    print("Serial Number   : ", GPG.get_id()              ) # read and display the serial number
    print("Hardware version: ", GPG.get_version_hardware()) # read and display the hardware version
    print("Firmware version: ", GPG.get_version_firmware()) # read and display the firmware version
    print("Battery voltage : ", GPG.get_voltage_battery() ) # read and display the current battery voltage
    print("5v voltage      : ", GPG.get_voltage_5v()      ) # read and display the current 5v regulator voltage
    
except IOError as error:
    print(error)

except gopigo3.FirmwareVersionError as error:
    print(error)
