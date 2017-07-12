###########################
API Reference Point - Basic
###########################

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

.. _physical ports:

=====================================
Hardware Ports
=====================================

In this graphical representation, the `GoPiGo3`_ board has the following ports available for use.
The quoted literals are to be used as pin identifiers inside the python scripts.

.. image:: gpg3_ports.jpg

These ports have the following functionalities:

   * Ports ``"AD1"`` and ``"AD2"`` - general purpose input/output ports.
   * Ports ``"SERVO1"`` and ``"SERVO2"`` - servo controller ports.
   * Ports ``"I2C"`` - ports to which you can connect I2C-enabled devices.
   * Port ``"SERIAL"`` - port to which you can connect UART-enabled device.

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

.. seealso::

   For more technical details on the `GoPiGo3`_ robot, please check our `technical specs`_ page.


=====================================
EasyGoPiGo3
=====================================

.. autoclass:: easygopigo3.EasyGoPiGo3
   :members:
   :special-members:

=====================================
LightSensor
=====================================

.. autoclass:: easygopigo3.LightSensor
   :members:
   :special-members:

=====================================
SoundSensor
=====================================

.. autoclass:: easygopigo3.SoundSensor
   :members:
   :special-members:

=====================================
UltrasonicSensor
=====================================

.. autoclass:: easygopigo3.UltraSonicSensor
   :members:
   :special-members:

=====================================
Buzzer
=====================================

.. autoclass:: easygopigo3.Buzzer
   :members:
   :special-members:

=====================================
Led
=====================================

.. autoclass:: easygopigo3.Led
   :members:
   :special-members:

=====================================
ButtonSensor
=====================================

.. autoclass:: easygopigo3.ButtonSensor
   :members:
   :special-members:

=====================================
LineFollower
=====================================

.. autoclass:: easygopigo3.LineFollower
   :members:
   :special-members:

=====================================
Servo
=====================================

.. autoclass:: easygopigo3.Servo
   :members:
   :special-members:

=====================================
DistanceSensor
=====================================

.. autoclass:: easygopigo3.DistanceSensor
   :members:
   :special-members:

=====================================
DHTSensor
=====================================

.. warning::

   Coming soon!

##############################
API Reference Point - Advanced
##############################

=====================================
Sensor
=====================================

.. autoclass:: easygopigo3.Sensor
  :members:
  :special-members:
  :exclude-members: __weakref__

=====================================
DigitalSensor
=====================================

.. warning::

   Coming soon!

=====================================
AnalogSensor
=====================================

.. warning::

   Class has some issues - not ready for general use.

.. autoclass:: easygopigo3.AnalogSensor
  :members:
  :special-members:
