.. _tutorials-basic-buzzer:

****************
Ringing a Buzzer
****************

==========
Our target
==========

In this tutorial, we are making a `Grove Buzzer`_ play different musical tones on our `GoPiGo3`_ robot.
We start off with 3 musical notes and finish by playing the all-known *"Twinkle Twinklle Little Star"* song.

===================
The code we analyse
===================

The code we're analyzing in this tutorial is this.

.. code-block:: python

  # import the time library for the sleep function
  import time

  # import the GoPiGo3 drivers
  import easygopigo3 as easy

  # Create an instance of the GoPiGo3 class.
  # GPG will be the GoPiGo3 object.
  gpg = easy.EasyGoPiGo3()

  # Create an instance of the Buzzer
  # connect a buzzer to port AD2
  my_buzzer = gpg.init_buzzer("AD2")

  twinkle = ["C4","C4","G4","G4","A4","A4","G4"]

  print("Expecting a buzzer on Port AD2")
  print("A4")
  my_buzzer.sound(440)
  time.sleep(1)
  print("A5")
  my_buzzer.sound(880)
  time.sleep(1)
  print("A3")
  my_buzzer.sound(220)
  time.sleep(1)

  for note in twinkle:
      print(note)
      my_buzzer.sound(buzzer.scale[note])
      time.sleep(0.5)
      my_buzzer.sound_off()
      time.sleep(0.25)

  my_buzzer.sound_off()


The source code for this example program can be found `here on github <https://github.com/DexterInd/GoPiGo3/blob/master/Software/Python/Examples/easy_Buzzer.py>`_.

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
We are using the :py:class:`~easygopigo3.EasyGoPiGo3` object for creating an instance of :py:class:`~easygopigo3.Buzzer` class,
which is necessary for controlling the `Grove Buzzer`_ device.

.. code-block:: python

   gpg = easy.EasyGoPiGo3()

Now that we have an :py:class:`~easygopigo3.EasyGoPiGo3` object, we can instantiate
a :py:class:`~easygopigo3.Buzzer` object.
The argument of the initializer method is the port to which we connect the `Grove Buzzer`_ and
it's set to ``"AD2"``.

.. code-block:: python

   my_buzzer = gpg.init_buzzer("AD2")

.. note::

   See the following :ref:`graphical representation <hardware-ports-section>` as a reference to where the ports are.

=================
Setting variables
=================

For playing *"Twinkle Twinkle Little Star"* song, we need to have a sequence of musical notes that describe this song.
We're encoding the musical notes into a list (called ``twinkle``) of strings, where each string represents a musical note.

.. code-block:: python

   twinkle = ["C4","C4","G4","G4","A4","A4","G4"]

=========
Main part
=========

The main zone of the code is divided into 2 sections:

   1. The 1st section, where we only play 3 musical notes which are split apart by delays worth of 1 second (each).
   2. The 2nd section, where we play the lovely *"Twinkle Twinkle Little Start"* song.

In the 1st section we are using the :py:meth:`easygopigo3.Buzzer.sound` method, which takes as a paramater,
an integer that represents the frequency of the emitted sound. As you can see in the following code snippet,
each musical note corresponds with a certain frequency:

   * The frequency of *A4* musical note is *440Hz*.
   * The frequency of *A5* musical note is *880Hz*.
   * The frequency of *A3* musical note is *220Hz*.

.. code-block:: python

    print("A4")
    my_buzzer.sound(440)
    time.sleep(1)

    print("A5")
    my_buzzer.sound(880)
    time.sleep(1)

    print("A3")
    my_buzzer.sound(220)
    time.sleep(1)

In the 2nd section we are using the :py:attr:`~easygopigo3.Buzzer.scale` dictionary.
In this dictionary there are stored the frequencies of each musical note.
So, when using the ``twinkle`` list in conjuction with :py:attr:`~easygopigo3.Buzzer.scale` attribute,
we're basically retrieving the frequency of a musical note (found in ``twinkle`` attribute) from the :py:attr:`~easygopigo3.Buzzer.scale` dictionary.

.. code-block:: python

    for note in twinkle:
        print(note)
        my_buzzer.sound(buzzer.scale[note])
        time.sleep(0.5)
        my_buzzer.sound_off()
        time.sleep(0.25)

==========
Running it
==========

The only thing left to do is to connect the `Grove Buzzer`_ to your `GoPiGo3`_ robot to port ``"AD2"``.
Then, on your Raspberry Pi, from within a terminal, type the following commands:

.. code-block:: console

    cd ~/Desktop/GoPiGo3/Software/Python/Examples
    python easy_Buzzer.py

.. tip::

   Please don't expect to hear a symphony, because the buzzer wasn't made for playing tones.
   We use the buzzer within this context to only demonstrate that it's a nice feature.


.. _gopigo3: https://www.dexterindustries.com/shop/gopigo-advanced-starter-kit/
.. _grove buzzer: https://www.dexterindustries.com/shop/grove-buzzer/
