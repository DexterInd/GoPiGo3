# C++ programs for GoPiGo3

The C++ GoPiGo3 API is defined by the files:  

```
GoPiGo3.h
GoPiGo3.cpp
```

and libgopigo3.so is the built link library for the API.  

Examples/ contains C++ programs that use the C++ GoPiGo3 API:  

```
info          Read GoPiGo3 Board Info  
vbatt         Read the GoPiGo3 battery voltage  
leds          Flash GoPiGo3 red LEDs  
drive         Use keyboard to drive your GoPiGo3  
servos        Rotate servos through range  
grove_led     Blink Grove LED  
sensors       Use Grove Ultrasonic and IR Receiver  
i2c           Drive PCA9570 I2C Expander  
motors        Gently spin left wheel forward,
                    watch encoder values, right wheel turn
```



### To build

1) install cmake:  

```
  sudo apt-get install cmake
```
2) run cmake to build make files  

```
  cmake CMakeLists.txt
```

5) run make to build the examples and the libgopigo3.so link library  

```
  make
```

6) try out the info executable:  

```
   ./info
```

7) Try out the other executables 


NOTE:  To clean the folder of all build products and binaries  

```
   ./clean.sh
```


==============  

NOTE:  To try your hand with the C++ GoPiGo3 API:

```
mkdir test
cd test
(create myrobot.cpp, and reference the the API with #include GoPiGo3.h)
g++ -o myrobot myrobot.cpp ../GoPiGo3.cpp -I..
./myrobot
```

The executable will be in the same folder as your C++ program (test/).  

