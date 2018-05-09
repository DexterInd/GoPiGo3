.. _getting-started-chapter:

###############
Getting Started
###############

****************
Buying a GoPiGo3
****************

To buy a `GoPiGo3`_ robot, please head over to our online `shop`_ and search for the `GoPiGo3`_ robot. From our `shop`_, you can get sensors for your robot such as the `Distance Sensor`_, the `Grove Light Sensor`_, etc.

.. image:: images/gopigo3.jpg

***********************
Assembling GoPiGo3
***********************

For assembling your `GoPiGo3`_ robot, read the instructions from the following page: `assembling instructions`_.

************************
Connecting to GoPiGo3
************************

To connect to your `GoPiGo3`_ robot with a computer or laptop, read the instructions on the following page: `connecting to robot`_.

***********************
Program your GoPiGo3
***********************

To program your `GoPiGo3`_ to do what you want, you can follow the instructions found here (`programming your robot`_) or *follow the rest of instructions found in this section*.

To install or update the `GoPiGo3`_ library on your RaspberryPi, open a terminal or the command line and type the following command:

.. code-block:: bash

   # follow any given instructions given through this command

   curl -kL dexterindustries.com/update_gopigo3 | bash

Also, in order to be able to use the :py:meth:`easygopigo3.EasyGoPiGo3.init_distance_sensor` method and the :py:class:`easygopigo3.DistanceSensor` class, the `DI-Sensors`_ package is required.
You can install it or update it with the following command in the terminal:

.. code-block:: bash

   # follow any given instructions given through this command

   curl -kL dexterindustries.com/update_sensors | bash

********************
Connect More Sensors
********************

The `GoPiGo3`_ can also be paired with our in-house sensors.
There are a number of digital and analog sensors that can be connected to the GoPiGo3. We have further in-depth documentation on the following 4 sensors:

   * The DI `IMU Sensor`_.
   * The DI `Light and Color Sensor`_.
   * The DI `Temperature Humidity Pressure Sensor`_.
   * The DI `Distance Sensor`_.

For more on getting started with these sensors, please check the `DI-Sensors`_ documentation.

.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _assembling instructions: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/1-assemble-gopigo3/
.. _connecting to robot: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/2-connect-to-the-gopigo-3/
.. _programming your robot: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/3-program-your-raspberry-pi-robot/
.. _shop: https://www.dexterindustries.com/shop/
.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _technical specs: https://www.dexterindustries.com/GoPiGo/learning/hardware-port-description/
.. _grove light sensor: https://www.dexterindustries.com/shop/grove-light-sensor/
.. _grove sound sensor: https://www.dexterindustries.com/shop/grove-sound-sensor/
.. _grove loudness sensor: http://wiki.seeed.cc/Grove-Loudness_Sensor/
.. _grove ultrasonic sensor: https://www.dexterindustries.com/shop/ultrasonic-sensor/
.. _grove buzzer: https://www.dexterindustries.com/shop/grove-buzzer/
.. _grove led: https://www.dexterindustries.com/shop/grove-red-led/
.. _grove button: https://www.dexterindustries.com/shop/grove-button/
.. _grove motion sensor: https://www.dexterindustries.com/shop/grove-pir-motion-sensor/
.. _grove dht sensor: https://www.dexterindustries.com/shop/temp-humidity/
.. _servo: https://www.dexterindustries.com/shop/servo-package/
.. _line follower: https://www.dexterindustries.com/shop/line-follower-for-gopigo/
.. _infrared receiver: https://www.dexterindustries.com/shop/grove-infrared-sensor/
.. _infrared remote: https://www.dexterindustries.com/shop/infrared-remote/
.. _gopigo3 package: https://pypi.python.org/pypi/gopigo3
.. _repository: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/3-program-your-raspberry-pi-robot/python-programming-language/
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
.. _forum: http://forum.dexterindustries.com/categories
.. _DI-Sensors: http://di-sensors.readthedocs.io
.. _imu sensor: https://www.dexterindustries.com/shop/imu-sensor/
.. _light and color sensor: https://www.dexterindustries.com/shop/light-color-sensor/
.. _temperature humidity pressure sensor: https://www.dexterindustries.com/shop/temperature-humidity-pressure-sensor/
