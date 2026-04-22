#!/usr/bin/env python
# import the time library for the sleep function
import time

# import the GoPiGo3 drivers
import easygopigo3 as easy

# Create an instance of the GoPiGo3 class.
# GPG will be the GoPiGo3 object.
gpg = easy.EasyGoPiGo3()

# Twinkle Twinkle Little Star
# Each entry is (note, duration) where duration is in beats (quarter note = 1)
SONG = [
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
    ("A4", 1), ("A4", 1), ("G4", 2),
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
    ("D4", 1), ("D4", 1), ("C4", 2),
    ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
    ("E4", 1), ("E4", 1), ("D4", 2),
    ("G4", 1), ("G4", 1), ("F4", 1), ("F4", 1),
    ("E4", 1), ("E4", 1), ("D4", 2),
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1),
    ("A4", 1), ("A4", 1), ("G4", 2),
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1),
    ("D4", 1), ("D4", 1), ("C4", 2),
]

BEAT = 0.4  # seconds per quarter note

try:
    # connect a buzzer to port AD2
    my_buzzer = gpg.init_buzzer("AD2")

    print("Expecting a buzzer on Port AD2")
    print("Playing Twinkle Twinkle Little Star")

    for note, beats in SONG:
        print(note)
        my_buzzer.sound(my_buzzer.scale[note])
        time.sleep(BEAT * beats * 0.9)   # note on
        my_buzzer.sound_off()
        time.sleep(BEAT * beats * 0.1)   # brief gap between notes

    my_buzzer.sound_off()

except KeyboardInterrupt:
    gpg.reset_all()
