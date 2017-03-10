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

# =================
# Character Layout 
# =================

key_str_2_HID_code_and_shift_mod_required = {
	"Bk" : { "hid" :  0 , "shift" : 0 },	# Blank key, used to prevent repeating of previously pressed keys
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
	"LC" : { "hid" : 224, "shift" : 0 },	# Left Ctrl
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
	"LS" : { "hid" : 225, "shift" : 0 },	# Left Shift  
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
	"RS" : { "hid" : 229, "shift" : 0 },	# Right Shift
	"LA" : { "hid" : 226, "shift" : 0 },	# Left Alt
	"Se" : { "hid" : 44 , "shift" : 0 },	# Space
	#"KEY_CAPSLOCK" : 57,	# Don't really need if we have a joystick capsalpha set and separate numspecial set
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
	"RC" : { "hid" : 228, "shift" : 0 },	# Right Ctrl
	"RA" : { "hid" : 230, "shift" : 0 },	# Right Alt
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
	"Me" : { "hid" : 239, "shift" : 0 },	# Mute
	"VD" : { "hid" : 238, "shift" : 0 }, 	# Volume Down
	"VU" : { "hid" : 237, "shift" : 0 },	# Volume Up
	#"KEY_POWER" : 102,
	#"KEY_PAUSE" : 72,
	"LM" : { "hid" : 227, "shift" : 0 }, 	# Left Meta
	"RM" : { "hid" : 231, "shift" : 0 }, 	# Right Meta
	#"KEY_STOP" : 243,
	#"KEY_OPEN" : 116,
	#"KEY_BACK" : 241,
	#"KEY_FORWARD" : 242,
	#"KEY_NEXTSONG" : 235,
	"PP" : { "hid" : 232, "shift" : 0 }, # Play/Pause
	#"KEY_PREVIOUSSONG" : 234,
	#"KEY_STOPCD" : 233,
	#"KEY_REFRESH" : 250,
	#"KEY_SCROLLUP" : 245,
    	#"KEY_SCROLLDOWN" : 246,

    	# created to allow toggling Cursor-Mode
    	"CT" : { "hid" : -1, "shift" : 0 }, # Cursor toggle key, dummy entry
}

def get_HID(key_str):
    return key_str_2_HID_code_and_shift_mod_required[key_str]["hid"]

def get_Shift_Required(key_str):
    return key_str_2_HID_code_and_shift_mod_required[key_str]["shift"]

# Hardcoded key_str_2D arrays (which are then used to get HID codes + necessary modifiers) 
# are accessed via a combination of finger and direction, the joystick navigating between str_arrays

# [finger][direction], where finger = {L5=0, L4=1, L3=2, L2=3, L1=4, R1=5, R2=6, R3=7, R4=8, R5=9}
# and where direction = {neutral=0, north=1, east=2, south=3, west=4}, counting clockwise

# accessed via Joyclick-North, since numerical keys are located on top side of qwerty keyboard

left_numspecial_key_str_2D_array = np.array([
	["1_","!_",">_","=_","<_"],
	["2_","@_","Rt","+_","Lt"],
	["3_","#_","Up","-_","Dn"],
	["4_","$_",")_","%_","(_"],
	["5_", "" , "" , "" , "" ]],
	dtype="a2")

right_numspecial_key_str_2D_array = np.array([
	["0_","|_","}_","\\_","{_"],
	["9_","/_","Rt",";_","Lt"],
	["8_","*_","Dn",":_","Up"],
	["7_","&_","]_","^_","[_"],
	["6_", "" , "" , "" , "" ]],
	dtype="a2")

# accessed via Joyclick-East, since arrow keys are located on right side of qwerty keyboard

left_arrowfunc_key_str_2D_array = np.array([
	["F1","PU","Ed","PD","He"],
	["F2","Ee","Rt","11","Lt"],
	["F3","It","Up","12","Dn"],
	["F4","Up","Rt","Dn","Lt"],
	["F5", "" , "" , "" , "" ]],
	dtype="a2")
	
right_arrowfunc_key_str_2D_array = np.array([
	["10","PU","Ed","PD","He"],
	["F9","VU","Rt","VD","Lt"],
	["F8","PP","Dn","Me","Up"],
	["F7","Up","Rt","Dn","Lt"],
	["F6", "" , "" , "" , "" ]],
	dtype="a2")

