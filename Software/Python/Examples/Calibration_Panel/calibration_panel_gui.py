import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont
import easygopigo3 as easy
import subprocess


# Global GPG 
try:
    gpg = easy.EasyGoPiGo3()
except Exception as e:
    print("GoPiGo3 cannot be instanstiated. Most likely wrong firmware version")
    print(e)
    exit()

# in case the window is killed by the end user, let's make sure the robot is stopped
import atexit
atexit.register(gpg.stop)


ticks = gpg.ENCODER_TICKS_PER_ROTATION
messages=["Did it achieve the distance?", 
          "If the robot is off by approximately half or double the distance,\nclick 'Retry' to do a second attempt", 
          "Otherwise click 'Fine Tune' to go to fine tuning."]

# detect if we are in the first phase where we have to determine the number of ticks, or if we're passed that
fine_tuning = False
retried = False


# Disable all main frames
def enable(children):
   for child in children:
      child.configure(state='normal')

# Enable all main frames
def enable_all():
    enable(main_window.wheel_diameter_frame.winfo_children())
    enable(main_window.distance_between_wheels_frame.winfo_children())
    enable(main_window.bottom_frame.winfo_children())

# Disable all children of a frame
def disable(children):
   for child in children:
      child.configure(state='disable')

# enable all children of a frame
def disable_all():
    disable(main_window.wheel_diameter_frame.winfo_children())
    disable(main_window.distance_between_wheels_frame.winfo_children())
    disable(main_window.bottom_frame.winfo_children())


# Callback for the emergency stop button
def emergency():
    gpg.stop()

    # if the popup is up, kill it
    try:
        popup.destroy()
    except:
        pass
    enable_all()

def finetune():
    '''
    Go into fine tuning mode.  This means we have accepted the number of ticks 
    and won't bring the popup window any more
    '''
    global fine_tuning
    fine_tuning = True
    main_window.wheel_top_label.config(text="Second Step: Fine Tune the Distance")
    popup.destroy()
    enable_all()

def retry():
    '''
    The user has signaled that the robot is completely off track.
    Switch to the other number of ticks and try again.
    Since we only support 6 or 16, if we fall into this method for a second time,
    then the user has to contact customer service.
    '''
    global ticks, process, command, retried

    if not retried:
        if ticks == 6:
            newticks = 16
        elif ticks == 16:
            newticks = 6
        command = command.replace(f"{ticks}, ", f"{newticks}, ")
        ticks = newticks
        retried = True
        process = subprocess.Popen(['python', '-c', command], stdout=subprocess.PIPE)
    else:
        # User has attempted both configurations
        popup.destroy()
        enable_all()
        messagebox.showwarning("Customer Service","Please contact Customer Service: support@modrobotics.com")



def save():
    '''
    Save the new constants
    '''
    diam, base, ticks = get_values()
    if diam > 0 and base > 0 and ticks > 0:
        gpg.set_robot_constants(diam, base, ticks, gpg.MOTOR_GEAR_RATIO)
        gpg.save_robot_constants()
    

def exit_app():
    exit()


def save_exit_app():
    save()
    exit()


def get_values():
    '''
    Read the values from the various input fields.
    Ticks is no longer being read, so it's kind off a moot point
    '''

    try:
        diam = float(main_window.wheel_diameter_variable.get())
        # print(diam)
    except Exception as e:
        # print("Wheel diameter is invalid.")
        print(e)
        return (0,0,0)

    try:
        base = float(main_window.distance_between_wheels_variable.get())
        # print(base)
    except:
        # print("The distance between wheels is invalid.")
        return (0,0,0)

    return(diam, base, ticks)

def drive_6_feet():
    '''
    Get values from the input fields, and drive 6 feet with those values
    Use a subprocess so the main event loop isn't blocked, and also the emergency stop can work.
    '''
    global process, command

    diam, base, ticks = get_values()

    if diam==0 or base==0 or ticks==0:
        return

    try:
        command = f"import easygopigo3 as e; g = e.EasyGoPiGo3(); g.set_robot_constants({diam}, {base}, {ticks}, {gpg.MOTOR_GEAR_RATIO});g.drive_inches(6*12)"
        process = subprocess.Popen(['python', '-c', command], stdout=subprocess.PIPE)
        if not fine_tuning:
            answer = messageWindow(title="Driving forward", messages=messages)
    except Exception as e:
        print(e)


def drive_2m():
    '''
    Get values from the input fields, and drive 2m with those values
    Use a subprocess so the main event loop isn't blocked, and also the emergency stop can work.
    '''
    global process, command

    diam, base, ticks = get_values()

    if diam==0 or base==0 or ticks==0:
        return

    try:
        command = f"import easygopigo3 as e; g = e.EasyGoPiGo3(); g.set_robot_constants({diam}, {base}, {ticks}, {gpg.MOTOR_GEAR_RATIO});g.drive_cm(200)"
        process = subprocess.Popen(['python', '-c', command], stdout=subprocess.PIPE)
        if not fine_tuning:
            answer = messageWindow(title="Driving forward", messages=messages)
    except Exception as e:
        print(e)
        pass


