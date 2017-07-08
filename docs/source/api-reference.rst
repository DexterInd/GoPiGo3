###################
API Reference Point
###################

.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/

.. _physical ports:

**************************
GoPiGo3 Ports
**************************

.. role:: red

.. role:: orange

.. role:: blue

.. role:: green

.. role:: yellow


In this graphical representation, the `GoPiGo3`_ board has the following ports available for use.

.. image:: gpg3_ports.jpg

.. note::

   Use the quoted port names when referencing them inside a python script like in the following example.

   .. code-block:: python

      # we need an EasyGoPiGo3 object for instantiating sensor / actuator objects
      gpg3_obj = EasyGoPiGo3()

      # we're using the quoted port names from the above graphical representation

      # here's a LightSensor object binded on port AD2
      light_obj = gpg3_obj.init_light_sensor("AD2")

      # here's a UltraSonicSensor object binded on port AD1
      us_obj = gpg3_obj.init_ultrasonic_sensor("AD1")

      # here's a LineFollower object binded on port I2C
      line_follower_obj = gpg3_obj.init_line_follower("I2C")

      # and so on

**************************
``easygopigo3`` Module
**************************

=====================================
EasyGoPiGo3
=====================================

.. autoclass:: easygopigo3.EasyGoPiGo3
   :members:
   :special-members:

=====================================
Sensor
=====================================

=====================================
DigitalSensor
=====================================

=====================================
AnalogSensor
=====================================

=====================================
LightSensor
=====================================

.. autoclass:: easygopigo3.LightSensor
   :members:
   :special-members:

=====================================
SoundSensor
=====================================

=====================================
UltrasonicSensor
=====================================

=====================================
Buzzer
=====================================

=====================================
Led
=====================================

=====================================
ButtonSensor
=====================================

=====================================
LineFollower
=====================================

=====================================
Servo
=====================================

=====================================
DistanceSensor
=====================================

=====================================
DHTSensor
=====================================
