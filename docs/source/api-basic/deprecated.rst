*************************************
API - Deprecated
*************************************

In earlier versions of this library, all classes of the :py:mod:`easysensors` module belonged to :py:mod:`easygopigo3` module.
This can potentially make scripts written on a older version of this not work anymore. In order to prevent this problem, we have created dummy functions
of each class of the :py:mod:`easysensors` module and placed them in :py:mod:`easygopigo3`. Since these functions take the same arguments as the classes that were in previously
and because they return an object, the scripts that were built on that long-gone API still work.

We intent to support these "dummy" functions for a while before we retire them.

In summary, the classes that are now being instantiated from the :py:mod:`easysensors` can still be instantiated from :py:mod:`easygopigo3` for a while. These classes are:


.. autosummary::
   easygopigo3.LightSensor
   easygopigo3.SoundSensor
   easygopigo3.LoudnessSensor
   easygopigo3.UltraSonicSensor
   easygopigo3.Buzzer
   easygopigo3.Led
   easygopigo3.MotionSensor
   easygopigo3.ButtonSensor
   easygopigo3.Remote
   easygopigo3.LineFollower
   easygopigo3.Servo
   easygopigo3.DHTSensor

The only exception is the :py:func:`easygopigo3.DistanceSensor` which class no longer exists in either module.
This surrogate function has the same arguments as the other classes and the only port available to use is the ``"I2C"``.
If you wish to initialize an object for the `Distance Sensor`_, a better way is just to use the :py:class:`~di_sensors.distance_sensor.DistanceSensor` class of `DI-Sensors`_ library on which this library is based upon.

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