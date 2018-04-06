# GoPiGo3 [![Documentation Status](https://readthedocs.org/projects/gopigo3/badge/?version=master)](http://gopigo3.readthedocs.io/en/latest/?badge=master)

The GoPiGo3 is a delightful and complete robot for the Raspberry Pi that turns your Pi into a fully operating robot.  GoPiGo3 is a mobile robotic platform for the Raspberry Pi developed by [Dexter Industries.](http://www.dexterindustries.com/GoPiGo)

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot.jpg)

# Raspbian for Robots

You can find all software and installation for the GoPiGo3 on an SD Card by using [our operating system Raspbian for Robots](https://www.dexterindustries.com/raspberry-pi-robot-software/).  You can [download and install Raspbian for Robots for free with instructions found here](https://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/).  

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot_With_Eyes.jpg)

You can also [purchase an SD Card with the software on it here](https://www.dexterindustries.com/shop/sd-card-raspbian-wheezy-image-for-raspberry-pi/).  

# Installation
You can install the GoPiGo3 on your own operating system with the following commands in the command line:
1. Clone this repository onto the Raspberry Pi:

        sudo git clone http://www.github.com/DexterInd/GoPiGo3.git /home/pi/Dexter/GoPiGo3

2. Run the install script: `sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh`
3. Reboot the Raspberry Pi to make the settings take effect: `sudo reboot`


# Quick Install
In order to quick install the `GoPiGo3` repository, open up a terminal and type one of the 2 following commands:

1. For installing the python packages of the `GoPiGo3` with root privileges (except any other settings that can come with), use the following command:
```
curl -kL dexterindustries.com/update_gopigo3 | sudo bash
```

2. For installing the python packages of the `GoPiGo3` without root privileges (except any other settings that can come with), use the following command:
```
curl -kL dexterindustries.com/update_gopigo3 | bash
```
The same command can be used for updating the `GoPiGo3` to the latest version.

# License

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md

# See Also

- [Dexter Industries](http://www.dexterindustries.com/GoPiGo)
- [Dexter Industries Forum Support](http://forum.dexterindustries.com/c/gopigo)
