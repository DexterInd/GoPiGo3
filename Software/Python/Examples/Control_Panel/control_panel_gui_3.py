#!/usr/bin/python

from __future__ import print_function

# try to import the auto_detection library
try:
    import auto_detect_robot
    no_auto_detect = False
except:
    no_auto_detect = True

import gopigo3
import easygopigo3 as easy
gpg = easy.EasyGoPiGo3()

try:
    import wx
except ImportError:
    raise ImportError("The wxPython module is required to run this program")

import atexit
atexit.register(gpg.stop)    

left_led=0
right_led=0
left_eye=0
right_eye=0
# trim_val=gopigo.trim_read()
v=gpg.volt()
f=gpg.get_version_firmware()
# slider_val=gopigo.trim_read()

class gopigo_control_app(wx.Frame):
    slider=0
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self,parent,id,title,size=(475,600))
        self.parent = parent
        self.initialize()
        # Exit
        exit_button = wx.Button(self, label="Exit", pos=(240+75,500))
        exit_button.Bind(wx.EVT_BUTTON, self.onClose)
    
    #----------------------------------------------------------------------
    def OnEraseBackground(self, evt):
        """
        Add a picture to the background
        """
        # yanked from ColourDB.py
        dc = evt.GetDC()
 
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()	
        # bmp = wx.Bitmap("/home/pi/Desktop/GoBox/Troubleshooting_GUI/dex.png")	# Draw the photograph.
        # dc.DrawBitmap(bmp, 0, 400)						# Absolute position of where to put the picture


    def initialize(self):
        sizer = wx.GridBagSizer()

        x=75
        y=175 
        dist=60

        # if we can auto-detect, then give feedback to the user
        if no_auto_detect == False:
            detected_robot = auto_detect_robot.autodetect()
            if detected_robot != "GoPiGo3":
                detected_robot_str = wx.StaticText(self,-1,
                    label="Warning: Could not find a GoPiGo3",pos=(x-30+dist*2,4))
                detected_robot_str.SetForegroundColour('red')
                sizer.AddStretchSpacer((0,0))
                sizer.Add(detected_robot_str,(0,1))
                sizer.AddStretchSpacer((0,2))

        # Motion buttons

        fwd_button = wx.Button(self,-1,label="Forward", pos=(x+dist*2,y-dist))
        sizer.Add(fwd_button, (1,1))
        self.Bind(wx.EVT_BUTTON, self.fwd_button_OnButtonClick, fwd_button)

        left_button = wx.Button(self,-1,label="Left", pos=(x,y))
        sizer.Add(left_button, (2,0))
        self.Bind(wx.EVT_BUTTON, self.left_button_OnButtonClick, left_button)

        stop_button = wx.Button(self,-1,label="Stop", pos=(x+dist*2,y))
        stop_button.SetBackgroundColour('red')
        sizer.Add(stop_button, (2,1))
        self.Bind(wx.EVT_BUTTON, self.stop_button_OnButtonClick, stop_button)

        right_button = wx.Button(self,-1,label="Right", pos=(x+dist*4,y))
        sizer.Add(right_button, (2,2))
        self.Bind(wx.EVT_BUTTON, self.right_button_OnButtonClick, right_button)
        
        bwd_button = wx.Button(self,-1,label="Back", pos=(x+dist*2,y+dist))
        sizer.Add(bwd_button, (3,1))
        self.Bind(wx.EVT_BUTTON, self.bwd_button_OnButtonClick, bwd_button)
        
        # Led buttons
        x=75
        y=25
        left_led_button = wx.Button(self,-1,label="Left LED", pos=(x,y))
        sizer.Add(left_led_button, (4,0))
        self.Bind(wx.EVT_BUTTON, self.left_led_button_OnButtonClick, left_led_button)

        right_led_button = wx.Button(self,-1,label="Right LED", pos=(x+dist*4,y))
        sizer.Add(right_led_button, (4,2))
        self.Bind(wx.EVT_BUTTON, self.right_led_button_OnButtonClick, right_led_button)       

        # Eyes buttons
        x=75
        y=65
        left_eye_button = wx.Button(self,-1,label="Left eye", pos=(x,y))
        sizer.Add(left_eye_button, (5,0))
        self.Bind(wx.EVT_BUTTON, self.left_eye_button_OnButtonClick, left_eye_button)

        right_eye_button = wx.Button(self,-1,label="Right eye", pos=(x+dist*4,y))
        sizer.Add(right_eye_button, (5,2))
        self.Bind(wx.EVT_BUTTON, self.right_eye_button_OnButtonClick, right_eye_button)    
        
        y=320
        battery_button = wx.Button(self,-1,label="Check Battery Voltage", pos=(x,y))
        sizer.Add(battery_button, (6,1))
        self.Bind(wx.EVT_BUTTON, self.battery_button_OnButtonClick, battery_button)

        firmware_button = wx.Button(self,-1,label="Check Firmware Version", pos=(x,y+dist/2))
        sizer.Add(firmware_button, (7,1))
        self.Bind(wx.EVT_BUTTON, self.firmware_button_OnButtonClick, firmware_button)        
        # Set up labels

        
        self.battery_label = wx.StaticText(self,-1,label=str(round(v,1))+"V",pos=(x+dist*2+65,y+6))
        sizer.Add( self.battery_label, (6,2),(1,2), wx.EXPAND )
        
        self.firmware_label = wx.StaticText(self,-1,label=str(f),pos=(x+dist*2+65,y+6+dist/2))
        sizer.Add( self.firmware_label, (7,2),(1,2), wx.EXPAND )
        
        y=460

        self.Show(True)     

    def battery_button_OnButtonClick(self,event):
        global v
        # v=gopigo.volt()
        v=round(gpg.volt(),1)
        self.battery_label.SetLabel(str(v)+"V")    
        
    def firmware_button_OnButtonClick(self,event):
        global f
        f=gpg.get_version_firmware()
        self.firmware_label.SetLabel(str(f))
     
    def left_button_OnButtonClick(self,event):
        f=gpg.left()
 
    def stop_button_OnButtonClick(self,event):
        f=gpg.stop()

    def right_button_OnButtonClick(self,event):
        f=gpg.right()
        
    def fwd_button_OnButtonClick(self,event):
        f=gpg.forward()

    def bwd_button_OnButtonClick(self,event):
        f=gpg.backward()

    def left_led_button_OnButtonClick(self,event):
        global left_led
        if left_led==0:
            gpg.led_on(1)
            left_led=1        
        else :
            gpg.led_off(1)
            left_led=0
    
    def right_led_button_OnButtonClick(self,event):
        global right_led
        if right_led==0:
            gpg.led_on(0)
            right_led=1        
        else :
            gpg.led_off(0)
            right_led=0

    def right_eye_button_OnButtonClick(self,event):
        global right_eye
        if right_eye==0:
            gpg.open_right_eye()
            right_eye=1        
        else :
            gpg.close_right_eye()
            right_eye=0

    def left_eye_button_OnButtonClick(self,event):
        global left_eye
        if left_eye==0:
            gpg.open_left_eye()
            left_eye=1        
        else :
            gpg.close_left_eye()
            left_eye=0

    def onClose(self, event):	# Close the entire program.
        self.Close()

if __name__ == "__main__":
    app = wx.App()
    frame = gopigo_control_app(None,-1,'GoPiGo3 Control Panel')
    app.MainLoop()
