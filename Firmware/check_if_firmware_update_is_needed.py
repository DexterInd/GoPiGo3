import gopigo3
import os

list_files = os.listdir('/home/pi/Dexter/GoPiGo3/Firmware')
for onefile in list_files:
#     print (F"{onefile}: { onefile.find('GoPiGo3_Firmware_')}")
    if onefile.find("GoPiGo3_Firmware_") == 0:
        available_firmware = onefile[len("GoPiGo3_Firmware_"):-4]
        break

try:
        g = gopigo3.GoPiGo3()
        current_firmware = g.get_version_firmware()
        if current_firmware == available_firmware:
                print(f"\nThe GoPiGo is already running the latest firmare: {current_firmware}. \nAn upgrade is not needed at this time.\n")
                exit(1)
except Exception as e:
        print(e)
        print("Firmware upgrade is needed")
        exit(0)