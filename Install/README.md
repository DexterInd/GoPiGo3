# GoPiGo3 Installation

## Using Raspbian for Robots

If you are using Raspbian for Robots, there is no need for an installation, all of the software comes installed.  You may need to run a software update.  

You can find all software and installation for the GoPiGo3 on an SD Card by using [our operating system Raspbian for Robots](https://www.dexterindustries.com/raspberry-pi-robot-software/).  You can [download and install Raspbian for Robots for free with instructions found here](https://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/).  

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot_With_Eyes.jpg)

You can also [purchase an SD Card with the software on it here](https://www.dexterindustries.com/shop/sd-card-raspbian-wheezy-image-for-raspberry-pi/).  

## Installing

You need internet access for the following step(s).

The quickest way for installing the GoPiGo3 is to enter the following command:
```
curl -kL dexterindustries.com/update_gopigo3 | bash
```

By default, the GoPiGo3 package is installed system-wide and [script_tools](https://github.com/DexterInd/script_tools) is completely updated each time the script is ran.

If you still want to go the old route where you first clone the repo and then you run the install script, you can do it by running the following command once cloned:
```
bash update_gopigo3.sh
```

An example using options appended to the command can be:
```
curl -kL dexterindustries.com/update_gopigo3 | bash -s --user-local --no-update-aptget --no-dependencies
```

#### Command Options

The options that can be appended to this command are:

* `--no-dependencies` - skip installing any dependencies for the GoPiGo3. It's supposed to be used on each consecutive update after the initial install has gone through.
* `--no-update-aptget` - to skip using `sudo apt-get update` before installing dependencies. For this to be useful, `--no-dependencies` has to be not used.
* `--bypass-rfrtools` - skip installing RFR_Tools altogether.
* `--bypass-python-rfrtools` - skips installing/updating the python package for  [RFR_Tools](https://github.com/DexterInd/RFR_Tools).
* `--user-local` - install the python package for the GoPiGo3 in the home directory of the user. This doesn't require any special read/write permissions: the actual command used is (`python setup.py install --force --user`).
* `--env-local` - install the python package for the GoPiGo3 within the given environment without elevated privileges: the actual command used is (`python setup.py install --force`).
* `--system-wide` - install the python package for the GoPiGo3 within the sytem-wide environment with `sudo`: the actual command used is (`sudo python setup.py install --force`).

Important to remember is that `--user-local`, `--env-local` and `--system-wide` options are all mutually-exclusive - they cannot be used together.
As a last thing, different versions of it can be pulled by appending a corresponding branch name or tag.

## Test and Troubleshooting
You can see [the test and troubleshooting section on the GoPiGo3, including detailed information about updating the firmwaer, here.](https://www.dexterindustries.com/GoPiGo/get-started-with-the-gopigo3-raspberry-pi-robot/test-and-troubleshoot-the-gopigo3-raspberry-pi-robot/)

## License

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md

# See Also

- [Dexter Industries](http://www.dexterindustries.com/GoPiGo)
- [Dexter Industries Forum Support](http://forum.dexterindustries.com/c/gopigo)
