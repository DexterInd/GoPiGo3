# Compile C++ programs for GoPiGo3

1) mkdir for the cpp stuff:  

```
  mkdir  <path>/GoPiGo3_Software_C
  mkdir  <path>/GoPiGo3_Software_C/bin
```

2) copy the Dexter cpp examples:  

```
  cp -r ~/GoPiGo3/Software/C/* <path>/GoPiGo3_Software_C
```

3) install cmake:  

```
  sudo apt-get install cmake
```
4) run cmake to build make files (or ./build_all.sh)  

```
  cd <path>/GoPiGo3_Software_C
  cmake CMakeLists.txt
```

5) run make to build the examples and the libgopigo3.so link library  

```
  make
```

6) try out the info executable:  

```
   bin/info
```

7) If it works, try out the other executables 
```
bin/info          Read GoPiGo3 Board Info  
bin/vbatt         Read the GoPiGo3 battery voltage  
bin/leds          Flash GoPiGo3 red LEDs  
bin/drive         Use keyboard to drive your GoPiGo3  
bin/servos        Rotate servos through range  
bin/grove_led     Blink Grove LED  
bin/sensors       Use Grove Ultrasonic and IR Receiver  
bin/i2c           Drive PCA9570 I2C Expander  
bin/motors        Gently spin left wheel forward,
                    watch encoder values, right wheel turn
```

8) Clean the folder of all build products and binaries  

```
   ./clean.sh
```


==============  

NOTE:  Individual Examples can be built in the Examples folder with:

```
g++ -o motors motors.cpp ../GoPiGo3.cpp -I..
```

The executable will be in the Examples folder.  

