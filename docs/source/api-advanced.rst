.. _api-advanced-chapter:

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

If you have issues importing these 2 modules, then make sure that:

   * You've followed the steps found in :ref:`Getting Started <getting-started-chapter>` guide.
   * You have installed either `Raspbian For Robots`_, the GoPiGo3 `repository`_ or the `GoPiGo3 package`_ (the pip package).
   * You have the ``gopigo3`` package installed by typing the command ``pip freeze | grep gopigo3`` on your Raspberry Pi's terminal. If the package is installed, then a string with the ``GoPiGo3==[x.y.z]`` format will show up.

If you encounter issues that aren't covered by our :ref:`Getting Started <getting-started-chapter>` guide or :ref:`FAQ <faq-chapter>` chapter, please head over to our `forum`_.

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

.. note::

   Being developed!

=====================================
AnalogSensor
=====================================

.. autoclass:: easygopigo3.AnalogSensor
  :members:
  :special-members:


.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _gopigo3 package: https://pypi.python.org/pypi/gopigo3
.. _shop: https://www.dexterindustries.com/shop/
.. _infrared receiver: https://www.seeedstudio.com/Grove-Infrared-Receiver-p-994.html
.. _repository: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/3-program-your-raspberry-pi-robot/python-programming-language/
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
.. _forum: http://forum.dexterindustries.com/categories
