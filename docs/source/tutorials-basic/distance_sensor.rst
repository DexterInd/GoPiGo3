.. _tutorials-basic-distance-sensor:

**********************************
Measuring with the Distance Sensor
**********************************

==========
Our target
==========

In this tutorial, we are using a `Distance Sensor`_ for measuring the distance to a target with the `GoPiGo3`_ robot.
We are going to print the values on a terminal.

===================
The code we analyse
===================

The code we're analyzing in this tutorial is the following one.

.. code-block:: python

    from __future__ import print_function
    from __future__ import division
    from builtins import input
    # the above lines are meant for Python3 compatibility.
    # they force the use of Python3 functionality for print(),
    # the integer division and input()
    # mind your parentheses!

    # import the GoPiGo3 drivers
    import time
    import easygopigo3 as easy

    # Create an instance of the Distance Sensor class.
    my_distance_sensor = easy.DistanceSensor()     # Distance_Sensor will be the Line Follower object.

    # Read the Distance Sensor
    def get_sensorval():
        val = my_distance_sensor.read_mm()           # Read the distance sensor in mm.
        # You can also read the sensor in cm or inches.  Uncomment the lines below to read in different units.
        # val=Distance_Sensor.read()            # Read the distance sensor in cm.
        # val=Distance_Sensor.read_inches()     # Read the distance sensor in inches.
        return val

    while True:
        # Directly print the values of the sensor.
        print ("Distance Sensor Reading (mm): " + str(get_sensorval()))

The source code for this example program can be found `here on github <https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/Examples/easy_Distance_Sensor.py>`_.


===========
The modules
===========

Start by importing 2 important modules:

.. code-block:: python

   import time
   import easygopigo3 as easy

The :py:mod:`easygopigo3` module is used for interacting with the `GoPiGo3`_ robot, whilst
the ``time`` module is generally used for delaying actions, commands, setting timers etc.

We also import 3 other functions which are meant for python3 compatibility. We shouldn't care about them.

.. code-block:: python

    from __future__ import print_function
    from __future__ import division
    from builtins import input

===========
The objects
===========

For interfacing with the `Distance Sensor`_ we need to instantiate an object of the :py:class:`easygopigo3.DistanceSensor` class.
We do it like in the following code snippet.

.. code-block:: python

   my_distance_sensor = easy.DistanceSensor()

=========
Main part
=========

There's a single while loop in the entire script. That loop is meant for printing the values that we're
reading repeatedly, but in order to do that, we need to define a function called ``get_sensorval()``.
``get_sensorval()`` function returns the distance in millimeters from our target.

.. code-block:: python

    # Read the Distance Sensor
    def get_sensorval():
        val = my_distance_sensor.read_mm()           # Read the distance sensor in mm.
        # You can also read the sensor in cm or inches.  Uncomment the lines below to read in different units.
        # val=Distance_Sensor.read()            # Read the distance sensor in cm.
        # val=Distance_Sensor.read_inches()     # Read the distance sensor in inches.
        return val

    while True:
        # Directly print the values of the sensor.
        print ("Distance Sensor Reading (mm): " + str(get_sensorval()))

.. seealso::

     Check out :py:class:`easygopigo3.DistanceSensor`'s API for more details.

==========
Running it
==========

Connect the `Distance Sensor`_ to any of the 2 ``"I2C"`` ports on the `GoPiGo3`_ robot.
After the sensor is connected, on your Raspberry Pi, open up a terminal and type in the following 2 commands.

.. code-block:: console

    cd ~/Desktop/GoPiGo3/Software/Python/Examples
    python easy_Distance_Sensor.py

.. image:: http://i.imgur.com/2yNHhsm.gif

.. note::

   For knowing where the ports are located on the robot (like port ``"I2C"``), see the following :ref:`graphical representation <hardware-ports-section>`.

.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
