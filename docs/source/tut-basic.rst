.. _tutorials-basic-chapter:

#################
Tutorials - Basic
#################

************
Requirements
************

Please make sure you have followed all the instructions found in :ref:`Getting Started <getting-started-chapter>`.
In all these tutorials, you will need:

  1. A `GoPiGo3`_ robot.
  2. Sensor/Actuator specific for the tutorial : i.e.: a `Grove Buzzer`_, a `Line Follower`_, etc.


****************
Pushing a Button
****************

In this tutorial, we are going to make a `Grove Button`_ control `GoPiGo3`_ Dex's eyes.

   * When the `Grove Button`_ is pressed, Dex's eyes turn on.
   * When the `Grove Button`_ is released, Dex's eyes turn off.

We need to start by importing 2 important modules:

.. code-block:: python

   import time
   import easygopigo3 as easy

The :py:mod:`easygopigo3` module is used for interacting with the `GoPiGo3`_ robot, whilst
the ``time`` module is generally used for delaying actions, commands, etc.

After this, we need to instantiate an :py:class:`easygopigo3.EasyGoPiGo3` object.
With this :py:class:`~easygopigo3.EasyGoPiGo3` object, we are doing 2 things:

   * Use it for turning *ON* and *OFF* the `GoPiGo3`_ Dex's eyes.
   * Use it for instantiating a :py:class:`~easygopigo3.ButtonSensor` object for reading the `Grove Button`_'s state.

.. code-block:: python

   gpg = easy.EasyGoPiGo3()




.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _shop: https://www.dexterindustries.com/shop/
.. _infrared receiver: https://www.seeedstudio.com/Grove-Infrared-Receiver-p-994.html
.. _technical specs: https://www.dexterindustries.com/GoPiGo/learning/hardware-port-description/
.. _grove light sensor: https://www.dexterindustries.com/shop/grove-light-sensor/
.. _grove sound sensor: https://www.dexterindustries.com/shop/grove-sound-sensor/
.. _grove ultrasonic sensor: https://www.dexterindustries.com/shop/ultrasonic-sensor/
.. _grove buzzer: https://www.dexterindustries.com/shop/grove-buzzer/
.. _grove led: https://www.dexterindustries.com/shop/grove-red-led/
.. _grove button: https://www.dexterindustries.com/shop/grove-button/
.. _servo: https://www.dexterindustries.com/shop/servo-package/
.. _line follower: https://www.dexterindustries.com/shop/line-follower-for-gopigo/
.. _gopigo3 package: https://pypi.python.org/pypi/gopigo3
.. _repository: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/3-program-your-raspberry-pi-robot/python-programming-language/
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
.. _forum: http://forum.dexterindustries.com/categories
