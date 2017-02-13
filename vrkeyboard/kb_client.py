# -*- coding: utf8 -*-

#!/usr/bin/python
#
# Adapted from www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
#
# also adapted from http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html
import sys
hand = str(sys.argv[1]) # accept the handedness as an C.L. argument, sys.argv[0] is the name of the python script itself

import subprocess # also used to grep spi device Bus and Device integer values
device = subprocess.check_output("ls /home/",shell=True).rstrip()

if device == "pi" :
	import RPi.GPIO as GPIO  #to use the GPIO pins, was used for RPi not CHIP
elif device == "chip" :
	import CHIP_IO.GPIO as GPIO		# https://github.com/xtacocorex/CHIP_IO for documentation
# import CHIP_IO.OverlayManager as OM 	# https://github.com/xtacocorex/CHIP_IO, not necessary now with /etc/rc.local nano edit
# OM.load("SPI2")
import spidev   #to use joystick
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import os
import numpy as np

char_str_2_HID_code_and_shift_mod_required = {		
	"Ee" : { "hid" : 41 , "shift" : 0 }, 	# Escape			
	"1_" : { "hid" : 30 , "shift" : 0 },
	"!_" : { "hid" : 30 , "shift" : 1 },		
	"2_" : { "hid" : 31 , "shift" : 0 },
	"@_" : { "hid" : 31 , "shift" : 1 },
	"3_" : { "hid" : 32 , "shift" : 0 },
	"#_" : { "hid" : 32 , "shift" : 1 },		
	"4_" : { "hid" : 33 , "shift" : 0 },
	"$_" : { "hid" : 33 , "shift" : 1 },
	"5_" : { "hid" : 34 , "shift" : 0 },
	"%_" : { "hid" : 34 , "shift" : 1 },
	"6_" : { "hid" : 35 , "shift" : 0 },
	"^_" : { "hid" : 35 , "shift" : 1 },
	"7_" : { "hid" : 36 , "shift" : 0 },
	"&_" : { "hid" : 36 , "shift" : 1 },
	"8_" : { "hid" : 37 , "shift" : 0 },
	"*_" : { "hid" : 37 , "shift" : 1 },
	"9_" : { "hid" : 38 , "shift" : 0 },
	"(_" : { "hid" : 38 , "shift" : 1 },
	"0_" : { "hid" : 39 , "shift" : 0 },
	")_" : { "hid" : 39 , "shift" : 1 },		
	"-_" : { "hid" : 45 , "shift" : 0 },
	"__" : { "hid" : 45 , "shift" : 1 },
	"=_" : { "hid" : 46 , "shift" : 0 },
	"+_" : { "hid" : 46 , "shift" : 1 },
	"Be" : { "hid" : 42 , "shift" : 0 },	# Backspace
	"Tb" : { "hid" : 43 , "shift" : 0 },	# Tab
	"UT" : { "hid" : 43 , "shift" : 1 },	# Un-Tab
	"q_" : { "hid" : 20 , "shift" : 0 },
	"Q_" : { "hid" : 20 , "shift" : 1 },
	"w_" : { "hid" : 26 , "shift" : 0 },	
	"W_" : { "hid" : 26 , "shift" : 1 },
	"e_" : { "hid" : 8  , "shift" : 0 },
	"E_" : { "hid" : 8  , "shift" : 1 },
	"r_" : { "hid" : 21 , "shift" : 0 },
	"R_" : { "hid" : 21 , "shift" : 1 },
	"t_" : { "hid" : 23 , "shift" : 0 },
	"T_" : { "hid" : 23 , "shift" : 1 },
	"y_" : { "hid" : 28 , "shift" : 0 },
	"Y_" : { "hid" : 28 , "shift" : 1 },
	"u_" : { "hid" : 24 , "shift" : 0 },
	"U_" : { "hid" : 24 , "shift" : 1 },
	"i_" : { "hid" : 12 , "shift" : 0 },
	"I_" : { "hid" : 12 , "shift" : 1 },
	"o_" : { "hid" : 18 , "shift" : 0 },
	"O_" : { "hid" : 18 , "shift" : 1 },
	"p_" : { "hid" : 19 , "shift" : 0 },
	"P_" : { "hid" : 19 , "shift" : 1 },
	"[_" : { "hid" : 47 , "shift" : 0 },
	"{_" : { "hid" : 47 , "shift" : 1 },
	"]_" : { "hid" : 48 , "shift" : 0 },
	"}_" : { "hid" : 48 , "shift" : 1 },
	"Er" : { "hid" : 40 , "shift" : 0 },	# Enter/Return
	#"KEY_LEFTCONTROL" : 224,	# Left Control, ================== Control ============
	"a_" : { "hid" : 4  , "shift" : 0 },
	"A_" : { "hid" : 4  , "shift" : 1 },
	"s_" : { "hid" : 22 , "shift" : 0 },
	"S_" : { "hid" : 22 , "shift" : 1 },
	"d_" : { "hid" : 7  , "shift" : 0 },
	"D_" : { "hid" : 7  , "shift" : 1 },
	"f_" : { "hid" : 9  , "shift" : 0 },
	"F_" : { "hid" : 9  , "shift" : 1 },
	"g_" : { "hid" : 10 , "shift" : 0 },
	"G_" : { "hid" : 10 , "shift" : 1 },
	"h_" : { "hid" : 11 , "shift" : 0 },
	"H_" : { "hid" : 11 , "shift" : 1 },
	"j_" : { "hid" : 13 , "shift" : 0 },
	"J_" : { "hid" : 13 , "shift" : 1 },
	"k_" : { "hid" : 14 , "shift" : 0 },
	"K_" : { "hid" : 14 , "shift" : 1 },
	"l_" : { "hid" : 15 , "shift" : 0 },
	"L_" : { "hid" : 15 , "shift" : 1 },
	";_" : { "hid" : 51 , "shift" : 0 },
	":_" : { "hid" : 51 , "shift" : 1 },
	"'_" : { "hid" : 52 , "shift" : 0 },	# Apostrophe
	"\"_" :{ "hid" : 52 , "shift" : 1 },
	"`_" : { "hid" : 53 , "shift" : 0 },	# Grave
	"~_" : { "hid" : 53 , "shift" : 1 },
	#"KEY_LEFTSHIFT" : 225,	# No Shift key, using Joystick set ============= SHIFT ==========  
	"\\_" : { "hid" : 50 , "shift" : 0 },	# Backslash	
	"|_" : { "hid" : 50 , "shift" : 1 },
	"z_" : { "hid" : 29 , "shift" : 0 },
	"Z_" : { "hid" : 29 , "shift" : 1 },
	"x_" : { "hid" : 27 , "shift" : 0 },
	"X_" : { "hid" : 27 , "shift" : 1 },
	"c_" : { "hid" : 6  , "shift" : 0 },
	"C_" : { "hid" : 6  , "shift" : 1 },
	"v_" : { "hid" : 25 , "shift" : 0 },
	"V_" : { "hid" : 25 , "shift" : 1 },
	"b_" : { "hid" : 5  , "shift" : 0 },
	"B_" : { "hid" : 5  , "shift" : 1 },
	"n_" : { "hid" : 17 , "shift" : 0 },
	"N_" : { "hid" : 17 , "shift" : 1 },
	"m_" : { "hid" : 16 , "shift" : 0 },
	"M_" : { "hid" : 16 , "shift" : 1 },
	",_" : { "hid" : 54 , "shift" : 0 },
	"<_" : { "hid" : 54 , "shift" : 1 },
	"._" : { "hid" : 55 , "shift" : 0 },
	">_" : { "hid" : 55 , "shift" : 1 },
	"/_" : { "hid" : 56 , "shift" : 0 },
	"?_" : { "hid" : 56 , "shift" : 1 },
	#"KEY_RIGHTSHIFT" : 229,
	# "AT" : 226,	# Left Alt, we really only need one Alt  # ===============ALT========
	"Se" : { "hid" : 44 , "shift" : 0 },	# Space
	#"KEY_CAPSLOCK" : 57,	# Don't really need if we have a joystic-Shift set
	"F1" : { "hid" : 58 , "shift" : 0 },
	"F2" : { "hid" : 59 , "shift" : 0 },
	"F3" : { "hid" : 60 , "shift" : 0 },
	"F4" : { "hid" : 61 , "shift" : 0 },
	"F5" : { "hid" : 62 , "shift" : 0 },
	"F6" : { "hid" : 63 , "shift" : 0 },
	"F7" : { "hid" : 64 , "shift" : 0 },
	"F8" : { "hid" : 65 , "shift" : 0 },
	"F9" : { "hid" : 66 , "shift" : 0 },
	"10" : { "hid" : 67 , "shift" : 0 },	# F10
	"11" : { "hid" : 68 , "shift" : 0 },	# F11
	"12" : { "hid" : 69 , "shift" : 0 },	# F12
	#"KEY_RIGHTCTRL" : 228,
	#"KEY_RIGHTALT" : 230,
	"He" : { "hid" : 74 , "shift" : 0 },	# Home
	"Up" : { "hid" : 82 , "shift" : 0 },	# Up
	"PU" : { "hid" : 75 , "shift" : 0 },	# Page Up
	"Lt" : { "hid" : 80 , "shift" : 0 },	# Left
	"Rt" : { "hid" : 79 , "shift" : 0 },	# Right
	"Ed" : { "hid" : 77 , "shift" : 0 },	# End
	"Dn" : { "hid" : 81 , "shift" : 0 },	# Down
	"PD" : { "hid" : 78 , "shift" : 0 },	# Page Down
	"It" : { "hid" : 73 , "shift" : 0 },	# Insert
	"De" : { "hid" : 76 , "shift" : 0 },	# Delete
	# 
	# Multi-Functional Keys
	#
	#"KEY_MUTE" : 239,
	#"KEY_VOLUMEDOWN" : 238,
	#"KEY_VOLUMEUP" : 237,
	#"KEY_POWER" : 102,
	#"KEY_PAUSE" : 72,
	#"KEY_LEFTMETA" : 227,
	#"KEY_RIGHTMETA" : 231,
	#"KEY_STOP" : 243,
	#"KEY_OPEN" : 116,
	#"KEY_BACK" : 241,
	#"KEY_FORWARD" : 242,
	#"KEY_NEXTSONG" : 235,
	#"KEY_PLAYPAUSE" : 232,
	#"KEY_PREVIOUSSONG" : 234,
	#"KEY_STOPCD" : 233,
	#"KEY_REFRESH" : 250,
	#"KEY_SCROLLUP" : 245,
    	#"KEY_SCROLLDOWN" : 246,
}

