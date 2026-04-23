#!/usr/bin/env python
#
# GoPiGo3 Buzzer example - Jamaican Reggae Beat
#
# Plays a reggae-inspired riddim on a Grove buzzer connected to port AD2.
# The pattern uses the A minor pentatonic scale with the classic reggae
# "one drop" feel: bass on beat 1, skank stabs on the offbeats of 2 & 4,
# and a short melodic fill at the end of each 2-bar phrase.
#
# Connect a Grove buzzer to port AD2 of the GoPiGo3.

import time
import easygopigo3 as easy

gpg = easy.EasyGoPiGo3()

BPM  = 80          # relaxed reggae tempo
BEAT = 60.0 / BPM  # seconds per quarter note

# Each entry: (note, beats)  -- note=None means a rest
# A minor pentatonic: A3 C4 D4 E4 G4 A4
#
# Structure (repeating 2-bar loop):
#   Bar 1 — bass on 1 & 3, skank stabs on the + of 2 and 4
#   Bar 2 — same groove with a melodic fill on beat 4
LOOP = [
    # --- bar 1 ---
    ("A3",  0.50), (None, 0.25), ("A3",  0.25),   # beat 1 (bass drop)
    (None,  0.50), ("C4",  0.25), (None, 0.25),   # beat 2 skank (+ of 2)
    ("B3",  0.50), (None, 0.25), ("B3",  0.25),   # beat 3 (bass)
    (None,  0.50), ("D4",  0.25), (None, 0.25),   # beat 4 skank (+ of 4)

    # --- bar 2 ---
    ("A3",  0.50), (None, 0.25), ("A3",  0.25),   # beat 1 (bass drop)
    (None,  0.50), ("C4",  0.25), (None, 0.25),   # beat 2 skank
    ("B3",  0.50), (None, 0.25), ("B3",  0.25),   # beat 3 (bass)
    ("E4",  0.25), ("D4", 0.25), ("C4",  0.25), ("A3", 0.25),  # melodic fill
]

def play_note(buzzer, note, beats):
    duration = BEAT * beats
    if note is None:
        time.sleep(duration)
    else:
        buzzer.sound(buzzer.scale[note])
        time.sleep(duration * 0.85)   # note on
        buzzer.sound_off()
        time.sleep(duration * 0.15)   # articulation gap

try:
    my_buzzer = gpg.init_buzzer("AD2")

    print("Playing Jamaican reggae beat on Port AD2  (Ctrl-C to stop)")

    while True:
        for note, beats in LOOP:
            play_note(my_buzzer, note, beats)

except KeyboardInterrupt:
    gpg.reset_all()
