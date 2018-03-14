*************************************
Deprecated Classes/Functions
*************************************

In earlier versions of this library, all classes of the :py:mod:`easysensors` module belonged to :py:mod:`easygopigo3` module.
This can potentially make scripts written on a older version of this not work anymore. In order to prevent this problem, we have created dummy functions
of each class of the :py:mod:`easysensors` module and placed them in :py:mod:`easygopigo3`. Since these functions take the same arguments as the classes that were in previously
and because they return an object, the scripts that were built on that long-gone API still work.

We intent to support these "dummy" functions for a while before we retire them.

In summary, the classes that are now being instantiated from the :py:mod:`easysensors` can still be instantiated from :py:mod:`easygopigo3` for a while. These classes are:


.. autosummary::
   easysensors.LightSensor
   easysensors.SoundSensor
   easysensors.LoudnessSensor
   easysensors.UltraSonicSensor
   easysensors.Buzzer
   easysensors.Led
   easysensors.MotionSensor
   easysensors.ButtonSensor
   easysensors.Remote
   easysensors.LineFollower
   easysensors.Servo
   easysensors.DHTSensor

.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _infrared receiver: https://www.dexterindustries.com/shop/grove-infrared-sensor/
.. _grove light sensor: https://www.dexterindustries.com/shop/grove-light-sensor/
.. _grove sound sensor: https://www.dexterindustries.com/shop/grove-sound-sensor/
.. _grove loudness sensor: http://wiki.seeed.cc/Grove-Loudness_Sensor/
.. _grove ultrasonic sensor: https://www.dexterindustries.com/shop/ultrasonic-sensor/
.. _grove buzzer: https://www.dexterindustries.com/shop/grove-buzzer/
.. _grove led: https://www.dexterindustries.com/shop/grove-red-led/
.. _grove button: https://www.dexterindustries.com/shop/grove-button/
.. _grove motion sensor: https://www.dexterindustries.com/shop/grove-pir-motion-sensor/
.. _grove dht sensor: https://www.dexterindustries.com/shop/temp-humidity/
.. _servo: https://www.dexterindustries.com/shop/servo-package/
.. _line follower: https://www.dexterindustries.com/shop/line-follower-for-gopigo/
.. _infrared remote: https://www.dexterindustries.com/shop/infrared-remote/