# accessed via Joyclick-South, (default mode) since lowercase letters are located along the bottom of qwerty keyboard
	
left_loweralpha_key_str_2D_array = np.array([
	["a_","q_","'_","z_","`_"],
	["s_","w_","Rt","x_","Lt"],
	["e_","d_","Up","c_","Dn"],
	["t_","f_","r_","v_","g_"],
	["-_", "" , "" , "" , "" ]],
	dtype="a2")

right_loweralpha_key_str_2D_array = np.array([
	["p_","y_","/_","b_",";_"],
	["o_","l_","Rt","._","Lt"],
	["i_","k_","Dn",",_","Up"],
	["n_","u_","m_","j_","h_"],
	["__", "" , "" , "" , "" ]],
	dtype="a2")

# accessed via Joyclick-West, since Caps key is located on left side of qwerty keyboard
	
left_capsalpha_key_str_2D_array = np.array([
	["A_","Q_","\"_","Z_","~_"],
	["S_","W_","Rt","X_","Lt"],
	["E_","D_","Up","C_","Dn"],
	["T_","F_","R_","V_","G_"],
	["-_", "" , "" , "" , "" ]],
	dtype="a2")
	
right_capsalpha_key_str_2D_array = np.array([
	["P_","Y_","?_","B_",":_"],
	["O_","L_","Rt",">_","Lt"],
	["I_","K_","Dn","<_","Up"],
	["N_","U_","M_","J_","H_"],
	["__", "" , "" , "" , "" ]],
	dtype="a2")

def get_numspecial_key_str(btn_idx, dir_idx):
    if   hand == "left" :
    	return left_numspecial_key_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
	return right_numspecial_key_str_2D_array[btn_idx][dir_idx]

def get_arrowfunc_key_str(btn_idx, dir_idx):
    if   hand == "left" :
        return left_arrowfunc_key_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
        return right_arrowfunc_key_str_2D_array[btn_idx][dir_idx]
	
def get_loweralpha_key_str(btn_idx, dir_idx):
    if   hand == "left" :
    	return left_loweralpha_key_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
    	return right_loweralpha_key_str_2D_array[btn_idx][dir_idx]

def get_capsalpha_key_str(btn_idx, dir_idx):
    if   hand == "left" :
	return left_capsalpha_key_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
	return right_capsalpha_key_str_2D_array[btn_idx][dir_idx]

def get_key_str(arr_idx, btn_idx, dir_idx):
    if   arr_idx == 1 :
	return get_numspecial_key_str(btn_idx, dir_idx)
    elif arr_idx == 2 :
	return get_arrowfunc_key_str(btn_idx, dir_idx)
    elif arr_idx == 3 :
	return get_loweralpha_key_str(btn_idx, dir_idx)
    elif arr_idx == 4 :
	return get_capsalpha_key_str(btn_idx, dir_idx)
	

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

# ===============================
# Virtual Reality Keyboard Class
# ===============================