def spin1():
    '''
    Get values from the input fields, and attempt a single full spin with those values
    Use a subprocess so the main event loop isn't blocked, and also the emergency stop can work.
    '''
    global process
    diam, base, ticks = get_values()

    if diam==0 or base==0 or ticks==0:
        return

    try:
        command = f"import easygopigo3 as e; g = e.EasyGoPiGo3(); g.set_robot_constants({diam}, {base}, {ticks}, {gpg.MOTOR_GEAR_RATIO});g.turn_degrees(360)"
        process = subprocess.Popen(['python', '-c', command], stdout=subprocess.PIPE)
    except Exception as e:
        print(e)
        pass


def messageWindow(title, messages):
    '''
    Popup window which should be called just once.
    '''
    global popup
    popup = tk.Toplevel()
    popup.title(title)
    popup.configure( background="white")
    popup.geometry("+{}+{}".format(positionRight, positionDown))

    top_frame = tk.Frame(master=popup, width=400, height=50, padx=5, pady=5, background="white")
    top_frame.pack()
    first_message = True
    for message in messages:
        if first_message:
            first_message = False
            tk.Label(top_frame, anchor='w', text=message, background="#447267", foreground="#FFFFFF").pack(padx=5, pady=5)
        else:
            tk.Label(top_frame, anchor='w', text=message, background="white").pack(padx=5, pady=5)

    buttons = tk.Frame(master=popup, padx=5, pady=5, background="white")
    buttons.pack()


    tk.Button(buttons, text='Retry', width="18", command=retry, background="#66AFA0", foreground="#FFFFFF").pack(side="left", padx=20, fill="x")
    tk.Button(buttons, text='Fine Tune', width="18", command=finetune, background="#66AFA0", foreground="#FFFFFF").pack(side="left", padx=20, fill="x")
    tk.Button(buttons, text='Emergency Stop & Close', width="18", command=emergency, background="#8A2F43", foreground="#FFFFFF").pack(side="left", padx=20, fill="x")
    disable_all()


