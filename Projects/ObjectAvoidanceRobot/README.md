# Obstacle Avoidance Robot

In this project, we use a DistanceSensor for detecting obstacles with a GoPiGo3. The robot's speed is proportional we read.
When the target is too close to the robot, the GoPiGo3 robot stops. The robot will start moving again once the obstacle is removed from the robot's path.

This project can run with Python 2 and 3.

There are a couple of constants that can be set within the script:

* `DEBUG` : By default it's set to `False`, but if you wish to see more then set it to `True`.
* `MAX_DISTANCE` : The maximum distance the sensor can detect in millimeters.
* `MIN_DISTANCE` : The minimum distance the sensor can detect in millimeters.
* `NO_OBSTACLE` : Don't modify this constant. When the sensor can't detect any surface, it returns a value equal to this constant.
* `ERROR` : Don't modify this constant. When the sensor can't be detected, it returns a value equal to this constant.
* `MAX_SPEED` : Through tests it has been proven that this constant's value is the optimum speed for the GoPiGo3.
* `MIN_SPEED` : The minimum speed for the GoPiGo3. Can be set way lower.
