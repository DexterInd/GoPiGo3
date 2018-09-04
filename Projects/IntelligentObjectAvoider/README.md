# Intelligent Object Avoider Robot

## Component Requirements

In this project, we make the `GoPiGo3` intelligently avoid obstacles. You need the following:
* [GoPiGo3](https://www.dexterindustries.com/shop/gopigo3-robot-base-kit/)
* [Distance Sensor](https://www.dexterindustries.com/shop/distance-sensor/)
* [Servo Package](https://www.dexterindustries.com/shop/servo-package/)
* Charged battery pack - it comes with the [GoPiGo3](https://www.dexterindustries.com/shop/gopigo3-robot-base-kit/), but it still requires batteries. Works with any other supply as long as it's in the `7-12V` voltage range and is able to supply larger currents (i.e. `5 amps`).

The `servo` is particularly useful, because it gives the distance sensor a 120 degrees viewing angle. The script uses a greedy-like algorithm for choosing the best path.

## DexterOS Notice

In DexterOS it's not needed to install or configure anything. Any required dependency is already installed on it. Just make sure you've got the right physical configuration (sensors, servos, etc) and then run the script this way `python program-name.py`.

## Preparing It

You need to do the following things in order to be able to launch the `robot.py` script:
1. Install `scikit-learn` package. A `sudo pip3 install scikit-learn` should be enough (be mindful of whether you need to use `sudo` or not - most probably it's `sudo` that's required).
Generally, `pip` is associated for `Python 2` applications and `pip3` is associated for `Python 3` apps, so most likely, on your system, you'll have to do use the `pip3` command.
2. Plug in the servo into port `SERVO 1` of the GoPiGo3 just like in the below photo.
3. Plug in the distance sensor into any of the 2 `I2C` ports of the GoPiGo3 just like in the below photo.
4. Run the actual script. Use only `Python 3` as `Python 2` is not supported.

## Running It

In order to run it, use the following command:
```
python3 robot.py
```

Depending on how your system is set, the Python 3 executable may be set to `python` or `python3`. To find out which executable you're dealing with, use the `-V` option when
calling the executable to see which version it is: `python -V` or `python3 -V`.

In order to stop, you need to press the `CTRL-C` combination of keyboard keys. Wait a couple of seconds until it finishes exiting.

## Robot Environment

In order to test this script, create a small labyrinth for your `GoPiGo3`. Books, bags, stools can be used. Avoid creating very sharp corners in your little maze or too small "corridors" as your `GoPiGo3` can get stuck.

![Imgur](http://i.imgur.com/LbuFTMd.jpg)
