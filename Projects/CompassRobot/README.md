# Compass Oriented Robot

In this project, we make the `GoPiGo3` robot follow the 4 cardinal points. In order to control the robot,
a set of keyboard combinations will be displayed in the terminal. The 6 available commands are:

* `<UP>` key - to move the robot towards *North*.
* `<DOWN>` key - to move the robot towards *South*.
* `<LEFT>` key - to move the robot towards *West*.
* `<RIGHT>` key - to move the robot towards *East*.
* `w` key - make the robot move towards a given direction (select one of the above cardinal points).
* `<SPACE>` key - stops the robot (still allows you to use the `<LEFT>`, `<RIGHT>`, etc commands).

## Required Components

* A [`GoPiGo3`](https://www.dexterindustries.com/gopigo3/) robot - that includes the board, the actual robot and the battery pack.
* A [`RaspberryPi`](https://www.dexterindustries.com/shop/raspberry-pi-3/).
* A `DexterIndustries IMU` - only used for getting the magnetometer values.
* A laptop to communicate with the `GoPiGo3`.

## Preparing

In order to run this script, the following extra package is required:

* `DI-Sensors` - it comes with `Raspbian For Robots`. If you don't have `Raspbian For Robots`, the you need to go to [`DI-Sensors`](https://github.com/DexterInd/DI_Sensors) repository and follow the instructions on how to install.

You also need to plug the `IMU` inside the `AD1` port. See the `GoPiGo3` ports' location in the [documentation](http://gopigo3.readthedocs.io/en/latest/api-basic.html#hardware-ports). Then mount the `IMU` sensor like in the following photo.

![DI IMU + GoPiGo3](http://i.imgur.com/bdPfass.jpg)

## DexterOS Notice

In DexterOS it's not needed to install or configure anything. Any required dependency is already installed on it. Just make sure you've got the right physical configuration (sensors, servos, etc) and then run the script this way `python program-name.py`.

## Running It

In order to run this script, we need to use Python 3 exclusively like this:

* `python3 compass_robot.py`

At the beginning of the script, you will be asked to calibrate the robot by rotating it. Just rotate the `GoPiGo3` robot in the air for a couple of seconds and the robot should then be good to go.

After the calibration is done, your terminal should look like this.

![Script terminal](http://i.imgur.com/4PWYzkv.png)

Now, play with it!

#### Warning: the compass (DI IMU) is very sensitive to any electronic/electric devices (laptops, PCs, smartphones, LCDs, etc). This devices will affect the determined heading of the robot.

## Compass Considerations

The geographical location of the North pole is never static and it constantly changes as times passes.
This means the North pole doesn't have to be exactly at the North pole of Earth - that's just a general convention. Right now, the North pole is situated somewhere near Canada, so that's pretty far away from what we consider the North pole.

In order to determine where that should be, engineers use the actual geographical location of the North pole along with a GPS. With these 2, the so-called [*magnetic declination*](https://en.wikipedia.org/wiki/Magnetic_declination) is calculated and then added to the determined heading.
In this project, we haven't used a `GPS` and so, we don't know what's the *magnetic declination*. Therefore, the heading we are getting actually represents the direction of the [Earth's magnetic field lines](https://en.wikipedia.org/wiki/Earth%27s_magnetic_field) in that geographical location.

For setting up the magnetic declination, do the following 2 steps:

1. Go to [magnetic-declination](http://www.magnetic-declination.com/) website and find out the declination in your geographical region.

1. Assign your location's magnetic declination to `MAGNETIC_DECLINATION` constant. The constant is found in the `compass_robot.py` script. By default, `MAGNETIC_DECLINATION` is set to `0`.

Here's a visual representation of the Earth's variation of the magnetic field (as of 2015).

* The **red** lines indicate a **negative** variation between the real North pole's location and the compass' heading.
* The **blue** lines indicate a **positive** variation between the real North pole's location and the compass' heading.
* The **green** lines indicate **0** variation between real North pole's location and the compass' heading.

![Imgur](http://i.imgur.com/cLaPxFV.png)

For more information, please checkout the [NOAA(National Centers For Environmental Information)](https://maps.ngdc.noaa.gov/viewers/historical_declination/).
