cmake_minimum_required(VERSION 2.8.3)
project(gopigo3_cpp)

include_directories(.)

### GoPiGo3 library
add_library(gopigo3 SHARED GoPiGo3.cpp)

### Examples

# grove_led
add_executable(grove_led Examples/grove_led.cpp)
target_link_libraries(grove_led gopigo3)

# i2c
add_executable(i2c Examples/i2c.cpp)
target_link_libraries(i2c gopigo3)

# info
add_executable(info Examples/info.cpp)
target_link_libraries(info gopigo3)

# leds
add_executable(leds Examples/leds.cpp)
target_link_libraries(leds gopigo3)

# motors
add_executable(motors Examples/motors.cpp)
target_link_libraries(motors gopigo3)

# sensors
add_executable(sensors Examples/sensors.cpp)
target_link_libraries(sensors gopigo3)