# all str_arrays (which are then used to get HID codes + necessary modifiers) 
# are accessed via a combination of finger and direction, the joystick navigating between str_arrays

# [finger][direction], where finger = {L5=0, L4=1, L3=2, L2=3, L1=4, R1=5, R2=6, R3=7, R4=8, R5=9}
# and where direction = {neutral=0, north=1, east=2, south=3, west=4}, counting clockwise

# accessed via Joyclick-North, since numerical keys are located on top side of qwerty keyboard

left_numspecial_str_2D_array = np.array([
	["1_","=_",")_","#_","(_"],
	["2_","-_","It","$_","Ee"],
	["3_","+_","Be","%_","De"],
	["4_","*_","]_","^_","[_"],
	["5_","__","__","__","__"]],
	dtype="a2"
	)

right_numspecial_str_2D_array = np.array([
	["0_","\\_","{_","/_","}_"],
	["9_","&_","Be","|_","De"],
	["8_","@_","It",";_","Ee"],
	["7_","!_","<_",":_",">_"],
	["6_","__","__","__","__"]],
	dtype="a2"
	)

# accessed via Joyclick-East, since arrow keys are located on right side of qwerty keyboard

left_arrowfunc_str_2D_array = np.array([
	["Lt","F1","PD","11","PU"],
	["Dn","F2","It","12","Ee"],
	["Up","F3","Be","__","De"],
	["Rt","F4","Ed","__","He"],
	["F5","__","__","__","__"]],
	dtype="a2"
	)
	
