#!/usr/bin/env python
# Dexter Industries line sensor basic example
#
# This example shows a basic example to read sensor data from the line sensor.  Most basic example prints out the data from the 5 sensors on the line follower.
#
# Have a question about this example?  Ask on the forums here:  http://www.dexterindustries.com/forum/?forum=gopigo
#
# 
# Initial Date: 13 Dec 2015  Karan Nayan
# Last Updated: 16 Feb 2016  John Cole
# http://www.dexterindustries.com/
'''
## License
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
# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

import easygopigo3 as easy
import time

sensor_readings = None

gpg = easy.EasyGoPiGo3()

try:
    my_linefollower = gpg.init_line_follower()
    time.sleep(0.1)
except:
    print('Line Follower not responding')
    time.sleep(0.2)
    exit()
my_linefollower.read_position()
my_linefollower.read_position()


# start
gpg.forward()
while not  my_linefollower.read_position() == "black":
    if my_linefollower.read_position() == 'center':
        gpg.forward()
    if my_linefollower.read_position() == 'left':
        gpg.left()
    if my_linefollower.read_position() == 'right':
        gpg.right()
gpg.stop()

