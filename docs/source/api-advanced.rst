##############################
API Reference Point - Advanced
##############################

============
Requirements
============

Before using this chapter's classes, you need to be able to import the following modules.

.. code-block:: python

   import easygopigo3
   import gopigo3

Unless you're already running `Raspbian For Robots`_ , make sure the `gopigo3 package`_ is installed as otherwise an import error will be thrown.

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
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
