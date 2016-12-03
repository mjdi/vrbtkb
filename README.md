# FYDP NE2017_11: Repurposing http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html ,
# in a 4-button + clickable analog joystick Raspberry pi Zero-based bluetooth controller to be used for emulating regular 
# qwerty keyboard functionality on a VR-enabled Android smartphone

# Add line '@bash /home/pi/vrbtkb/vr_hid_bt_kb_setup.sh' to the end of /home/pi/.config/lxsession/LXDE/autostart

# Button GPIO pins:

#		GPIO.setmode(GPIO.BOARD)

#		self.btn2_pin = 33
#		self.btn3_pin = 31
#		self.btn4_pin = 35
#		self.btn5_pin = 37
