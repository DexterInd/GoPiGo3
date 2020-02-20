#!/bin/bash
curl -ssl https://pi4j.com/install | sudo bash
sudo mkdir /opt/java-json
wget https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/json-simple/json-simple-1.1.1.jar
sudo mv json-simple-1.1.1.jar /opt/java-json
javac -classpath .:classes:/opt/pi4j/lib/'*' -d . com/dexterindustries/gopigo3driver/constants/*.java
javac -classpath .:classes:/opt/pi4j/lib/'*':/opt/java-json/'*' -d . com/dexterindustries/gopigo3driver/*.java