# Mouse Control Project

In this project, you'll be able to control your `GoPiGo3` robot with a ``wireless mouse``.
Make sure you connect a `wireless mouse` to your `Raspberry Pi` and then launch the script (preferably with SSH).

![GoPiGo3 with Mouse](http://i.imgur.com/Rat5EQN.jpg)

When the ``mouse_control_robot`` script is launched (with either Python 2 or 3), the user
is prompted to input a value which represents the mode of operation:

* When the input value is `choice = 1`, the robot gets to be controlled by the mouse's buttons. Here's a list on what each combination of buttons does:
  * The `left` button of the mouse - moves the `GoPiGo3` to the left.
  * The `right` button of the mouse - moves the `GoPiGo3` to the right.
  * The `middle` button of the mouse - moves the `GoPiGo3` backward.
  * Both the `left` & the `right` buttons of the mouse - moves the `GoPiGo3` forward.
  * Not pressing any button keeps the robot stationary.

* When the input value is `choice = 2`, the robot gets to be controlled by the mouse's movements.
  * Moving the mouse `forward`, makes the `GoPiGo3` to move forward.
  * Moving the mouse `backward`, makes the `GoPiGo3` to move backward.
  * Moving the mouse to the `left`, makes the `GoPiGo3` to move to the left.
  * Moving the mouse to the `right`, makes the `GoPiGo3` to move to the right.
  * Not moving the mouse in any direction keeps the robot stationary.

When closing the app, press the `CTRL-C` combination of keys and move the mouse around just a little bit, so that the process stops. That's because the script uses blocking methods and while the mouse is stationary (and no buttons are pressed), the script is in a state of *"waiting"*.  

![](http://i.imgur.com/K5ZK8fj.gif)

## On DexterOS
In DexterOS it's not needed to install or configure anything. Any required dependency is already installed on it. Just make sure you've got the right physical configuration (sensors, servos, etc) and then run the script this way `python program-name.py`.