right_arrowfunc_str_2D_array = np.array([
	["Rt","10","PD","__","PU"],
	["Dn","F9","Be","._","De"],
	["Up","F8","It",",_","Ee"],
	["Lt","F7","Ed","__","He"],
	["F6","__","__","__","__"]],
	dtype="a2"
	)

# accessed via Joyclick-South, (default mode) since lowercase letters are located along the bottom of qwerty keyboard
	
left_loweralpha_str_2D_array = np.array([
	["a_","q_","'_","z_","`_"],
	["s_","w_","It","x_","Ee"],
	["e_","d_","Be","c_","De"],
	["t_","f_","r_","v_","g_"],
	["__","__","__","__","__"]],
	dtype="a2"
	)

right_loweralpha_str_2D_array = np.array([
	["p_","y_","/_","b_",";_"],
	["o_","l_","Be","._","De"],
	["i_","k_","It",",_","Ee"],
	["n_","u_","m_","j_","h_"],
	["__","__","__","__","__"]],
	dtype="a2"
	)

# accessed via Joyclick-West, since Caps key is located on left side of qwerty keyboard
	
left_capsalpha_str_2D_array = np.array([
	["A_","Q_","\"_","Z_","~_"],
	["S_","W_","It","X_","Ee"],
	["E_","D_","Be","C_","De"],
	["T_","F_","R_","V_","G_"],
	["__","__","__","__","__"]],
	dtype="a2"
	)
	
