# GoPiGo3 Installation

## Using Raspbian for Robots

If you are using Raspbian for Robots, there is no need for an installation, all of the software comes installed.  You may need to run a software update.

You can find all software and installation for the GoPiGo3 on an SD Card by using [our operating system Raspbian for Robots](https://www.dexterindustries.com/raspberry-pi-robot-software/).  You can [download and install Raspbian for Robots for free with instructions found here](https://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/).

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot_With_Eyes.jpg)

You can also [purchase an SD Card with the software on it here](https://www.dexterindustries.com/shop/sd-card-raspbian-wheezy-image-for-raspberry-pi/).

## Quick Install

Instead of cloning the repository and then running the install script, you can just enter the following command and then reboot your Raspberry Pi:
```
sudo curl -kL dexterindustries.com/update_gopigo3 | bash
```

## Installation
You can install the GoPiGo3 on your own operating system with the following commands in the command line:
1. Clone this repository onto the Raspberry Pi:
```
sudo git clone http://www.github.com/DexterInd/GoPiGo3.git /home/pi/Dexter/GoPiGo3
```
2. Run the install script:
```
sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh
```
3. Reboot the Raspberry Pi to make the settings take effect:
```
sudo reboot
```

## Test and Troubleshooting
You can see [the test and troubleshooting section on the GoPiGo3, including detailed information about updating the firmwaer, here.](https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/test-and-troubleshoot-the-gopigo3-raspberry-pi-robot/)

## License

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md

# See Also

- [Dexter Industries](http://www.dexterindustries.com/GoPiGo)
- [Dexter Industries Forum Support](http://forum.dexterindustries.com/c/gopigo)
