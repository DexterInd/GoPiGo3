#!/usr/bin/python

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
    raise ImportError,"The wxPython module is required to run this program"

import atexit
atexit.register(gpg.stop)    

left_led=0
right_led=0
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
        exit_button = wx.Button(self, label="Exit", pos=(240+75,550))
        exit_button.Bind(wx.EVT_BUTTON, self.onClose)
        
        # robot = "/home/pi/Desktop/GoBox/Troubleshooting_GUI/dex.png"
        # png = wx.Image(robot, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        # wx.StaticBitmap(self, -1, png, (0, 0), (png.GetWidth()-320, png.GetHeight()-20))
        # self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)		# Sets background picture
    
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
                sizer.AddStretchSpacer((1,1))
                sizer.Add(detected_robot_str,(0,1))
                sizer.AddStretchSpacer((1,1))

        # Motion buttons
        left_button = wx.Button(self,-1,label="Left", pos=(x,y))
        sizer.Add(left_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.left_button_OnButtonClick, left_button)

        stop_button = wx.Button(self,-1,label="Stop", pos=(x+dist*2,y))
        stop_button.SetBackgroundColour('red')
        sizer.Add(stop_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.stop_button_OnButtonClick, stop_button)

        right_button = wx.Button(self,-1,label="Right", pos=(x+dist*4,y))
        sizer.Add(right_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.right_button_OnButtonClick, right_button)
        
        fwd_button = wx.Button(self,-1,label="Forward", pos=(x+dist*2,y-dist))
        sizer.Add(fwd_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.fwd_button_OnButtonClick, fwd_button)
        
        bwd_button = wx.Button(self,-1,label="Back", pos=(x+dist*2,y+dist))
        sizer.Add(bwd_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.bwd_button_OnButtonClick, bwd_button)
        
        # Led buttons
        x=75
        y=25
        left_led_button = wx.Button(self,-1,label="Left LED", pos=(x,y))
        sizer.Add(left_led_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.left_led_button_OnButtonClick, left_led_button)

        right_led_button = wx.Button(self,-1,label="Right LED", pos=(x+dist*4,y))
        sizer.Add(right_led_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.right_led_button_OnButtonClick, right_led_button)       
        
        y=320
        battery_button = wx.Button(self,-1,label="Check Battery Voltage\t ", pos=(x,y))
        sizer.Add(battery_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.battery_button_OnButtonClick, battery_button)

        firmware_button = wx.Button(self,-1,label="Check Firmware Version\t", pos=(x,y+dist/2))
        sizer.Add(firmware_button, (0,1))
        self.Bind(wx.EVT_BUTTON, self.firmware_button_OnButtonClick, firmware_button)        
        # Set up labels

        
        self.battery_label = wx.StaticText(self,-1,label=str(v)+"V",pos=(x+dist*2+45,y+6))
        sizer.Add( self.battery_label, (1,0),(1,2), wx.EXPAND )
        
        self.firmware_label = wx.StaticText(self,-1,label=str(f),pos=(x+dist*2+45,y+6+dist/2))
        sizer.Add( self.firmware_label, (1,0),(1,2), wx.EXPAND )
        
        sizer.Add( self.firmware_label, (1,0),(1,2), wx.EXPAND )
        
        y=460

        self.Show(True)     

    def battery_button_OnButtonClick(self,event):
        global v
        # v=gopigo.volt()
        v=gpg.volt()
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

    def onClose(self, event):	# Close the entire program.
        self.Close()

if __name__ == "__main__":
    app = wx.App()
    frame = gopigo_control_app(None,-1,'GoPiGo3 Control Panel')
    app.MainLoop()