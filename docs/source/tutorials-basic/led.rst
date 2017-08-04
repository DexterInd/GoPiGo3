.. _tutorials-basic-led:

***************
Flashing an LED
***************

========
Our goal
========

In this tutorial, we are making a `Grove Led`_ flash continuously, while it's being connected to a `GoPiGo3`_ robot.


===================
The code we analyse
===================

The code we're analyzing in this tutorial is the following one.

.. code-block:: python

    # import the EasyGoPiGo3 drivers
    import time
    import easygopigo3 as easy

    # Create an instance of the GoPiGo3 class.
    # GPG will be the GoPiGo3 object.
    gpg = easy.EasyGoPiGo3()


    # create the LED instance, passing the port and GPG
    my_led = gpg.init_led("AD1")
    # or
    # my_LED = easy.Led("AD1", GPG)

    # loop 100 times
    for i in range(100):
        my_led.light_max() # turn LED at max power
        time.sleep(0.5)

        my_led.light_on(30)  # 30% power
        time.sleep(0.5)

        my_led.light_off() # turn LED off
        time.sleep(0.5)

The source code for this example program can be found `here on github <https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/Examples/easy_LED.py>`_.

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
We are using the :py:class:`~easygopigo3.EasyGoPiGo3` object for creating an instance of :py:class:`~easygopigo3.Led` class,
which is necessary for controlling the `Grove Led`_ device.

.. code-block:: python

   gpg = easy.EasyGoPiGo3()

Now that we have an :py:class:`~easygopigo3.EasyGoPiGo3` object, we can instantiate
a :py:class:`~easygopigo3.Led` object.
The argument of the initializer method is the port to which we connect the `Grove Led`_ and
it's set to ``"AD1"``.

.. code-block:: python

   my_led = gpg.init_led("AD1")

.. note::

   See the following :ref:`graphical representation <hardware-ports-section>` as a reference to where the ports are.

=========
Main part
=========

In this section of the tutorial we are focusing on 3 methods of the :py:class:`easygopigo3.Led` class.

   * The :py:meth:`~easygopigo3.Led.light_max` method - which turns the LED at the maximum brightness.
   * The :py:meth:`~easygopigo3.Led.light_on` method - used for turning the LED at a certain percent of the maximum brightness.
   * The :py:meth:`~easygopigo3.Led.light_off` method - used for turning off the LED.

All in all, the following code snippet turns on the LED to the maximum brightness, then it sets the LED's brightness at 30%
and in the last it turns off the LED. The delay between all these 3 commands is set at half a second.

.. code-block:: python

    for i in range(100):
        my_led.light_max() # turn LED at max power
        time.sleep(0.5)

        my_led.light_on(30)  # 30% power
        time.sleep(0.5)

        my_led.light_off() # turn LED off
        time.sleep(0.5)

==========
Running it
==========

Connect the `Grove Led`_ to your `GoPiGo3`_ robot to port ``"AD1"`` and then let's crank up the Raspberry Pi.
For running the analyzed example program, within a terminal on your Raspberry Pi, type the following 2 commands:

.. code-block:: console

    cd ~/Desktop/GoPiGo3/Software/Python/Examples
    python easy_LED.py

.. image:: http://i.imgur.com/OhqtJAO.gif


.. _grove led: https://www.dexterindustries.com/shop/grove-red-led/
.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
