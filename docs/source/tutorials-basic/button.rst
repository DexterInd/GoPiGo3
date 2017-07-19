.. _tutorials-basic-button:

****************
Pushing a Button
****************

==========
Our target
==========

In this tutorial, we are going to control `GoPiGo3`_ Dex's eyes with a `Grove Button`_.

   * When the `Grove Button`_ is pressed, Dex's eyes turn on.
   * When the `Grove Button`_ is released, Dex's eyes turn off.


===================
The code we analyse
===================

In the end the code should look like this.

.. code-block:: python

  # import the time library for the sleep function
  import time

  # import the GoPiGo3 drivers
  import easygopigo3 as easy

  # Create an instance of the GoPiGo3 class.
  # GPG will be the GoPiGo3 object.
  gpg = easy.EasyGoPiGo3()

  # Put a grove button in port AD1
  my_button = gpg3.init_button_sensor("AD1")

  print("Ensure there's a button in port AD1")
  print("Press and release the button as often as you want")
  print("the program will run for 2 minutes or")
  print("Ctrl-C to interrupt it")


  start = time.time()
  RELEASED = 0
  PRESSED = 1
  state = RELEASED

  while time.time() - start < 120:

      if state == RELEASED and my_button.read() == 1:
          print("PRESSED")
          gpg.open_eyes()
          state = PRESSED
      if state == PRESSED and my_button.read() == 0:
          print("RELEASED")
          gpg.close_eyes()
          state = RELEASED
      time.sleep(0.05)

  print("All done!")

The source code for this example program can be found `here on github <https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/Examples/easy_Button.py>`_.

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
The :py:class:`~easygopigo3.EasyGoPiGo3` object is used for 2 things:

   * For turning *ON* and *OFF* the `GoPiGo3`_ Dex's eyes.
   * For instantiating a :py:class:`~easygopigo3.ButtonSensor` object for reading the `Grove Button`_'s state.

.. code-block:: python

   gpg = easy.EasyGoPiGo3()

Now that we have an :py:class:`~easygopigo3.EasyGoPiGo3` object, we can instantiate
a :py:class:`~easygopigo3.ButtonSensor` object.
The argument of the initializer method is the port to which we connect the `Grove Button`_ and
it's set to ``"AD1"``.

.. code-block:: python

   my_button = gpg3.init_button_sensor("AD1")

.. note::

   For knowing where the ports are located on the robot (like port ``"AD1"``), see the following :ref:`graphical representation <hardware-ports-section>`.

=================
Setting variables
=================

Define 2 states for the button we're using.
We are setting the default state to ``"RELEASED"``.

.. code-block:: python

   start = time.time()
   RELEASED = 0
   PRESSED = 1
   state = RELEASED

There's also a variable called ``start`` to which we assign the clock time of that moment.
We use it to limit for how long the script runs.

=========
Main part
=========

The main part is basically a while loop that's going to run for 120 seconds.
Within the while loop, we have 2 ``if / else`` blocks that define a simple algorithm:
whenever the previous state is different from the current one, we either turn on or close
Dex's eyes. Here's the logic:

   * If in the previous iteration of the while loop the button was **released** and now the button is **1** (aka **pressed**), then we turn **on** the LEDs and save the new state in ``state`` variable.
   * If in the previous iteration of the while loop the button was **pressed** and now the button is **0** (aka **released**), then we turn **off** the LEDs and save the new state in ``state`` variable.

This way, we don't call ``gpg.open_eyes()`` all the time when the button is pressed or ``gpg.close_eyes()`` when the button is released.
It only needs to call one of these 2 functions once.

.. code-block:: python

  while time.time() - start < 120:

    if state == RELEASED and my_button.read() == 1:
      print("PRESSED")
      gpg.open_eyes()
      state = PRESSED
    if state == PRESSED and my_button.read() == 0:
      print("RELEASED")
      gpg.close_eyes()
      state = RELEASED

    time.sleep(0.05)

``time.sleep(0.05)`` was added to limit the CPU time. 50 mS is more than enough.

==========
Running it
==========

Make sure you have connected the `Grove Button`_ to your `GoPiGo3`_ robot to port ``"AD1"``.
Then, on the Rasperry Pi, from within a terminal, type the following commands.

.. code-block:: console

   cd ~/Desktop/GoPiGo3/Software/Python/Examples
   python easy_Button.py

.. image:: http://i.imgur.com/6SQr3vY.gif




.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _grove button: https://www.dexterindustries.com/shop/grove-button/
