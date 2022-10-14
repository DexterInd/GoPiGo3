.. _tutorials-basic-distance-sensor:

**********************************
Measuring Distance
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

    # This example shows how to read values from the Distance Sensor

    # Create an instance of the GoPiGo3 class.
    # GPG will be the GoPiGo3 object.
    gpg = easy.EasyGoPiGo3()

    # Create an instance of the Distance Sensor class.
    # I2C1 and I2C2 are just labels used for identifyng the port on the GoPiGo3 board.
    # But technically, I2C1 and I2C2 are the same thing, so we don't have to pass any port to the constructor.
    my_distance_sensor = gpg.init_distance_sensor()

    while True:
        # Directly print the values of the sensor.
        print("Distance Sensor Reading (mm): " + str(my_distance_sensor.read_mm()))

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

For interfacing with the `Distance Sensor`_ we need to instantiate an object of the :py:class:`easygopigo3.EasyGoPiGo3` class so in return, we can instantiate an object of the :py:class:`di_sensors.easy_distance_sensor.EasyDistanceSensor` class.
We do it like in the following code snippet.

.. code-block:: python

   gpg = easy.EasyGoPiGo3() # this is an EasyGoPiGo3 object
   my_distance_sensor = gpg.init_distance_sensor() # this is a DistanceSensor object

.. important::
  Notice that in order for this to work, we also need to have the `DI-Sensors`_ library installed. Follow the instructions on that documentation on how to install the required package.

=========
Main part
=========

There's a single while loop in the entire script. The loop is for printing the values that we're
reading repeatedly. We will be using the :py:meth:`~di_sensors.easy_distance_sensor.EasyDistanceSensor.read_mm` method for reading
the distance in millimeters to the target.

.. code-block:: python

    while True:

        # Directly print the values of the sensor.
        print("Distance Sensor Reading (mm): " + str(my_distance_sensor.read_mm()))

.. seealso::

     Check out :py:class:`di_sensors.easy_distance_sensor.EasyDistanceSensor`'s API for more details.

==========
Running it
==========

Connect the `Distance Sensor`_ to any of the 2 ``"I2C"`` ports on the `GoPiGo3`_ robot.
After the sensor is connected, on your Raspberry Pi, open up a terminal and type in the following 2 commands.

.. code-block:: console

    cd ~/Desktop/GoPiGo3/Software/Python/Examples
    python easy_Distance_Sensor.py

.. image:: ../images/dist_sensor.gif

.. note::

   See the following :ref:`graphical representation <hardware-ports-section>` as a reference to where the ports are.

.. _DI-Sensors: http://di-sensors.readthedocs.io
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