right_capsalpha_str_2D_array = np.array([
	["P_","Y_","?_","B_",":_"],
	["O_","L_","Be",">_","De"],
	["I_","K_","It","<_","Ee"],
	["N_","U_","M_","J_","H_"],
	["__","__","__","__","__"]],
	dtype="a2"
	)

def get_numspecial_char_str(btn_idx, dir_idx):
    if   hand == "left" :
    	return left_numspecial_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
	return right_numspecial_str_2D_array[btn_idx][dir_idx]

def get_arrowfunc_char_str(btn_idx, dir_idx):
    if   hand == "left" :
        return left_arrowfunc_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
        return right_arrowfunc_str_2D_array[btn_idx][dir_idx]
	
def get_loweralpha_char_str(btn_idx, dir_idx):
    if   hand == "left" :
    	return left_loweralpha_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
    	return right_loweralpha_str_2D_array[btn_idx][dir_idx]

def get_capsalpha_char_str(btn_idx, dir_idx):
    if   hand == "left" :
	return left_capsalpha_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
	return right_capsalpha_str_2D_array[btn_idx][dir_idx]

def get_char_str(arr_idx, btn_idx, dir_idx):
    if   arr_idx == 1 :
	return get_numspecial_char_str(btn_idx, dir_idx):
    elif arr_idx == 2 :
	return get_arrowfunc_char_str(btn_idx, dir_idx):
    elif arr_idx == 3 :
	return get_loweralpha_char_str(btn_idx, dir_idx):
    elif arr_idx == 4 :
	return get_capsalpha_char_str(btn_idx, dir_idx):
	
def get_HID(char_str):
    return char_str_2_HID_code_and_shift_mod_required[char_str]["hid"]

def get_Shift_Required(char_str):
    return char_str_2_HID_code_and_shift_mod_required[char_str]["shift"]

# ======================
# Analog Joystick Setup
# ======================

print "opening up SPI Bus to read Analog Pins"
	
#open SPI bus
spi = spidev.SpiDev()

if device == "pi" :
	spi.open(0,0) # spidev open ( spi.open(X,Y) opens the spi device located at /dev/spiX.Y )
elif device == "chip" :
	SPI_BUS = int(subprocess.check_output("ls /dev/spidev* | grep -oP '(\d+)\.' | grep -oP '(\d+)'", shell=True).rstrip())
	SPI_DEVICE = int(subprocess.check_output("ls /dev/spidev* | grep -oP '\.(\d+)' | grep -oP '(\d+)'", shell=True).rstrip())
	spi.open(SPI_BUS,SPI_DEVICE)

