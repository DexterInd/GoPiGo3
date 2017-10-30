####################################################
# This file tests the mutex class
# Run it in parallel with text_heavy_mutext_2.py
# in order to verify that mutex is functional.
# This one acquires and releases every half second
# the other one is every 5 seconds
####################################################
import time
from I2C_mutex import Mutex
import fcntl

mutex = Mutex(debug=True)

DexterLockI2C_handle = open('/run/lock/DexterLockI2C')

while True:
    try:
        mutex.acquire()
        time.sleep(0.5)
        mutex.release()
    except KeyboardInterrupt:
        mutex.release()
        exit(0)
    except Exception as e:
        print(e)
