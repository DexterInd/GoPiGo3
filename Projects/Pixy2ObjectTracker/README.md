# GoPiGo3 + Pixy2 Object Tracker

A robot that follows a designated object.

## Quick Overview

![Imgur](https://i.imgur.com/aABAITV.jpg)

This is a project which uses the Pixy2 module in tandem with the GoPiGo3. The robot's purpose is to follow a designated object, which is color coded. In our case, we decided to go with a red object, because it is differentiated more easily. 

The advantage of using a Pixy2 module along a GoPiGo3 is that a big chunk of the computer-vision processing is offloaded to the Pixy2, thus allowing the Raspberry Pi to "breathe" more easily. This leads to a shorter algorithm on the Pi's side.

![Imgur](https://i.imgur.com/iTDQOLM.jpg)

In our case, we decided to make the Pixy2 communicate with the Raspberry Pi over the I2C and power up the module through the USB. Be aware that this little module is quite hungry, so it's better to have another power source going to the Pi, apart from the regular Dexter Industries battery pack. It also gets really warm to touch.

![Imgur](https://i.imgur.com/AMuOqZV.jpg)

We used a Grove cable to connect to the Pixy2. Basically, we've chopped the other end of the cable and use 3 header pins to connect that to the Pixy2: an `SDA`, `SCL` and `GND`. The intact Grove connector gets plugged into the I2C port. You can find out more about the Pixy2's GPIO pins [here](https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:porting_guide).

Here are a two GIFs with this robot:

<img src="https://i.imgur.com/WUjJPBo.gif?raw=true" width="480px">

In the above figure, we can see what the Pixy2 camera actually detects: it's a can of spray and it's red. Setting up the recognition of this object can be done via the PixyMon monitor.

<img src="https://i.imgur.com/Pluk9in.gif?raw=true" width="480px">

And in the above GIF, we can see how the GoPiGo3 follows the said object. Pretty neat!

## Installing

To install `scipy` run
```bash
sudo apt-get update
sudo apt-get install python3-scipy
```
And to install the recordclass for mutable named tuples and the Pixy2 device library run
```bash
sudo pip3 install recordclass
sudo pip3 install git+https://github.com/RobertLucian/pixy2.git@v0.1.0
```

## Setting It Up

To set this up, connect the Pixy2 to your laptop and run the PixyMon monitor. You can do that on your Raspberry Pi as well, but it's a bit more complicated. The installation instructions for both approaches can be found [here](https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:pixy_regular_quick_start).

Next, set your tracked object and use signature `1` as that's the one that's tracked in this project's script. Make sure the color of your object is separable from that of others, because the Pixy2 actually looks for colors instead of shapes. 

The Pixy2 can be relatively easily mounted with zip ties on the GoPiGo3's chassis and in this particular situation, the angle of tilt is not important.

## Running It

To run, you only have to launch the main script and it's ready to follow your wonder object.
```bash
python pixy2_object_tracker.py
```
To stop the program, press the `<ESC>` key.