class main(object):
    '''
    Main dialog window
    '''
    global left_ticks_variable, right_ticks_variable, wheel_diameter_variable, distance_between_wheels_variable, spin_disk_button_variable
    global wheel_diameter_frame, distance_between_wheels_frame, bottom_frame

    def __init__(self,master):
        self.master=master
        self.fontStyle = tkFont.Font(family="Lucida Grande", size=20)
        self.fontStyle2 = tkFont.Font(family="Lucida Grande", size=15)

        self.top_frame = tk.Frame(master=root, width=400, height=50, padx=5, pady=5, background="#447267")
        self.top_frame.pack(fill=tk.BOTH, expand=True)

        self.main_frame = tk.Frame(master=root, width=150, height=150, padx=5, pady=5, background="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.explanation_frame = tk.Frame(master=self.main_frame, bd=5, background="white")
        self.explanation_frame.pack(fill=tk.BOTH, expand=True)
        self.explanation_frame1 = tk.Frame(master=self.main_frame, bd=5, background="white")
        self.explanation_frame1.pack(fill=tk.BOTH, expand=True)

        self.wheel_diameter_frame = tk.Frame(master=self.main_frame, background="white")
        self.wheel_diameter_frame.pack(fill=tk.BOTH, expand=True)

        self.spacer_frame = tk.Frame(master=self.main_frame, height=35, background="white")
        self.spacer_frame.pack(fill=tk.BOTH, expand=True)

        self.explanation_frame2 = tk.Frame(master=self.main_frame, background="white")
        self.explanation_frame2.pack(fill=tk.BOTH, expand=True)

        self.distance_between_wheels_frame = tk.Frame(master=self.main_frame, background="white")
        self.distance_between_wheels_frame.pack(fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(master=self.master, width=25, height=25, padx=5, pady=5, background="white")
        self.bottom_frame.pack(fill=tk.BOTH, expand=True)

        # Top Frame
        self.title_label = tk.Label(master=self.top_frame, text="Calibrate your GoPiGo3", font=self.fontStyle, background="#447267", foreground="#FFFFFF")
        self.title_label.pack(padx=5, pady=5)

        # Main Frame

        # Explanation Frame
        self.wheel_top_label = tk.Label(master=self.explanation_frame, text="First Step: Adjusting the distance:", font=self.fontStyle2, anchor="w", background='white')
        self.wheel_top_explanation1 = tk.Label(master=self.explanation_frame1, text="Press either 'Drive 6 feet' or 'Drive 2m' to have the robot go that distance.", background='white')
        self.wheel_top_explanation2 = tk.Label(master=self.explanation_frame1, text="You can adjust the wheel diameter value until you are satisfied with the precision.", background='white')
        self.wheel_top_explanation3 = tk.Label(master=self.explanation_frame1, text="You can then move on to adjust turning. ",background='white')
        
        self.wheel_top_label.pack(padx=5, pady=10, side="left")
        self.wheel_top_explanation1.pack(padx=5, pady=1, anchor='w')
        self.wheel_top_explanation2.pack(padx=5, pady=1, anchor='w')
        self.wheel_top_explanation3.pack(padx=5, pady=1, anchor='w')

        # wheel_diameter_frame

        self.wheel_diameter_variable = tk.StringVar(master=self.wheel_diameter_frame, value=gpg.WHEEL_DIAMETER)
        self.wheel_diameter_label = tk.Label(master=self.wheel_diameter_frame, text="with wheel diameter set to", background='white')
        self.wheel_diameter_entry = tk.Entry(master=self.wheel_diameter_frame,  textvariable=self.wheel_diameter_variable, width=6)
        self.wheel_diameter_mm_label = tk.Label(master=self.wheel_diameter_frame, text="mm", background='white')
        self.drive_6_feet_button = tk.Button(master=self.wheel_diameter_frame, text="Drive 6 feet", command = drive_6_feet, background="#66AFA0")
        self.wheel_diameter_or_label = tk.Label(master=self.wheel_diameter_frame, text="or", background='white')
        self.drive_2m_button = tk.Button(master=self.wheel_diameter_frame, text="Drive 2m", command = drive_2m, background="#66AFA0")
        self.drive_6_feet_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.wheel_diameter_or_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.drive_2m_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.wheel_diameter_label.pack(padx=5, pady=5, side = "left")
        self.wheel_diameter_entry.pack(padx=5, pady=5, side = "left")
        self.wheel_diameter_mm_label.pack(padx=5, pady=5, side = "left")


        # distance_between_wheels_frame
        self.distance_between_wheels_top_label = tk.Label(master=self.explanation_frame2, text="Last Step: Fine Tune Turns:", anchor="nw", background='white')

        self.spin_one_button = tk.Button(master=self.distance_between_wheels_frame, text="Spin 1 Rotation", command = spin1, background="#66AFA0")
        self.distance_between_wheels_label = tk.Label(master=self.distance_between_wheels_frame, text="with a distance between the wheels of", background='white')
        self.distance_between_wheels_variable = tk.StringVar(master=self.distance_between_wheels_frame, value=gpg.WHEEL_BASE_WIDTH)
        self.distance_between_wheels_entry = tk.Entry(master=self.distance_between_wheels_frame, textvariable=self.distance_between_wheels_variable, width=6)
        self.distance_between_wheels_mm_label = tk.Label(master=self.distance_between_wheels_frame, text="mm", background='white')
        
        self.distance_between_wheels_top_label.pack(padx=5, pady=10, side = "left")
        self.spin_one_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.distance_between_wheels_label.pack(padx=5, pady=5, side = "left")
        self.distance_between_wheels_entry.pack(padx=5, pady=5, side = "left")
        self.distance_between_wheels_mm_label.pack(padx=5, pady=5, side = "left")

        # bottom_frame
        self.emergency_button = tk.Button(master=self.bottom_frame, text="Emergency Stop", command = emergency, background="#8A2F43", foreground="#FFFFFF", height=2)
        self.save_button = tk.Button(master=self.bottom_frame, text="Save", command = save, background="#447267", foreground="#FFFFFF")
        self.save_exit_button = tk.Button(master=self.bottom_frame,text="Save and Exit", command = save_exit_app, background="#447267", foreground="#FFFFFF")
        self.exit_button = tk.Button(master=self.bottom_frame,text="Exit", command = exit_app, background="#333333", foreground="#FFFFFF")

        self.emergency_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.save_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.save_exit_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")
        self.exit_button.pack(fill=tk.BOTH, expand=True, padx=5, pady=5, side = "left")



try:
    gpg = easy.EasyGoPiGo3()
except Exception as e:
    print("GoPiGo3 cannot be instanstiated. Most likely wrong firmware version")
    print(e)

root = tk.Tk()

# Gets the requested values of the height and width.
windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()
 
# Gets both half the screen width/height and root width/height
positionRight = int(root.winfo_screenwidth()/3 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/3 - windowHeight/2)
 
# Positions the root in the center of the page.
root.geometry("+{}+{}".format(positionRight, positionDown))
root.configure(background='white')
root.title("Calibration")

# root.eval('tk::PlaceWindow . center')
main_window = main(root)
root.mainloop()