class VR_Keyboard():

	def __init__(self):

		#the structure for a bt keyboard input report (size is 10 bytes)

		#self.kb_state=[
		#	0xA1, #this is an input report
		#	0x01, #Usage report = Keyboard
		#	#Bit array for Modifier keys
		#	[0,	#Right GUI - Windows Key
		#	 0,	#Right ALT
		#	 0, #Right Shift
		#	 0, #Right Control
		#	 0,	#Left GUI
		#	 0, #Left ALT
		#	 0,	#Left Shift
		#	 0],#Left Control
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

		if device == "pi" :
 
			GPIO.setmode(GPIO.BOARD)

			self.btn2_pin = 33
			self.btn3_pin = 31
			self.btn4_pin = 35
			self.btn5_pin = 37

			GPIO.setup(self.btn2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # index finger
			GPIO.setup(self.btn3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # middle finger
			GPIO.setup(self.btn4_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # ring finger
			GPIO.setup(self.btn5_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # pinky finger

		elif device == "chip" : # https://github.com/xtacocorex/CHIP_IO for documentation

			self.btn2_pin = "GPIO2"
			self.btn3_pin = "GPIO3"
		    	self.btn4_pin = "GPIO4"
		    	#self.btn5_pin = "GPIO5" # doesn't seem to be working
			self.btn5_pin = "GPIO6"
			
		    	GPIO.setup(self.btn2_pin, GPIO.IN) # index finger
		    	GPIO.setup(self.btn3_pin, GPIO.IN) # middle finger
		    	GPIO.setup(self.btn4_pin, GPIO.IN) # ring finger
		    	GPIO.setup(self.btn5_pin, GPIO.IN) # pinky finger

		# Deprecated, left over code

		# Define sensor channels
		# (channels 3 to 7 unused)
		#self.swt_channel = 0
		#self.vrx_channel = 1
		#self.vry_channel = 2

		self.analog_dimension = 1024 	# based on 10 bit ADC (MPC3008)

		self.deadzone_width = 64 		# 2^7 / 2, (hardcoded)

		self.cursor_mode_on = 1 		# default to cursor mode on

		# Initialize "last" variables

		self.last_arr_idx = 3 	# default to loweralpha_key_str_2D_array, arr_idx = { 1=>numspecial, 2=>arrowfunc, 3=>loweralpha, 4=>capsalpha }
		self.last_dir_idx = -1
		self.last_mod_bit_str = "00000000"
		self.last_btns_state = [0,0,0,0,0]
		self.last_hid = -1

		self.reset_joystick_path_booleans()

		# modifier toggle in this 3-state manner: none -> once -> always (locked)
		
		self.mod_key_str_2_idx = { "RM" : 0, "RA" : 1, "RS" : 2, "RC" : 3, "LM" : 4, "LA" : 5, "LS" : 6, "LC" : 7 }
		self.mod_arr = [0,0,0,0,0,0,0,0]
		self.mod_lock_arr = [0,0,0,0,0,0,0,0]
		
		self.reset_non_locked_modifiers()
		self.reset_modifier_locks()

		# end of __init__	

	# Deprecated: forward keyboard events to the dbus service (deprecated, not used in this script, as we manually do so instead)
	def send_input(self):

		bin_str=""
		element=self.kb_state[2]
		for bit in element:
			bin_str += str(bit) # forms 8 char string which represents modifier(s), i.e. "00100000" is left shift

			self.iface.send_keys(int(bin_str,2),self.kb_state[4:10] )
		
	def reset_joystick_path_booleans(self):
		self.D2N = 0 # deadzone to north
		self.D2E = 0 # deadzone to east
		self.D2S = 0 # deadzone to south
		self.D2W = 0 # deadzone to west
		self.N2E = 0 # north to east
		self.N2W = 0 # north to west
		self.E2N = 0 # east to north
		self.E2S = 0 # east to south
		self.S2E = 0 # south to east
		self.S2W = 0 # south to west
		self.W2N = 0 # west to north
		self.W2S = 0 # west to south


	def reset_non_locked_modifiers(self):
		
		for i in range(0, len(self.mod_arr)) : # range(start,stop[,step]) generates all numbers up to but not including stop 
			if not self.mod_lock_arr[i] == 1 :
				self.mod_arr[i] = 0
		
	def reset_modifier_locks(self):

		for i in range(0, len(self.mod_lock_arr)) : # range(start,stop[,step]) generates all numbers up to but not including stop 
			self.mod_lock_arr[i] = 0


	def get_dir_idx(self):

		# read x and y potentiometer values
		xpos = ReadChannel(1)
		ypos = ReadChannel(2)

		#Center values at zero by subtracting 512
		xpos = xpos - ( self.analog_dimension / 2 )
		ypos = ypos - ( self.analog_dimension / 2 )

		# (hand prototype)rotate control stick 180 degrees if need be 
		# xpos = -xpos
		# ypos = -ypos

		# Determine dir_idx

		#if abs(xpos) < ( kb.deadzone_width / 2 ) and abs(ypos) < ( kb.deadzone_width / 2 ) : 	 # square deadzone
		if (xpos * xpos + ypos * ypos) < (self.deadzone_width / 2) * (self.deadzone_width / 2) : # circular deadzone
			self.direction_str = 'deadz'
			self.dir_idx = 0

			if   self.last_dir_idx == 1 :
				self.N2D = 1
			elif self.last_dir_idx == 2 :	
				self.E2D = 1
			elif self.last_dir_idx == 3 :	
				self.S2D = 1
			elif self.last_dir_idx == 4 :	
				self.W2D = 1	

		else :
			if    ypos >= abs(xpos) :

				self.direction_str = 'north'
				self.dir_idx = 1

				if   self.last_dir_idx == 0 :
					self.D2N = 1
				elif self.last_dir_idx == 2 :
					self.E2N = 1
				elif self.last_dir_idx == 4 :
					self.W2N = 1

			elif -ypos >= abs(xpos) :

				self.direction_str = 'south'
				self.dir_idx = 3

				if   self.last_dir_idx == 0 :
					self.D2S = 1
				elif self.last_dir_idx == 2 :
					self.E2S = 1
				elif self.last_dir_idx == 4 :
					self.W2S = 1

			elif  xpos >= abs(ypos) :

				self.direction_str = 'east_'
				self.dir_idx = 2

				if   self.last_dir_idx == 0 :
					self.D2E = 1
				elif self.last_dir_idx == 1 :
					self.N2E = 1
				elif self.last_dir_idx == 3 :
					self.S2E = 1

			elif -xpos >= abs(ypos) :

				self.direction_str = 'west_'
				self.dir_idx = 4

				if   self.last_dir_idx == 0 :
					self.D2W = 1
				elif self.last_dir_idx == 1 :
					self.N2W = 1
				elif self.last_dir_idx == 3 :
					self.S2W = 1

	def get_key_str_if_joystick_deadzone_cycle(self):

		num_CW_edges  = self.N2E + self.E2S + self.S2W + self.W2N # number of clockwise edges traveled along deadzone cycle
		num_CCW_edges = self.N2W + self.W2S + self.S2E + self.E2N # number of counter-clockwise edges traveled along deadzone cycle

		# Due to the imprecision of the ADC reading the joystick, there may be some noise which is causing the joystick
		# to cross the boundaries between Cardinal directions multiple times (depending on the polling speed as well)
		# Specifically, N->E and E->N seem to be entangled as well as N->W and W->N (The bottom edges seem to be okay atm)
		# In order to account for this, more experimenting with the kb.debug_joystick_cycle() function needs to be done...
		# In the meantime, we can use slightly less strict conditionals in order to achieve the same effect (their order is now important too!)
		
		if   num_CW_edges == 4 and num_CCW_edges == 4 : # both full counter-clockwise & full clockwise rotations
			self.key_str = "CT"	# Cursor Toggle
		elif num_CW_edges == 4 and num_CCW_edges <= 2 : # full clockwise rotation only
			self.key_str = "De"	# Delete
		elif num_CW_edges <= 2 and num_CCW_edges == 4 : # full counter-clockwise rotation only
			self.key_str = "Be"	# Backspace
		elif num_CW_edges == 2 and num_CCW_edges <= 1 : # clockwise half rotation only
			if   self.N2E and self.E2S : # eastern
				self.key_str = "RC"	# Right Ctrl
			elif self.E2S and self.S2W : # southern
				self.key_str = "RM"	# Right Meta
			elif self.S2W and self.W2N : # western
				self.key_str = "RA"	# Right Alt
			elif self.W2N and self.N2E : # northern
				self.key_str = "RS"	# Right Shift
		elif num_CW_edges <= 1 and num_CCW_edges == 2 : # counter-clockwise half rotation only
			if   self.N2W and self.W2S : # eastern
				self.key_str = "LC"	# Left Control
			elif self.W2S and self.S2E : # southern
				self.key_str = "LM"	# Left Meta
			elif self.S2E and self.E2N : # western
				self.key_str = "LA"	# Left Alt
			elif self.E2N and self.N2W : # northern
				self.key_str = "LS"	# Left Shift
		elif num_CW_edges == 0 and num_CCW_edges == 0 : # no joystick rotation at all, but check for joystick "flick"
			if   self.D2N : # Flick (north)
				self.key_str = "Bk" 	# Blank Key, used to prevent repeating of previously pressed White-space keys
			elif self.D2E : # Flick (east)
				self.key_str = "Er" 	# Enter
			elif self.D2S : # Flick (south)
				self.key_str = "Se"	# Space
			elif self.D2W : # Flick (west)
				self.key_str = "Tb"	# Tab

	def debug_joystick_cycle(self):

		print "{D2N,D2E,D2S,D2W} = [" + str(self.D2N) + str(self.D2E) + str(self.D2S) + str(self.D2W) + "], " ,
		print "{N2W,W2S,S2E,E2N} = [" + str(self.N2W) + str(self.W2S) + str(self.S2E) + str(self.E2N) + "], " ,
		print "{N2E,E2S,S2W,W2N} = [" + str(self.N2E) + str(self.E2S) + str(self.S2W) + str(self.W2N) + "], " ,  

	def get_btns_state(self):

		self.btns_state = [0,0,0,0,0]
		self.btns_state[0] = GPIO.input(self.btn5_pin)	# off = 0, on = 1
		self.btns_state[1] = GPIO.input(self.btn4_pin)	# off = 0, on = 1
		self.btns_state[2] = GPIO.input(self.btn3_pin)	# off = 0, on = 1
		self.btns_state[3] = GPIO.input(self.btn2_pin) 	# off = 0, on = 1
		self.btns_state[4] = int( not bool(ReadChannel(0)) ) 	# off = ~1024 , on = 0 (we transform this to 0 off and 1 on)

		self.num_btns_pressed = sum(self.btns_state)
	
	def get_mod_bit_str(self):

		return ''.join( str(x) for x in self.mod_arr )

	def debug_modifer_toggles(self):

		print "\tmod_bit_str=" + self.get_mod_bit_str() ,
		print "\tmod_lock_bit_str=" + ''.join( str(x) for x in self.mod_lock_arr ) ,

	def toggle_modifer(self):

		i = self.mod_key_str_2_idx[self.key_str]

		# 3-state toggle conditional logic

		if   self.mod_arr[i] == 0 :

			self.mod_arr[i] = 1 # turn modifier on (turns off after typing a single character/function key)

		elif self.mod_arr[i] == 1 and self.mod_lock_arr[i] == 1 :

			self.mod_arr[i] = 0 # turn both left ctrl off 
			self.mod_lock_arr[i] = 0  # and modifier lock off 

		elif self.mod_arr[i] == 1 :

			self.mod_lock_arr[i] = 1 # turn modifier lock on (stays on for all subsequent character/function keys)

	def debug_selected_key(self):

		print "\tarr_idx =" + str(self.last_arr_idx) + "\tkey_str = " + self.key_str + "\tmod_bit_str" + self.get_mod_bit_str() ,

	def activate_shift_mod_if_required_for_key_str(self):
		
		if get_Shift_Required(self.key_str) == 1 :
			if hand == "left" :
				self.mod_arr[self.mod_key_str_2_idx["LS"]] = 1 # turn left shift modifier on
			elif hand == "right" : 
				self.mod_arr[self.mod_key_str_2_idx["RS"]] = 1 # turn right shift modifier on
		
	def type_hid_code_from_key_str(self):
		
		#self.debug_selected_key()
		
		if not self.key_str == "" : # Extra precaution in the event that a "" key_str slips by (like with changing characters sets)
			
			self.activate_shift_mod_if_required_for_key_str()

			self.iface.send_keys( int(self.get_mod_bit_str(),2), [get_HID(self.key_str),0,0,0,0,0] )

			self.reset_non_locked_modifiers()
			self.reset_joystick_path_booleans() # reset joystick path to prevent new joystick cycles as it resets to deadzone

	def flash_char_cursor_from_key_str(self):
		
		#self.debug_selected_key()
		
		if not self.key_str == "" : # Extra precaution in the event that a "" key_str slips by (like with changing characters sets)
		
			self.current_char_cursor_key_str = self.key_str # store for when we type by releasing button (repeating is not possible)
			
			self.activate_shift_mod_if_required_for_key_str()

			# this (in it's current state, can be definitely be optimized) requires sending blank keypresses in between to avoid character repetition (but slow!)

			self.iface.send_keys( int(self.get_mod_bit_str(),2), [get_HID(self.key_str),0,0,0,0,0] ) # display char_cursor
			self.iface.send_keys( 0, [0,0,0,0,0,0] ) # blank char_cursor to stop or "lift" previous key
			time.sleep(0.25) # wait for a 1/4 of a second before deleting flashed character

			self.iface.send_keys( 0, [get_HID("Be"),0,0,0,0,0] ) # backspace char_cursor
			self.iface.send_keys( 0, [0,0,0,0,0,0] ) # blank char_cursor to stop or "lift" previous key
			time.sleep(0.25) # wait for a 1/4 of a second before continuing 

if __name__ == "__main__":

	kb = VR_Keyboard()
	
	print "Running VR Bluetooth Keyboard"

	while True: # main while loop

		kb.key_str = ""

		kb.get_dir_idx()

		if kb.dir_idx == 0 : # if at deadzone, check if any whitespace characters, modifiers, or Bksp or Del were entered
		
			kb.get_key_str_if_joystick_deadzone_cycle() 
			
		#kb.debug_joystick_cycle()
		#kb.debug_modifer_toggles()
		#print "\n"

		if   kb.key_str == "CT" : # Cursor Toggle, input from the combination of full counter-clockwise and full clockwise rotations

			kb.cursor_mode_on = int (not kb.cursor_mode_on) # toggle "Cursor Mode" on or off
			kb.reset_joystick_path_booleans() # reset joystick path to prevent new joystick cycles as it resets to deadzone
			kb.reset_non_locked_modifiers() # reset non-locked modifiers when you toggle Cursor Mode
			continue
			
		elif kb.key_str in kb.mod_key_str_2_idx :
		
			kb.toggle_modifer()
			kb.reset_joystick_path_booleans()
			continue

		kb.get_btns_state()

						    # range(start,stop[,step]) generates all numbers up to but not including stop
		if kb.btns_state[4] and kb.dir_idx in range(1,5) : # Joy-stick Click + direction = character set swap, no typing here

			kb.last_arr_idx = kb.dir_idx
			kb.last_dir_idx = -1 # reset after a character swap
			kb.last_btns_state = kb.btns_state 

			kb.reset_joystick_path_booleans()  # reset joystick path to prevent new joystick cycles as it resets to deadzone
			kb.reset_non_locked_modifiers()  # reset non-locked modifiers when you type a character
			kb.reset_modifier_locks() # always reset modifier_locks when switching directions
			
			continue

		# 7 scenarios: 0, 1, or 2 buttons pressed (with cursor mode either on or off), or the blank character (typed only once to stop repeating characters)

		if kb.num_btns_pressed == 0 and kb.key_str == "" : # Nothing pressed, no Joy-stick cycle, no key_str recorded yet

			if not kb.btns_state == kb.last_btns_state : # we only (type and) send blank key once! (so as not to slow down code with excess BT latency)
			
				if kb.cursor_mode_on :
					
					kb.key_str = kb.current_char_cursor_key_str # since typing function uses self.key_str
					kb.current_char_cursor_key_str = "" # reset for next cursor char
					kb.type_hid_code_from_key_str() # Having let go of all buttons, we type the last cursor character
				
				kb.iface.send_keys( 0, [0,0,0,0,0,0] ) # blank key

		elif kb.num_btns_pressed == 0 and not kb.key_str == "" : # Joy-stick cycle therefore a key_str was found (Cursor mode doesn't apply! must be memorized)

			kb.type_hid_code_from_key_str()

		elif kb.num_btns_pressed == 1 : # button pressed, find hid code

			btn_idx = -1; # we need to find the non-zero index of kb.btns_state

			for i in range(0,len(kb.btns_state)-1) : # This can be replaced with a faster numpy method perhaps later, but for 5 elements it probably doesn't matter
				
				if kb.btns_state[i] :
					
					btn_idx = i
					break

			kb.key_str = get_key_str(kb.last_arr_idx, btn_idx, kb.dir_idx)

			if kb.cursor_mode_on :

				kb.flash_char_cursor_from_key_str() # if key_str corresponds to a character

			else : # cursor mode is off, repeated characters allowed
				
				if not kb.last_btns_state == kb.btns_state : # don't repeatedly send same hid code (only need it once to "hold" key down, it's only lifted via "blank" key)

					kb.type_hid_code_from_key_str()
            
		elif kb.num_btns_pressed == 2 :

			continue

			# Cascaded typing, to be done later 

			#if kb.cursor_mode_on :

				# to be coded

			#else : # cursor mode is off, repeated characters allowed

				# to be coded

		else : # kb.num_btns_pressed > 2 will run into problems with BT latency (it's impossible to know which of the 2nd and 3rd pressed buttons was pressed first)

			continue # to be coded
		
		kb.last_dir_idx = kb.dir_idx
		kb.last_btns_state = kb.btns_state

		#print "\n" ,