# Function to read SPI data from MCP3008 chip
# Channel must be an integer 0-7
def ReadChannel(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

class VR_Keyboard():


	def __init__(self):
		#the structure for a bt keyboard input report (size is 10 bytes)

		#self.kb_state=[
		#	0xA1, #this is an input report
		#	0x01, #Usage report = Keyboard
		#	#Bit array for Modifier keys
		#	[0,	#Right GUI - Windows Key
		#	 0,	#Right ALT
		#	 0, 	#Right Shift
		#	 0, 	#Right Control
		#	 0,	#Left GUI
		#	 0, 	#Left ALT
		#	 0,	#Left Shift
		#	 0],	#Left Control
		#	0x00,	#Vendor reserved
		#	0x00,	#rest is space for 6 keys
		#	0x00,
		#	0x00,
		#	0x00,
		#	0x00,
		#	0x00]

		print "setting up DBus Client"	
		self.bus = dbus.SystemBus()
		self.btkservice = self.bus.get_object('org.yaptb.btkbservice','/org/yaptb/btkbservice')
		self.iface = dbus.Interface(self.btkservice,'org.yaptb.btkbservice')	

 		# inputs of four individual push buttons. 
		
		print "setting up GPIO structure to interpret digital pins"

#               ========================== GPIO setup for Raspberry Pi Zero =====================

#               GPIO.setmode(GPIO.BOARD)

#               self.btn2_pin = 33
#               self.btn3_pin = 31
#               self.btn4_pin = 35
#               self.btn5_pin = 37

#               GPIO.setup(self.btn2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # index finger
#               GPIO.setup(self.btn3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # middle finger
#               GPIO.setup(self.btn4_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # ring finger
#               GPIO.setup(self.btn5_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # pinky finger

#               ========================= GPIO setup for Next Thing Co. CHIP ====================
#		# https://github.com/xtacocorex/CHIP_IO for documentation

                self.btn2_pin = "GPIO2"
                self.btn3_pin = "GPIO3"
                self.btn4_pin = "GPIO4"
                self.btn5_pin = "GPIO5"

                GPIO.setup(self.btn2_pin, GPIO.IN) # index finger
                GPIO.setup(self.btn3_pin, GPIO.IN) # middle finger
                GPIO.setup(self.btn4_pin, GPIO.IN) # ring finger
                GPIO.setup(self.btn5_pin, GPIO.IN) # pinky finger
	
		# Define sensor channels
		# (channels 3 to 7 unused)
		#self.swt_channel = 0
		#self.vrx_channel = 1
		#self.vry_channel = 2

		self.analog_dimension = 1024 	# 2^10 

		# Harcoded deadzone width;
		self.deadzone_width = 64	# 2^7 / 2

		# used to access the alpha_str_2D_array, for debugging purposes right now

		self.arr_idx = 3; # default to loweralpha_char_str_2D_array 
				  # direction = {neutral=0, north=1, east=2, south=3, west=4}, counting clockwise

		# Initialize last variables
		
                self.btns_pressed = [0,0,0,0,0] # zero-based but pertains to buttons 1 through 5
		self.reset_btns_pressed()
		
                self.last_btn_pressed = 0 # TO BE USED WITH CASCADING TYPING
		
		self.last_mod_bit_str = "00000000"
		self.last_hid = -1

		# Think about using a conditional to check for in-valid index at start-up
		self.last_btn_idx = -1
		self.last_dir_idx = -1
		self.last_arr_idx = 4 # default to lowercase letters

		self.reset_joystick_path()

		# modifier lockers: none -> once -> always (locked) -> none => kb.L_ == 0 -> kb.L_ == 1 -> kb.L_ == 1 and kb.L__lock == 1 -> kb.L_ = 0

		self.depressed_analog_shift_modifier = 1 # required to prevent holding Analog Click (Shift) from rapidly cycling through
		self.reset_modifier_locks()

		self.reset_modifiers()

		# end of __init__

	# assume all buttons are not initially pressed	
		
	def reset_btns_pressed(self):
		self.btns_pressed[0] = 0
		self.btns_pressed[1] = 0
		self.btns_pressed[2] = 0
		self.btns_pressed[3] = 0
		self.btns_pressed[4] = 0
		
	# set all path booleans to zero
	def reset_joystick_path(self):
		self.D2N = 0 # deadzone to north
		self.D2E = 0
		self.D2S = 0
		self.D2W = 0
		self.N2D = 0 # north to deadzone
		self.N2E = 0
		self.N2W = 0
		self.E2D = 0 # east to deadzone
		self.E2N = 0
		self.E2S = 0
		self.S2D = 0 # south to deadzone
		self.S2E = 0
		self.S2W = 0
		self.W2D = 0 # west to deadzone
		self.W2N = 0
		self.W2S = 0

	# segment of code copied from original keytable.py
	# Map modifier keys to array element in the bit array
	#modkeys = {
	#   "KEY_RIGHTMETA" : 0,
	#   "KEY_RIGHTALT" : 1,
	#   "KEY_RIGHTSHIFT" : 2,
	#   "KEY_RIGHTCTRL" : 3,
	#   "KEY_LEFTMETA" : 4,
	#   "KEY_LEFTALT": 5,
	#   "KEY_LEFTSHIFT": 6,
	#   "KEY_LEFTCTRL": 7
	#}

	def reset_modifiers(self):
		self.LM = 0
		if not self.LA_lock == 1 :
			self.LA = 0
		if not self.LS_lock == 1 :
			self.LS = 0
		if not self.LC_lock == 1 :
			self.LC = 0
		self.RM = 0
		if not self.RA_lock == 1 :
			self.RA = 0
		if not self.RS_lock == 1 :
			self.RS = 0
		if not self.RC_lock == 1 :
			self.RC = 0

	def reset_modifier_locks(self):
		self.LM_lock = 0
		self.LA_lock = 0
		self.LS_lock = 0
		self.LC_lock = 0
		self.RM_lock = 0
		self.RA_lock = 0
		self.RS_lock = 0
		self.RC_lock = 0

	#forward keyboard events to the dbus service (deprecated, not used in this script)
   	def send_input(self):

		bin_str=""
		element=self.kb_state[2]
		for bit in element:
			bin_str += str(bit) # forms 8 char string which represents modifier(s), i.e. "00100000" is left shift

			self.iface.send_keys(int(bin_str,2),self.kb_state[4:10] )

if __name__ == "__main__":

	print "Setting up VR Bluetooth Keyboard"

	kb = VR_Keyboard()

	while True :

		# reset dir_idx, btn_idx, arr_idx, and hid every loop, so as to meet else condition of typing conditional

		dir_idx = -1
		btn_idx = -1
		arr_idx = -1
		hid = 0
		char_str = ""

                # determine direction_index (map x/y to cardinal directions, seen below), using circular deadzone!
		#      \     North      /
		#       \ ____________ /
		#        |            |
		#  West  | “deadzone” |  East 
		#        |____________|
		#       /              \
		#      /     South      \


		# read x and y potentiometer values
		xpos = ReadChannel(1)
		ypos = ReadChannel(2)
		
		#Center values at zero by subtracting 512
		xpos = xpos - ( kb.analog_dimension / 2 )
		ypos = ypos - ( kb.analog_dimension / 2 )

		# (hand prototype)rotate control stick 180 degrees if need be 
		# xpos = -xpos
		# ypos = -ypos

		# Determine dir_idx

		if (xpos * xpos + ypos * ypos) < kb.deadzone_width * kb.deadzone_width / 4 : # circular deadzone
		#if abs(xpos) < ( kb.deadzone_width / 2 ) and abs(ypos) < ( kb.deadzone_width / 2 ) : # square deadzone
			LH_direction = 'deadz'

			dir_idx = 0

			if   kb.last_dir_idx == 1 :
				kb.N2D = 1
			elif kb.last_dir_idx == 2 :	
				kb.E2D = 1
			elif kb.last_dir_idx == 3 :	
				kb.S2D = 1
			elif kb.last_dir_idx == 4 :	
				kb.W2D = 1	

			# determine white-space and ctrl/alt modifiers

			if not (kb.N2W == 1 or kb.W2S == 1 or kb.S2E == 1 or kb.E2N == 1 or kb.N2E == 1 or kb.E2S == 1 or kb.S2W == 1 or kb.W2N == 1) : # no rotation whatsoever
				if   (kb.D2N * kb.N2D) == 1 :
					char_str = "Se" #Space
				elif (kb.D2E * kb.E2D) == 1 :
					char_str = "Er" #Enter
				elif (kb.D2S * kb.S2D) == 1 :
					char_str = "__"	#Underscore
				elif (kb.D2W * kb.W2D) == 1 :
					char_str = "Tb"	#Tab

			if kb.N2W * kb.W2S * kb.S2E * kb.E2N == 1 : # full counter-clockwise rotation

				# 3-state toggle conditional logic

				if   kb.LC == 0 :
					kb.LC = 1 # turn left ctrl modifier on (for one character/function)
				elif kb.LC == 1 and kb.LC_lock == 1 :
					kb.LC = 0 # turn both left ctrl off 
					kb.LC_lock = 0  # and left ctrl modifier lock off 
				elif kb.LC == 1 :
					kb.LC_lock = 1 # turn left ctrl modifier lock on (for endless characters/functions)

			if kb.N2E * kb.E2S * kb.S2W * kb.W2N == 1 : # full clockwise rotation

				# 3-state toggle conditional logic

				if   kb.LA == 0 :
					kb.LA = 1 # turn left alt modifier on (for one character/function)
				elif kb.LA == 1 and kb.LA_lock == 1 :
					kb.LA = 0 # turn both left alt off 
					kb.LA_lock = 0  # and left alt modifier lock off
				elif kb.LA == 1 :
					kb.LA_lock = 1 # turn left alt modifier lock on (for endless characters/functions)

			kb.reset_joystick_path() # always reset all joystick paths when we reach deadzone again
		else :
			if ypos >= abs(xpos) :
				LH_direction = 'north'

				dir_idx = 1

				if   kb.last_dir_idx == 0 :
					kb.D2N = 1
				elif kb.last_dir_idx == 2 :
					kb.E2N = 1
				elif kb.last_dir_idx == 4 :
					kb.W2N = 1
			if ypos <= -abs(xpos) :
				LH_direction = 'south'

				dir_idx = 3

				if   kb.last_dir_idx == 0 :
					kb.D2S = 1
				elif kb.last_dir_idx == 2 :
					kb.E2S = 1
				elif kb.last_dir_idx == 4 :
					kb.W2S = 1
			if xpos > abs(ypos) :
				LH_direction = 'east_'

				dir_idx = 2

				if   kb.last_dir_idx == 0 :
					kb.D2E = 1
				elif kb.last_dir_idx == 1 :
					kb.N2E = 1
				elif kb.last_dir_idx == 3 :
					kb.S2E = 1
			if xpos < -abs(ypos) :
				LH_direction = 'west_'

				dir_idx = 4

				if   kb.last_dir_idx == 0 :
					kb.D2W = 1
				elif kb.last_dir_idx == 1 :
					kb.N2W = 1
				elif kb.last_dir_idx == 3 :
					kb.S2W = 1

		# DEBUGGING Whitespace, Ctrl, Alt modifiers

		# print "{D2N,D2E,D2S,D2W} = [" + str(kb.D2N) + str(kb.D2E) + str(kb.D2S) + str(kb.D2W) + "], " ,
		# print "{N2D,E2D,S2D,W2D} = [" + str(kb.N2D) + str(kb.E2D) + str(kb.S2D) + str(kb.W2D) + "], " ,
		# print "{N2W,W2S,S2E,E2N} = [" + str(kb.N2W) + str(kb.W2S) + str(kb.S2E) + str(kb.E2N) + "], " ,
		# print "{N2E,E2S,S2W,W2N} = [" + str(kb.N2E) + str(kb.E2S) + str(kb.S2W) + str(kb.W2N) + "], " ,  

		# FUTURE WORK: Determine one-by-one if each finger is pressed (rather than all at once)

		# Determine btn_idx

                # read push button(s) state
		# off = 0, on = 1
                btn5 = GPIO.input(kb.btn5_pin)
		if btn5 == 1:
			btn_idx = 0
			kb.btns_pressed[4] = 1
		else:
			kb.btns_pressed[4] = 0

		btn4 = GPIO.input(kb.btn4_pin)
		if btn4 == 1:
			btn_idx = 1
			kb.btns_pressed[3] = 1
		else:
			kb.btns_pressed[3] = 0

		btn3 = GPIO.input(kb.btn3_pin)
		if btn3 == 1:
			btn_idx = 2
			kb.btns_pressed[2] = 1
		else:
			kb.btns_pressed[2] = 0
			
		btn2 = GPIO.input(kb.btn2_pin)
		if btn2 == 1:
			btn_idx = 3
			kb.btns_pressed[1] = 1
		else:
			kb.btns_pressed[1] = 0
			
		# read z-click on the analog stick
		# off = ~1024 , on = 0
		btn1 = ReadChannel(0)
		if btn1 == 0:
			btn_idx = 4
			kb.btns_pressed[0] = 1
		else:
			kb.btns_pressed[0] = 0
			#print "depress" ,
			kb.depressed_analog_shift_modifier = 1 # records that we've depressed the analog click, necessary for Analog Click Shift Modifier to function

		# DEBUGGING Button/Direction recognition
		# print "btn5 = " + str(btn5) + "\tbtn4 = " + str(btn4) + "\tbtn3 = " + str(btn3) + "\tbtn2 = " + str(btn2) + "\tbtn1 = " + str(btn1) + "\tLHdirection =" + LH_direction , 
		# mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)
		# print "\tmod_bit_str=" + mod_bit_str ,
		# mod_lock_bit_str = str(kb.LM_lock) + str(kb.LA_lock) + str(kb.LS_lock) + str(kb.LC_lock) + str(kb.RM_lock) + str(kb.RA_lock) + str(kb.RS_lock) + str(kb.RC_lock)
		# print "\tmod_lock_bit_str=" + mod_lock_bit_str ,
 		# print "\tdepressed_analog_shift_modifier = " + str(kb.depressed_analog_shift_modifier) , 
 		# print "\tkb.LS = " + str(kb.LS) + "\tkb.LS_lock = " + str(kb.LS_lock) ,
		
		if (kb.btns_pressed[0] + kb.btns_pressed[1] + kb.btns_pressed[2] + kb.btns_pressed[3] + kb.btns_pressed[4]) > 0 : # if button is pressed, show prospective cursor

			# ====================================================================
			# get HID code and perform keyboard function with necessary modifiers
			# ====================================================================

			if (dir_idx > -1 and btn_idx > -1) or not char_str == "" : # if direction and button properly identified, or whitespace char_str has been assigned

				# Mechanism for changing character sets, using analog click (joyclick) + cardinal direction to change to new set (N=numsp,E=arrow,S=alpha,W=shift)

				if  btn_idx == 4 : # if Analog Stick click
					if not dir_idx == 0 : # if non-deadzone analog-click (i.e. with a direction)
						kb.last_arr_idx = dir_idx

						kb.reset_joystick_path()  # reset joystick path so we prevent white-space flicks when joystick resets to neutral
						kb.reset_modifiers() 	  # reset modifiers when you type a character (this will prevent ctrl and shift from being held though)
						kb.reset_modifier_locks() # always reset modifier_locks when switching directions

						hid = -1 # prevent typing

					else :	# if deadzone, so therefore directionless analog-click
						if not kb.last_arr_idx == 1 : # allows arrow and alpha sets to use Shift on the fly via Stick Keys, ignore 5 & 6
							if kb.depressed_analog_shift_modifier == 1:

								# 3-state toggle conditional logic

								if   kb.LS == 0 :
									kb.LS = 1 # turn left shift modifier on (for one character/function)
								elif kb.LS == 1 and kb.LS_lock == 1 :
									kb.LS = 0 # turn both left shift off 
									kb.LS_lock = 0  # and left shift modifier lock off 
								elif kb.LS == 1 :
									kb.LS_lock = 1 # turn left shift modifier lock on (for endless characters/functions)
								# print "in loop"

								kb.depressed_analog_shift_modifier = -1 # don't allow more toggling until analog-click is depressed, then re-pressed

							hid = -1 # prevent typing

				mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)

				# DEBUGGING Shift toggle via Analog Click (not for numbers, where analog click becomes 5 or 6)
				# print "\tmod_bit_str" + mod_bit_str ,

				if not hid == -1 :
	
					arr_idx = kb.last_arr_idx # Get array index for determining which set of character we are currently typing

					if char_str == "" : # if no white-space flick char_str assigned
						char_str = get_char_str(arr_idx, btn_idx, dir_idx)
	
					if get_Shift_Required(char_str) == 1 :
						kb.LS = 1 # turn left shift modifier on

					kb.last_hid = get_HID(char_str)

					kb.last_mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)

					# DEBUGGING final character set index (arr_idx), 2-character long key string, hid code, & modifier bit string 
					# print "\tarr_idx =" + str(arr_idx) + "\tchar_str = " + char_str + "\tHID = " + str(hid) + "\tmod_bit_str" + mod_bit_str ,

