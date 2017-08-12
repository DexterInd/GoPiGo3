.. _tutorials-basic-distance-sensor:

**********************************
Measuring with the Distance Sensor
**********************************

========
Our goal
========

In this tutorial, we are using a `Distance Sensor`_ for measuring the distance to a target with the `GoPiGo3`_ robot.
We are going to print the values on a terminal.

===================
The code we analyse
===================

The code we're analyzing in this tutorial is the following one.

.. code-block:: python

    # import the GoPiGo3 drivers
    import time
    import easygopigo3 as easy

    # Create an instance of the Distance Sensor class.
    my_distance_sensor = easy.DistanceSensor()     # Distance_Sensor will be the Line Follower object.

    while True:
        # Directly print the values of the sensor.
        print ("Distance Sensor Reading (mm): " + str(my_distance_sensor.read_mm()))

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

There's a single while loop in the entire script. The loop is for printing the values that we're
reading repeatedly. We will be using the :py:meth:`~easygopigo3.DistanceSensor.read_mm` method for reading
the distance in millimeters to the target.

.. code-block:: python

    while True:

        # Directly print the values of the sensor.
        print("Distance Sensor Reading (mm): " + str(my_distance_sensor.read_mm()))

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

   See the following :ref:`graphical representation <hardware-ports-section>` as a reference to where the ports are.

.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
