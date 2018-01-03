.. _api-advanced-chapter:

######################
API GoPiGo3 - Advanced
######################

============
Requirements
============

Before using this chapter's classes, you need to be able to import the following module.

.. code-block:: python

   import easygopigo3

If you have issues importing this module, then make sure that:

   * You've followed the steps found in :ref:`Getting Started <getting-started-chapter>` guide.
   * You have installed either `Raspbian For Robots`_, the GoPiGo3 `repository`_ or the `GoPiGo3 package`_ (the pip package).
   * You have the ``gopigo3`` package installed by typing the command ``pip freeze | grep gopigo3`` on your Raspberry Pi's terminal. If the package is installed, then a string with the ``gopigo3==[x.y.z]`` format will show up.

If you encounter issues that aren't covered by our :ref:`Getting Started <getting-started-chapter>` guide or :ref:`FAQ <faq-chapter>` chapter, please head over to our `forum`_.

Take note that the easygopigo3 module depends on the underlying gopigo3 module.  The base gopigo3 module contains lower level calls that would allow you finer control over your GoPiGo3 and its functionality is available to you once easygopigo3 is imported.

=====================================
Sensor
=====================================

.. autoclass:: easygopigo3.Sensor
  :members:
  :special-members:
  :exclude-members: __weakref__
  :show-inheritance:

=====================================
DigitalSensor
=====================================

.. note::

   Coming soon!

=====================================
AnalogSensor
=====================================

.. autoclass:: easygopigo3.AnalogSensor
  :members:
  :special-members:
  :show-inheritance:


.. _distance sensor: https://www.dexterindustries.com/shop/distance-sensor/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _gopigo3 package: https://pypi.python.org/pypi/gopigo3
.. _shop: https://www.dexterindustries.com/shop/
.. _infrared receiver: https://www.dexterindustries.com/shop/grove-infrared-sensor/
.. _repository: https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/3-program-your-raspberry-pi-robot/python-programming-language/
.. _raspbian for robots: https://sourceforge.net/projects/dexterindustriesraspbianflavor/
.. _forum: http://forum.dexterindustries.com/categories
