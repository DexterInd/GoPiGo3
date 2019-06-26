# Lane Follower w/ the Pixy2

![Imgur](https://i.imgur.com/vUQM7Sr.jpg)

*Figure 1 - GoPiGo3 + Pixy2 fully set up*

In this project, a GoPiGo3 is used in tandem with a Pixy2 to create a robot that's capable of following a lane - that is a robot that stays between two lines and at the same time advances forward. This is a different task from just following a line because with lanes, it's also about knowing one's position with regards to 2 lines: it involves a certain amount of awareness of the environment and it also implies the presence of assumption for the robot.

Needless to say, it's a much more fun challange than with a line follower.

## Hardware

This is what's needed for this project: 

* A  *GoPiGo3*.
* A *Pixy2* camera. 
* Zip ties.
* A custom made cable used for interfacing with the Pixy2 over I2C.

The zip ties are needed to anchor the Pixy2 to the GoPiGo3's chassis. The tilt of the Pixy2 can be seen in *figure 3*. That positive tilt is absolutely necessary and has to be experimented with by looking at what the camera sees - more on that in the following chapters. Since the camera has a narrower vertical field of view than the horizontal one, one has to tilt the Pixy2 forward so that more of the track can be seen. It also has the advantage of cutting out any noise that could have been caught if the Pixy2's sight were to be parallel with the ground.

The custom made cable is a Grove cable which has one end replaced with header pins. Those header pins are used to connect to the Pixy2's board. The I2C communication is done through that. To see what the Pixy2's interface looks like, check out [this](https://docs.pixycam.com/wiki/doku.php?id=wiki:v2:porting_guide).

Last but not least, it is recommended to use an additional power source for the Pixy2 because this device is quite power hungry that can otherwise lead to a system crash of the Raspberry Pi. 

## Dependencies

For setting up the Pixy2, there are 2 options: either set up the Pixy2 for the laptop or for your Raspberry Pi. This set up is only required for configuring the Pixy2 and not for the actual usage of the robot. Regardless, the instructions on setting this up can be found on Pixy2's documentation right [here](https://pixycam.com/downloads-pixy2/).


## On Calibration

### Pixy2 Camera Calibration

The Pixy2 comes preloaded with a configuration that may or may not be good for your setting or for this project. Through experimentation I have found out that the following values work best with the lane follower.

![Imgur](https://i.imgur.com/7fLehDw.jpg)
*Figure 2 - The configuration values in PixyMon*

In a nutshell, the trick is in lowering the line detection algorithm's sensitivity as much as possible while still preserving the ability to detect lanes. As it can be seen in *figure 3*, the lanes are white, so that gives us the most contrast when put side by side with other things from the environment.

### Lane Follower Calibration

![Imgur](https://i.imgur.com/nhhU2Eo.jpg)
*Figure 3 - The Pixy2's Tilt*

The lane follower script loads on start up a config file from the same directory as the script itself: `config.json`. This config file contains the configurations needed for the robot to work well. Setting up the right values can mean the difference between a bad robot driver and an excellent one. The user *has to* tinker with these values because the Pixy2 doesn't have a fix mount support for it and thus every situation will be different. Even sub-millimetric differences in how the Pixy2 is positioned can mean a lot for the robot's computed trajectory. Blame the zip ties! 

The `config.json` file has the following fields:

1. `alfa` - the factor of the exponential moving average. Represents how much (in percents) of the current read value is given credibility - be it the angle or the determined magnitude. It's between **0** and **1**. The higher it is, the faster it will react to new situations, but it also makes the robot more prone to giving credibility to noise. The lower, the more smooth the computed values are over time.

1. `yotta` - how much importance is given to the length of the determined trajectory: aka the magnitude. It's between **0** and **1**.

1. `pid1` - the first PID controller of the robot.

1. `pid2` - the 2nd PID controller of the robot.

1. `pid-switch-point` - the magnitude threshold at which point the `pid2` controller takes over.

1. `max-motor-speed` - the maximum speed of the motors.

When running the robot's script, 2 windows will show up on your screen:

1. A window showing you exactly what the robot sees as a collection of white vectors. Generally, the robot only has to see the 2 lines of the lane.

1. Another window showing a warped image of what the robot sees as if a bird is watching over the robot from up top. When the Pixy2 is **properly tilted**, the lane will appear as 2 straight parallel lines. Use this as feedback to calibrate the tilt of the Pixy2. This can be observed in *figure 4*.

![Imgur](https://i.imgur.com/brGRa95.gif)

*Figure 4 - Seeing what the robot sees*

## Track Properties

The track also needs to have a couple of properties:

1. The distance between the inner edges of the lane has to be *15 cm*.
1. The width of the lane's lines has to be around *2 (or more) cm*.
1. The most sharp curve can have a radius of *32 cm*.
1. There can only be 2 type of curves on the track because there are 2 PID controllers: say one type has a radius of 32 cm and the other has 78 cm. Theoretically, even with 2 PIDs there could be a wider range of permitted curves, but they should mostly have a small deviation. Like curves from 25-35 cm and then another range starting with 70 and going up to 100. It is possible, although the tuning process would be harder. The simplest option is in just having 2 types and that's it. 

The track I've built can be observed in *figure 5*.

![Imgur](https://i.imgur.com/Uco9PAz.jpg)
*Figure 5 - Picture of the track - 1 is for the distance between the inner edges of the lane and 2 is for the 32 cm radius of the sharp curve*.

## Usage

There are a couple of dependencies for this project: `numpy==1.12.1`, `opencv-python==3.4.4.19`, `getkey==0.6.5`, `recordclass==0.11.1` and `pixy2==0.1.0`.

To install the `pixy2` package run the following command:
```bash
pip3 install git+https://github.com/RobertLucian/pixy2.git@v0.1.0
```

All the rest of the packages mentioned above can be either installed with pip or with apt-get. 

After the dependencies get installed, the project's script can be run like this:
```bash
python3 pixy2_lane_follower.py
```

Here's a video of how the robot follows the lane. Pretty cool, ain't that right?

[![Youtube Video](https://img.youtube.com/vi/JyMkOBQr7ho/0.jpg)](https://www.youtube.com/watch?v=JyMkOBQr7ho)