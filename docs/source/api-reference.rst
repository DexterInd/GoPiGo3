###################
API Reference Point
###################

.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/

**************************
The ``easygopigo3`` module
**************************

.. py:module:: easygopigo3

.. py:class:: EasyGoPiGo3(object)

   | This class is used for controlling a `GoPiGo3`_ robot.
   | With this class you can do the following things with your `GoPiGo3`_:

     * drive your robot in any number of directions
     * have precise control over the direction of the robot
     * set the speed of the robot
     * turn *on* or *off* the blinker LEDs
     * control the distance sensor's *eyes*, *color* and so on ...

   .. py:method:: __init__(self)

      This constructor sets the variables to the following values:

      :var int speed = 300: the speed of the motors can go between **0-1000**
      :var (int,int,int) left_eye_color = (0,255,255): set the `distance sensor`_'s color to **turqoise**
      :var (int,int,int) right_eye_color = (0,255,255): set the `distance sensor`_'s color to **turqoise**

   .. py:method:: volt(self)

      This method returns the battery voltage of the `GoPiGo3`_.

      :return: the battery voltage of the `GoPiGo3`_
      :rtype: double

   .. py:method:: set_speed(self, in_speed)

      This method sets the speed of the `GoPiGo3`_ specified by ``in_speed`` argument.

      :param int in_speed: the speed at which the robot is set to run - speed between **0-1000**

   .. py:method:: get_speed(self)

      Use this method for getting the speed of your `GoPiGo3`_.

      :return: the speed of the robot measured between **0-1000**
      :rtype: int

   .. py:method:: stop(self)

      | This method stops the `GoPiGo3`_ from moving.
      | It brings the `GoPiGo3`_ to a full stop.
