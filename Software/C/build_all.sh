#!/bin/bash

cmake CMakeLists.txt
make

echo -e "Binary executables in bin/ folder"
ls -1 bin