# ======================= CURSOR CHARACTER FUNCTIONALITY ====================================#

					# requires sending blank keypresses in between to avoid character repetition (but slow!)
					
					kb.iface.send_keys( int(kb.last_mod_bit_str,2), [kb.last_hid,0,0,0,0,0] ) # display char_cursor
					print "display char_cursor" ,
					kb.iface.send_keys( int("00000000",2), [0,0,0,0,0,0] ) # blank char_cursor
				
					kb.iface.send_keys( int("00000000",2), [42,0,0,0,0,0] ) # backspace char_cursor
					print "backspace char_cursor",
					kb.iface.send_keys( int("00000000",2), [0,0,0,0,0,0] ) # blank char_cursor
		
					kb.reset_joystick_path() # reset joystick path so we prevent white-space flicks when joystick resets to neutral
					#kb.reset_modifiers() # reset modifiers when you type a character (this will prevent ctrl and shift from being held though)
			else:
				kb.last_mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)
				
				kb.iface.send_keys( int(kb.last_mod_bit_str,2), [0,0,0,0,0,0] ) # send only any locked modifiers (for alt-tab, etc.)
		
		elif kb.last_hid != -1 :	
                        kb.iface.send_keys( int(kb.last_mod_bit_str,2), [kb.last_hid,0,0,0,0,0] )
                        print "typed char_cursor" ,
			kb.reset_btns_pressed()
			
			kb.last_mod_bit_str = "00000000"
			kb.last_hid = -1 # must display another char_cursor before we can type again

                        kb.reset_joystick_path() # reset joystick path so we prevent white-space flicks when joystick resets to neutral
                        kb.reset_modifiers() # reset modifiers when you type a character (this will prevent ctrl and shift from being held though)

		else :
			kb.iface.send_keys( int(kb.last_mod_bit_str,2), [0,0,0,0,0,0] ) # send only any locked modifiers (for alt-tab, etc.)
		
		kb.last_btn_idx = btn_idx
		kb.last_dir_idx = dir_idx

		print "\n" ,
