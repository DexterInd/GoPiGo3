# GoPiGo3 Python package
from .gopigo3 import GoPiGo3, FirmwareVersionError, GoPiGoValueError
from .easygopigo3 import EasyGoPiGo3
from .easysensors import (
    Sensor,
    DigitalSensor,
    AnalogSensor,
    LightSensor,
    SoundSensor,
    LoudnessSensor,
    UltraSonicSensor,
    Buzzer,
    Led,
    MotionSensor,
    ButtonSensor,
    Remote,
    Servo,
    DHTSensor,
)

__version__ = "0.0.11"
__all__ = [
    "GoPiGo3",
    "FirmwareVersionError",
    "GoPiGoValueError",
    "EasyGoPiGo3",
    "Sensor",
    "DigitalSensor",
    "AnalogSensor",
    "LightSensor",
    "SoundSensor",
    "LoudnessSensor",
    "UltraSonicSensor",
    "Buzzer",
    "Led",
    "MotionSensor",
    "ButtonSensor",
    "Remote",
    "Servo",
    "DHTSensor",
]
