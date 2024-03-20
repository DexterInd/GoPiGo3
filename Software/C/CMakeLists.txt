cmake_minimum_required(VERSION 3.0)
project(gopigo3_cpp)

### Build

include_directories(.)

## GoPiGo3 library
add_library(gopigo3 SHARED GoPiGo3.cpp)

## Examples

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

# drive
add_executable(drive Examples/drive.cpp)
target_link_libraries(drive gopigo3)

# servo example
add_executable(servos Examples/servos.cpp)
target_link_libraries(servos gopigo3)

# vbatt example
add_executable(vbatt Examples/vbatt.cpp)
target_link_libraries(vbatt gopigo3)

### Installation

install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/
  DESTINATION include
  FILES_MATCHING PATTERN "*.h"
  PATTERN "Examples" EXCLUDE
)

install(TARGETS gopigo3 EXPORT gopigo3Targets
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
  INCLUDES DESTINATION include
)

### Export CMake configuration

set_property(TARGET gopigo3 APPEND PROPERTY INTERFACE_INCLUDE_DIRECTORIES
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/>
  $<INSTALL_INTERFACE:${CMAKE_INSTALL_PREFIX}/include/>
)

set(CONF_INCLUDE_DIRS ${CMAKE_INSTALL_PREFIX}/include/)

export(EXPORT gopigo3Targets
  FILE "${PROJECT_BINARY_DIR}/gopigo3_cppTargets.cmake")

configure_file(gopigo3_cppConfig.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/gopigo3_cppConfig.cmake" @ONLY)

install(FILES
  "${CMAKE_CURRENT_BINARY_DIR}/gopigo3_cppConfig.cmake"
  DESTINATION share/gopigo3_cpp/cmake)

install(EXPORT gopigo3Targets
  FILE gopigo3_cppTargets.cmake
  DESTINATION share/gopigo3_cpp/cmake
)
