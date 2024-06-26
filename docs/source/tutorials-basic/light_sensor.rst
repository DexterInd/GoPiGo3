.. _tutorials-basic-light-sensor:

***************
Detecting Light
***************

========
Our goal
========

In this tutorial, we are making a `Grove Light Sensor`_ light up a `Grove Led`_ depending on how strong the intensity
of the light is. The `Grove Light Sensor`_ and the `Grove Led`_ are both connected to the `GoPiGo3`_ and use the following ports.

   * Port ``"AD1"`` for the light sensor.
   * Port ``"AD2"`` for the LED.

.. important::

   Since this tutorial is based on :ref:`Led tutorial <tutorials-basic-led>`, we recommend following that one before going through the current one.


===================
The code we analyse
===================

The code we're analyzing in this tutorial is the following one.

.. code-block:: python

    # import the time library for the sleep function
    import time

    # import the GoPiGo3 drivers
    import easygopigo3 as easy

    # Create an instance of the GoPiGo3 class.
    # GPG will be the GoPiGo3 object.
    gpg = easy.EasyGoPiGo3()

    # Create an instance of the Light sensor
    my_light_sensor = gpg.init_light_sensor("AD1")
    my_led = gpg.init_led("AD2")

    # loop forever while polling the sensor
    while(True):
        # get absolute value
        reading = my_light_sensor.read()
        # scale the reading to a 0-100 scale
        percent_reading = my_light_sensor.percent_read()

        # check if the light's intensity is above 50%
        if percent_reading >= 50:
          my_led.light_off()
        else:
          my_led.light_max()
        print("{}, {:.1f}%".format(reading, percent_reading))

        time.sleep(0.05)

The source code for this tutorial can also be found `here on github <https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/Examples/easy_Light_Sensor.py>`_.


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

After this, we need to instantiate an :py:class:`easygopigo3.EasyGoPiGo3` object.
We are using the :py:class:`~easygopigo3.EasyGoPiGo3` object for creating an instance of :py:class:`~easysensors.Led` class,
which is necessary for controlling the `Grove Led`_ and for reading off of the `Grove Light Sensor`_.

.. code-block:: python

   gpg = easy.EasyGoPiGo3()

Now that we have an :py:class:`~easygopigo3.EasyGoPiGo3` object, we can instantiate
a :py:class:`~easysensors.LightSensor` and :py:class:`~easysensors.Led` objects.
The argument of each of the 2 initializer methods represents the port to which a device is connected.

.. code-block:: python

    my_light_sensor = gpg.init_light_sensor("AD1")
    my_led = gpg.init_led("AD2")

.. note::

   See the following :ref:`graphical representation <hardware-ports-section>` as a reference to where the ports are.

=========
Main part
=========

Let's make the LED behave in the following way.

   * When the light's intensity is below 50%, turn on the LED.
   * When the light's intensity is above 50%, turn off the LED.

To do this, we need to read the percentage value off of the light sensor - the variable responsible for holding the value is called ``percent_reading``.
Depending on the determined percentage, we turn the LED on or off.

To do all this, check out the following code snippet.

.. code-block:: python

    while(True):
        # get absolute value
        reading = my_light_sensor.read()
        # scale the reading to a 0-100 scale
        percent_reading = my_light_sensor.percent_read()

        # check if the light's intensity is above 50%
        if percent_read >= 50:
          my_led.light_off()
        else:
          my_led.light_max()
        print("{}, {:.1f}%".format(reading, percent_reading))

        time.sleep(0.05)

==========
Running it
==========

Here's the fun part. Let's run the python script.

Connect the `Grove Light Sensor`_ to your `GoPiGo3`_ robot to port ``"AD1"`` and `Grove Led`_ to port ``"AD2"``.
Within a terminal on your Raspberry Pi, type the following 2 commands:

.. code-block:: console

    cd ~/Desktop/GoPiGo3/Software/Python/Examples
    python easy_Light_Sensor.py

.. image:: ../images/light_sensor.gif

.. _gopigo3: https://gopigo.io/
.. _assembling instructions: https://gopigo.io/getting-started/
.. _connecting to robot: https://gopigo.io/pairing-gopigo-os/
.. _Tutorials - Basic: tutorials-basic/index.html
.. _shop: https://gopigo.io/shop/
.. _distance sensor: https://gopigo.io/distance-sensor/
.. _light & color sensor: https://gopigo.io/light-and-color-sensor/
.. _grove loudness sensor: https://gopigo.io/grove-loudness-sensor/
.. _grove buzzer: https://gopigo.io/grove-buzzer/
.. _grove led: https://gopigo.io/grove-led-red/
.. _grove button: https://gopigo.io/grove-button/
.. _grove motion sensor: https://gopigo.io/grove-pir-motion-sensor/
.. _servo: https://gopigo.io/servo-package/
.. _line follower sensor: https://gopigo.io/line-follower-for-robots/
.. _infrared receiver: https://gopigo.io/grove-infrared-receiver/
.. _infrared remote: https://gopigo.io/remote-control/
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
.. _forum: http://forum.dexterindustries.com/categories
.. _DI-Sensors: http://di-sensors.readthedocs.io
.. _imu sensor: https://gopigo.io/imu-sensor/
.. _temperature humidity pressure sensor: https://gopigo.io/thp-sensor/
.. _Raspberry Pi camera: https://gopigo.io/raspberry-pi-camera/
.. _DI-Sensors: http://di-sensors.readthedocs.io
.. _Grove Light Sensor: https://wiki.seeedstudio.com/Grove-Light_Sensor/
.. _Grove sound sensor: https://wiki.seeedstudio.com/Grove-Sound_Sensor/
.. _grove ultrasonic sensor: https://wiki.seeedstudio.com/Grove-Ultrasonic_Ranger/
.. _grove dht sensor: https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/