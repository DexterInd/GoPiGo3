# Obstacle Avoidance Robot

In this project, we use a [DistanceSensor](https://www.dexterindustries.com/shop/distance-sensor/) for detecting obstacles with a [GoPiGo3](https://www.dexterindustries.com/shop/gopigo3-robot-base-kit/).

The robot's speed is proportional to the distance from the target.
When the target is too close to the robot, the GoPiGo3 robot stops. The robot will start moving again once the obstacle is removed from the robot's trajectory.

This project can run with Python 2 and 3.

## On DexterOS
In DexterOS it's not needed to install or configure anything. Any required dependency is already installed on it. Just make sure you've got the right physical configuration (sensors, servos, etc) and then run the script this way `python program-name.py`.

## Attention

When the GoPiGo3 is low on battery, the script may inadvertently stop. Check the batteries before heading over to the forums.

![GoPiGo3 Cover](http://i.imgur.com/RBNHUzz.jpg)

## About the script

The DI-Sensor has to be connected to an I2C port with a Grove cable. Apart from that, there are a couple of constants that can be set within the script:

* `DEBUG` : By default it's set to `False`, but if you wish to see more then set it to `True`.
* `MAX_DISTANCE` : The maximum distance the sensor can detect in millimeters.
* `MIN_DISTANCE` : The minimum distance the sensor can detect in millimeters.
* `NO_OBSTACLE` : Don't modify this constant. When the sensor can't detect any surface, it returns a value equal to this constant.
* `ERROR` : Don't modify this constant. When the sensor can't be detected, it returns a value equal to this constant.
* `MAX_SPEED` : Through tests it has been proven that this constant's value is the optimum speed for the GoPiGo3.
* `MIN_SPEED` : The minimum speed for the GoPiGo3. Can be set way lower.

## Preview of the GoPiGo3


![GoPiGo3 with DistanceSensor](http://i.imgur.com/FlHrteg.gif)
