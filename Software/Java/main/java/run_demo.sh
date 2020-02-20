#!/bin/bash
sudo javac -classpath .:classes:/opt/pi4j/lib/'*':/opt/java-json/'*' -d . com/dexterindustries/DemoEasyGoPiGo3.java
sudo java -classpath .:classes:/opt/pi4j/lib/'*':/opt/java-json/'*' com/dexterindustries/DemoEasyGoPiGo3

