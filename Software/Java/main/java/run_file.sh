#!/bin/bash
javac -classpath .:classes:/opt/pi4j/lib/'*':/opt/java-json/'*':/home/pi/Dexter/GoPiGo3/Software/Java_new/main/java -d . $1.java
java -classpath .:classes:/opt/pi4j/lib/'*':/opt/java-json/'*':/home/pi/Dexter/GoPiGo3/Software/Java_new/main/java $1

