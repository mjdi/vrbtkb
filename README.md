# FYDP NE2017_11: Repurposing http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html ,
# in a 4-button + clickable analog joystick Raspberry Pi (RPi) Zero based bluetooth controller used for emulating a regular 
# qwerty keyboard's functionality on a VR-enabled Android smartphone while in the VR environment (with no touch screen access)

# Add line '@bash /home/pi/vrbtkb/startuo_script.sh' to the end of '/home/pi/.config/lxsession/LXDE/autostart' file for headless operation
# waiting about ~2 minutes for RPi to boot and enter bt_server.py script to then connect to Android smartphone via bluetooth

# Button GPIO pins:

#		GPIO.setmode(GPIO.BOARD)

#		self.btn2_pin = 33
#		self.btn3_pin = 31
#		self.btn4_pin = 35
#		self.btn5_pin = 37
