#!/bin/bash

# FILE:  clean.sh

# Use to fully clean out all cmake and make products (restore to original contents)

echo -e "Removing all built executables"
make clean
echo -e "Removing all cmake generated files"
rm CMakeCache.txt
rm -rf CMakeFiles
rm *.cmake
rm Makefile
echo -e "See README.txt for build instructions"


