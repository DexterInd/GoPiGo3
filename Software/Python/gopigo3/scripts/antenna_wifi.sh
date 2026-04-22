#!/bin/bash
# Detect if we have a Wifi connection and reflect it on the GoPiGo3 antenna LED.
#   Connected    → dim white (R=3, G=1, B=3)
#   Disconnected → dim red   (R=1, G=0, B=0)

if iwgetid --scheme > /dev/null 2>&1; then
    python3 -c "import gopigo3; GPG=gopigo3.GoPiGo3(); GPG.set_led(GPG.LED_WIFI,3,1,3)"
else
    python3 -c "import gopigo3; GPG=gopigo3.GoPiGo3(); GPG.set_led(GPG.LED_WIFI,1,0,0)"
fi
