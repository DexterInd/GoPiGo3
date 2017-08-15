# Intelligent Object Avoider Robot

In this project, we make the `GoPiGo3` intelligently avoid obstacles. You need the following:
* [GoPiGo3](https://www.dexterindustries.com/shop/gopigo3-robot-base-kit/)
* [Distance Sensor](https://www.dexterindustries.com/shop/distance-sensor/)
* [Servo Package](https://www.dexterindustries.com/shop/servo-package/)
* Charged battery pack - it comes with the [GoPiGo3](https://www.dexterindustries.com/shop/gopigo3-robot-base-kit/), but it still requires batteries. Works with any other supply as long as it's in the `7-12V` voltage range and is able to supply larger currents (i.e. `5 amps`).

The `servo` is particularly useful, because it gives the distance sensor a 120 degrees viewing angle. The script uses a greedy-like algorithm for choosing the best path.

In order to test this script, it's advised to create at your place a small labyrinth where the `GoPiGo3` can be put in. Books, bags, stools can be used. Avoid creating very sharp corners in your little maze or too small "corridors" as your `GoPiGo3` can get stuck.

This script can only run with `Python 3`.
Don't try to run it with `Python 2` or otherwise, it will fail. Run it with the following command:
* `python3 robot.py`

In order to stop, you need to press the `CTRL-C` combination of keyboard keys. Wait a couple of seconds until it finishes exiting.

## INSERT GIF HERE. I NEED TO BUY SOME BATTERIES.
