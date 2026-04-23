#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox
import os
import atexit

# try to import the auto_detection library
try:
    import auto_detect_robot
    no_auto_detect = False
except Exception:
    no_auto_detect = True

import easygopigo3 as easy
try:
    gpg = easy.EasyGoPiGo3()
except Exception as e:
    print("GoPiGo3 cannot be instantiated. Most likely wrong firmware version")
    print(e)
    _root = tk.Tk()
    _root.withdraw()
    messagebox.showerror(
        'GoPiGo3 not found',
        'GoPiGo3 cannot be found. It may need a firmware update.\n\n'
        'You can upgrade the firmware by running DI Software Update then updating your robot.'
    )
    raise SystemExit(1)

atexit.register(gpg.stop)

left_led = 0
right_led = 0
left_eye = 0
right_eye = 0

v = gpg.volt()
firmware_version = gpg.get_version_firmware()
try:
    library_version = easy.__version__
except AttributeError:
    library_version = ""
ticks = gpg.ENCODER_TICKS_PER_ROTATION
serial = gpg.get_id()

ICON_PATH = os.path.dirname(os.path.abspath(__file__))


class ControlPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GoPiGo3 Control Panel")
        self.resizable(False, False)
        self.configure(bg="white")

        try:
            icon = tk.PhotoImage(file=os.path.join(ICON_PATH, "GoPiGo3.png"))
            self.iconphoto(True, icon)
        except Exception:
            pass

        # --- Auto-detect warning ---
        if not no_auto_detect:
            detected = auto_detect_robot.autodetect()
            print(detected)
            if detected != "GoPiGo3":
                tk.Label(self, text="Warning: Could not find a GoPiGo3",
                         fg="red", bg="white",
                         font=("", 10, "bold")).pack(pady=(8, 0))

        # --- Remote Control ---
        tk.Label(self, text="Remote Control:", bg="white",
                 font=("", 15, "bold")).pack(anchor="w", padx=30, pady=(10, 0))

        blinker_frame = tk.Frame(self, bg="white")
        blinker_frame.pack(padx=30, pady=4)
        tk.Button(blinker_frame, text="Left Blinker", width=12,
                  command=self.toggle_left_led).pack(side="left", padx=20, pady=9)
        tk.Button(blinker_frame, text="Right Blinker", width=12,
                  command=self.toggle_right_led).pack(side="left", padx=20, pady=9)

        eyes_frame = tk.Frame(self, bg="white")
        eyes_frame.pack(padx=30, pady=4)
        tk.Button(eyes_frame, text="Left Eye", width=10,
                  command=self.toggle_left_eye).pack(side="left", padx=4)
        try:
            dex_img = tk.PhotoImage(file=os.path.join(ICON_PATH, "dex.png"))
            # Scale down to ~80px wide if the image is larger
            scale = max(1, dex_img.width() // 80)
            if scale > 1:
                dex_img = dex_img.subsample(scale, scale)
            dex_label = tk.Label(eyes_frame, image=dex_img, bg="white")
            dex_label.image = dex_img   # keep reference
            dex_label.pack(side="left", padx=8)
        except Exception:
            tk.Label(eyes_frame, text="[dex]", bg="white").pack(side="left", padx=8)
        tk.Button(eyes_frame, text="Right Eye", width=10,
                  command=self.toggle_right_eye).pack(side="left", padx=4)

        fwd_frame = tk.Frame(self, bg="white")
        fwd_frame.pack(pady=(8, 0))
        tk.Button(fwd_frame, text="Forward", width=10,
                  command=gpg.forward).pack()

        dir_frame = tk.Frame(self, bg="white")
        dir_frame.pack()
        tk.Button(dir_frame, text="Left", width=8,
                  command=gpg.left).pack(side="left", padx=2)
        tk.Button(dir_frame, text="Stop", width=8, fg="red",
                  command=gpg.stop).pack(side="left", padx=2)
        tk.Button(dir_frame, text="Right", width=8,
                  command=gpg.right).pack(side="left", padx=2)

        bwd_frame = tk.Frame(self, bg="white")
        bwd_frame.pack(pady=(0, 8))
        tk.Button(bwd_frame, text="Back", width=10,
                  command=gpg.backward).pack()

        # --- Vital Signs ---
        tk.Label(self, text="Vital Signs:", bg="white",
                 font=("", 15, "bold")).pack(anchor="w", padx=30, pady=(10, 0))

        battery_frame = tk.Frame(self, bg="white")
        battery_frame.pack(anchor="w", padx=30, pady=(9, 2))
        tk.Button(battery_frame, text="Check Battery Voltage",
                  command=self.check_battery).pack(side="left")
        self.battery_label = tk.Label(battery_frame,
                                      text=f"{round(v, 1)}V",
                                      bg="white", font=("", 10, "bold"))
        self.battery_label.pack(side="left", padx=10)

        tk.Label(self, text=f"Firmware Version: {firmware_version}",
                 bg="white").pack(anchor="w", padx=30, pady=2)
        tk.Label(self, text=f"Serial Number: {serial}",
                 bg="white").pack(anchor="w", padx=30, pady=2)
        tk.Label(self, text=f"Ticks per Motor: {ticks}",
                 bg="white").pack(anchor="w", padx=30, pady=2)
        if library_version:
            tk.Label(self, text=f"Driver Version: {library_version}",
                     bg="white").pack(anchor="w", padx=30, pady=2)

        # --- Exit ---
        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(bottom_frame, text="", bg="white", width=40).pack(side="left", expand=True, fill="x")
        tk.Button(bottom_frame, text="Exit", command=self.destroy).pack(side="right", padx=10)

    def toggle_left_led(self):
        global left_led
        if left_led == 0:
            gpg.led_on(1)
            left_led = 1
        else:
            gpg.led_off(1)
            left_led = 0

    def toggle_right_led(self):
        global right_led
        if right_led == 0:
            gpg.led_on(0)
            right_led = 1
        else:
            gpg.led_off(0)
            right_led = 0

    def toggle_left_eye(self):
        global left_eye
        if left_eye == 0:
            gpg.open_left_eye()
            left_eye = 1
        else:
            gpg.close_left_eye()
            left_eye = 0

    def toggle_right_eye(self):
        global right_eye
        if right_eye == 0:
            gpg.open_right_eye()
            right_eye = 1
        else:
            gpg.close_right_eye()
            right_eye = 0

    def check_battery(self):
        self.battery_label.config(text=f"{round(gpg.volt(), 1)}V")


if __name__ == "__main__":
    app = ControlPanel()
    app.mainloop()
