#!/usr/bin/env python
# This program is for testing GoPiGo3 Hardware.  

'''
## License
 GoPiGo3 for the Raspberry Pi: an open source robotics platform for the Raspberry Pi.
 Copyright (C) 2017  Dexter Industries

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/gpl-3.0.txt>.
'''
from __future__ import print_function
from __future__ import division
from builtins import input
# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

import time
import easygopigo3 as easy

gpg = easy.EasyGoPiGo3()
gpg.reset_all()
gpg.set_speed(300)

import sys

import atexit
atexit.register(gpg.stop)

print ("Both motors moving Forward with Dex Eyes On")
gpg.open_eyes()
gpg.forward()
time.sleep(5)

print ("Both motors stopped with Dex Eyes Off")
gpg.close_eyes()
gpg.stop()
time.sleep(2)

print ("Both motors moving back with blinkers On")
gpg.blinker_on(1)
gpg.blinker_on(0)
gpg.backward()
time.sleep(5)

print ("Both motors stopped with blinkers Off")
gpg.blinker_off(1)
gpg.blinker_off(0)
gpg.stop()
time.sleep(2)

gpg.stop()
gpg.stop()

print ("Hardware test finished.")