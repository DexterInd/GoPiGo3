# GoPiGo3 for Node.js

The GoPiGo3 is a delightful and complete robot for the Raspberry Pi that turns your Pi into a fully operating robot.  GoPiGo3 is a mobile robotic platform for the Raspberry Pi developed by [Dexter Industries.](http://www.dexterindustries.com/GoPiGo) 

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot.jpg)

# Raspbian for Robots

You can find all software and installation for the GoPiGo3 on an SD Card by using [our operating system Raspbian for Robots](https://www.dexterindustries.com/raspberry-pi-robot-software/).  You can [download and install Raspbian for Robots for free with instructions found here](https://www.dexterindustries.com/howto/install-raspbian-for-robots-image-on-an-sd-card/).  

![ GoPiGo3 Raspberry Pi Robot ](https://raw.githubusercontent.com/DexterInd/GoPiGo3/master/GoPiGo3_Raspberry_Pi_Robot_With_Eyes.jpg)

You can also [purchase an SD Card with the software on it here](https://www.dexterindustries.com/shop/sd-card-raspbian-wheezy-image-for-raspberry-pi/).  

# Installation
You can install the GoPiGo3 on your own operating system with the following commands in the command line:
1. Clone this repository onto the Raspberry Pi: 

        `sudo git clone http://www.github.com/DexterInd/GoPiGo3.git /home/pi/Dexter/GoPiGo3`
2. Run the install script: `sudo bash /home/pi/Dexter/GoPiGo3/Install/install.sh`
3. Reboot the Raspberry Pi to make the settings take effect: `sudo reboot`

## Install/Update Node.js
This library supports Node.js 8.x version, we provide a couple of bash scripts to install/uninstall the proper Node.js version.
To install NVM (Node Version Manager), Node.js and NPM:
1. Run the install script: `bash /home/pi/Dexter/GoPiGo3/Software/NodeJS/install.sh`
2. Follow the instructions

To uninstall NVM, Node.js and NPM:
1. Run the install script: `bash /home/pi/Dexter/GoPiGo3/Software/NodeJS/uninstall.sh`
2. Follow the instructions

# Use in your application
This library is published as a [NPM package](https://www.npmjs.com/package/node-gopigo3).
1. Install the package in your project by typing the following command in your project's folder:
        `npm install node-gopigo3 --save`
2. Include the package in your application:
        `const EasyGopigo3 = require('node-gopigo3').EasyGopigo3` or `const Gopigo3 = require('node-gopigo3').Gopigo3`

# How your application may look like
```javascript
const EasyGopigo3 = require('node-gopigo3').EasyGopigo3;

const easyGoPiGo3 = new EasyGopigo3();
const myLed = easyGoPiGo3.initLed('AD1');

// Turn on the led
myLed.lightOn(30);

// Turn off the led
myLed.lightOff();
```

For any initial hint please check the "examples" folder. Feel free to use the forum for any extra help.

# License

Please review the [LICENSE.md] file for license information.

[LICENSE.md]: ./LICENSE.md

# See Also

- [Dexter Industries](http://www.dexterindustries.com/GoPiGo)
- [Dexter Industries Forum Support](http://forum.dexterindustries.com/c/gopigo)

Notes for developers
=======

# Features
* Build with [Babel](https://babeljs.io). (ES6 -> ES5)
* Test with [mocha](https://mochajs.org).
* Cover with [istanbul](https://github.com/gotwarlost/istanbul).
* Check with [eslint](eslint.org).
* Deploy with [Travis](travis-ci.org).

# Commands
- `npm run clean` - Remove `lib/` directory
- `npm test` - Run tests. Tests can be written with ES6 (WOW!)
- `npm test:watch` - You can even re-run tests on file changes!
- `npm run cover` - Yes. You can even cover ES6 code.
- `npm run lint` - We recommend using [airbnb-config](https://github.com/airbnb/javascript/tree/master/packages/eslint-config-airbnb). It's fantastic.
- `npm run test:examples` - We recommend writing examples on pure JS for better understanding module usage.
- `npm run build` - Do some magic with ES6 to create ES5 code.