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
	["1_","=_",")_","#_","(_"],
	["2_","-_","Rt","$_","Lt"],
	["3_","+_","Up","%_","Dn"],
	["4_","*_","]_","^_","[_"],
	["5_", "" , "" , "" , "" ]],
	dtype="a2")

right_numspecial_key_str_2D_array = np.array([
	["0_","\\_","{_","/_","}_"],
	["9_","&_","Rt","|_","Lt"],
	["8_","@_","Dn",";_","Up"],
	["7_","!_","<_",":_",">_"],
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
	["-_", "" , "" , "" , "" ]],
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
	["-_", "" , "" , "" , "" ]],
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
		    	self.btn5_pin = "GPIO5"

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
		
		self.joystick_cycle_non_modifier_keys_arr = ["Se", "Er", "__", "Tb", "Be", "De"]

		self.reset_joystick_path_booleans()

		# modifier toggle in this 3-state manner: none -> once -> always (locked)
		
		self.mod_key_str_2_idx = { "RM" : 0, "RA" : 1, "RS" : 2, "RC" : 3, "LM" : 4, "LA" : 5, "LS" : 6, "LC" : 7 }
		self.mod_arr = [0,0,0,0,0,0,0,0]
		self.mod_lock_arr = [0,0,0,0,0,0,0,0]
		
		self.reset_modifiers()
		self.reset_modifier_locks()

		# end of __init__	
		
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

	def reset_modifier_locks(self):

		# mod_lock_arr == {RM_lock, RA_lock, RS_lock, RC_lock, LM_lock, LA_lock, LS_lock, LC_lock} = {0,0,0,0,0,0,0,0} 

		for i in range(0, len(self.mod_lock_arr)) :
			self.mod_lock_arr[i] = 0

	def reset_modifiers(self):

		# mod_arr == {RM, RA, RS, RC, LM, LA, LS, LC} = {0,0,0,0,0,0,0,0} 

		for i in range(0, len(self.mod_arr)) :
			if not self.mod_lock_arr[i] == 1 :
				self.mod_arr[i] = 0

	# Deprecated: forward keyboard events to the dbus service (deprecated, not used in this script, as we manually do so instead)
	def send_input(self):

		bin_str=""
		element=self.kb_state[2]
		for bit in element:
			bin_str += str(bit) # forms 8 char string which represents modifier(s), i.e. "00100000" is left shift

			self.iface.send_keys(int(bin_str,2),self.kb_state[4:10] )

# subroutines in main 

def get_dir_idx(kb):

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

	#if abs(xpos) < ( kb.deadzone_width / 2 ) and abs(ypos) < ( kb.deadzone_width / 2 ) : 	# square deadzone
	if (xpos * xpos + ypos * ypos) < kb.deadzone_width * kb.deadzone_width / 4 : 			# circular deadzone
		kb.direction_str = 'deadz'
		kb.dir_idx = 0

		if   kb.last_dir_idx == 1 :
			kb.N2D = 1
		elif kb.last_dir_idx == 2 :	
			kb.E2D = 1
		elif kb.last_dir_idx == 3 :	
			kb.S2D = 1
		elif kb.last_dir_idx == 4 :	
			kb.W2D = 1	

	else :
		if ypos >= abs(xpos) :

			kb.direction_str = 'north'
			kb.dir_idx = 1

			if   kb.last_dir_idx == 0 :
				kb.D2N = 1
			elif kb.last_dir_idx == 2 :
				kb.E2N = 1
			elif kb.last_dir_idx == 4 :
				kb.W2N = 1

		if ypos <= -abs(xpos) :

			kb.direction_str = 'south'
			kb.dir_idx = 3

			if   kb.last_dir_idx == 0 :
				kb.D2S = 1
			elif kb.last_dir_idx == 2 :
				kb.E2S = 1
			elif kb.last_dir_idx == 4 :
				kb.W2S = 1

		if xpos > abs(ypos) :

			kb.direction_str = 'east_'
			kb.dir_idx = 2

			if   kb.last_dir_idx == 0 :
				kb.D2E = 1
			elif kb.last_dir_idx == 1 :
				kb.N2E = 1
			elif kb.last_dir_idx == 3 :
				kb.S2E = 1

		if xpos < -abs(ypos) :

			kb.direction_str = 'west_'
			kb.dir_idx = 4

			if   kb.last_dir_idx == 0 :
				kb.D2W = 1
			elif kb.last_dir_idx == 1 :
				kb.N2W = 1
			elif kb.last_dir_idx == 3 :
				kb.S2W = 1

	return kb

def get_key_str_if_joystick_cycle(kb):

	if kb.dir_idx == 0 : # if at deadzone, check if any whitespace characters or Bksp or Del were entered

		# 2-edge long simple cycles: White-space (and underscore) characters

		if not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N or kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # no rotation whatsoever
			
			if   kb.D2N : # Flick (north)

				kb.key_str = "Se" 	# Space

			elif kb.D2E : # Flick (east)

				kb.key_str = "Er" 	# Enter

			elif kb.D2S : # Flick (south)

				kb.key_str = "__"	# Underscore

			elif kb.D2W : # Flick (west)

				kb.key_str = "Tb"	# Tab

		else : # some amount of rotation
			
			if   kb.N2E * kb.E2S * kb.S2W * kb.W2N * kb.N2W * kb.W2S * kb.S2E * kb.E2N : # full counter-clockwise rotation & full clockwise rotation

				kb.key_str = "CT"	# Cursor Toggle

			elif kb.N2E * kb.E2S * kb.S2W * kb.W2N and not ( kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # full clockwise rotation only

				kb.key_str = "De"	# Delete

			elif kb.N2W * kb.W2S * kb.S2E * kb.E2N and not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N ) : # full counter-clockwise rotation only

				kb.key_str = "Be"	# Backspace

			elif kb.N2E * kb.E2S and not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N ) : # clockwise half rotation (east) only

				kb.key_str = "RC"	# Right Ctrl

			elif kb.E2S * kb.S2W and not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N ) : # clockwise half rotation (south) only

				kb.key_str = "RM"	# Right Meta

			elif kb.S2W * kb.W2N and not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N ) : # clockwise half rotation (west) only

				kb.key_str = "RA"	# Right Alt

			elif kb.W2N * kb.N2E and not ( kb.N2W or kb.W2S or kb.S2E or kb.E2N ) : # clockwise half rotation (north) only

				kb.key_str = "RS"	# Right Shift

			elif kb.N2W * kb.W2S and not ( kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # counter-clockwise half rotation (west) only

				kb.key_str = "LC"	# Left Control

			elif kb.W2S * kb.S2E and not ( kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # counter-clockwise half rotation (south) only

				kb.key_str = "LM"	# Left Meta

			elif kb.S2E * kb.E2N and not ( kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # counter-clockwise half rotation (east) only

				kb.key_str = "LA"	# Left Alt

			elif kb.E2N * kb.N2W and not ( kb.N2E or kb.E2S or kb.S2W or kb.W2N ) : # counter-clockwise half rotation (north) only

				kb.key_str = "LS"	# Left Shift

		# Don't reset joystick path for Whitespace Char & Backspace/Delete, thereby repeatedly typing these characters until the Joystick leaves deadzone again (or another button is pressed)
		if not kb.key_str in joystick_cycle_non_modifier_keys_arr : 
			kb = reset_joystick_path_booleans(kb)

	return kb

def debug_joystick_cycle(kb):

	print "{D2N,D2E,D2S,D2W} = [" + str(kb.D2N) + str(kb.D2E) + str(kb.D2S) + str(kb.D2W) + "], " ,
	print "{N2D,E2D,S2D,W2D} = [" + str(kb.N2D) + str(kb.E2D) + str(kb.S2D) + str(kb.W2D) + "], " ,
	print "{N2W,W2S,S2E,E2N} = [" + str(kb.N2W) + str(kb.W2S) + str(kb.S2E) + str(kb.E2N) + "], " ,
	print "{N2E,E2S,S2W,W2N} = [" + str(kb.N2E) + str(kb.E2S) + str(kb.S2W) + str(kb.W2N) + "], " ,  

def get_btns_state(kb):

	kb.btns_state[0] = ReadChannel(0)			# off = ~1024 , on = 0
	kb.btns_state[1] = GPIO.input(kb.btn2_pin)	# off = 0, on = 1
	kb.btns_state[2] = GPIO.input(kb.btn3_pin)	# off = 0, on = 1
	kb.btns_state[3] = GPIO.input(kb.btn4_pin)	# off = 0, on = 1
    	kb.btns_state[4] = GPIO.input(kb.btn5_pin)	# off = 0, on = 1
	
	kb.num_btns_pressed = sum(kb.btns_state)

	return kb

def get_mod_bit_str(kb):

	return ''.join( str(x) for x in kb.mod_arr )

def debug_modifer_toggles(kb):

	print "\tmod_bit_str=" + get_mod_bit_str(kb) ,
	print "\tmod_lock_bit_str=" + ''.join( str(x) for x in kb.mod_lock_arr ) ,

def toggle_modifer(kb):

	i = mod_key_str_2_idx[kb.key_str]

	# 3-state toggle conditional logic

	if   kb.mod_arr[i] == 0 :

		kb.mod_arr[i] = 1 # turn modifier on (turns off after typing a single character/function key)

	elif kb.mod_arr[i] == 1 and kb.mod_lock_arr[i] == 1 :

		kb.mod_arr[i] = 0 # turn both left ctrl off 
		kb.mod_lock_arr[i] = 0  # and modifier lock off 

	elif kb.mod_arr[i] == 1 :

		kb.mod_lock_arr[i] = 1 # turn modifier lock on (stays on for all subsequent character/function keys)

	return kb

def debug_selected_key(kb):

	print "\tarr_idx =" + str(kb.last_arr_idx) + "\tkey_str = " + kb.key_str + "\tHID = " + str(kb.hid) + "\tmod_bit_str" + get_mod_bit_str(kb) ,

def type_hid_code_from_key_str(kb):

	if get_Shift_Required(key_str) == 1 :
		if hand == "left" :
			kb.mod_arr[kb.mod_key_str_2_idx["LS"]] = 1 # turn left shift modifier on
		elif hand == "right" : 
			kb.mod_arr[kb.mod_key_str_2_idx["RS"]] = 1 # turn right shift modifier on

	#debug_selected_key(kb)

	kb.iface.send_keys( int(get_mod_bit_str(kb),2), [get_HID(kb.key_str),0,0,0,0,0] )


def flash_char_cursor_from_key_str(kb):

	if get_Shift_Required(key_str) == 1 :
		if hand == "left" :
			kb.mod_arr[kb.mod_key_str_2_idx["LS"]] = 1 # turn left shift modifier on
		elif hand == "right" : 
			kb.mod_arr[kb.mod_key_str_2_idx["RS"]] = 1 # turn right shift modifier on

	# this (in it's current state, can be definitely be optimized) requires sending blank keypresses in between to avoid character repetition (but slow!)
	
	#print "display char_cursor" ,
	kb.iface.send_keys( int(get_mod_bit_str(kb),2), [get_HID(kb.key_str),0,0,0,0,0] ) # display char_cursor
	kb.iface.send_keys( int("00000000",2), [0,0,0,0,0,0] ) # blank char_cursor to stop "lift" previous key
	
	#print "backspace char_cursor",
	kb.iface.send_keys( int("00000000",2), [42,0,0,0,0,0] ) # backspace char_cursor
	kb.iface.send_keys( int("00000000",2), [0,0,0,0,0,0] ) # blank char_cursor to stop "lift" previous key

# main

if __name__ == "__main__":

	print "Running up VR Bluetooth Keyboard"

	kb = VR_Keyboard()

	while True: # main while loop

		# reset/initialize dir_idx, key_str, and hid every loop

		kb.dir_idx = -1
		kb.key_str = ""
		kb.hid = 0	# default to blank character

		kb = get_dir_idx(kb)

		kb = get_key_str_if_joystick_simple_cycle(kb) 

		if kb.key_str == "CT" :	# Cursor Toggle, input from the combination of full counter-clockwise and full clockwise rotations

			kb.cursor_mode_on = int (not kb.cursor_mode_on) # toggle Cursor Mode on or off
			break

		#debug_joystick_simple_cycle(kb)
		#debug_modifer_toggles(kb)

		kb = get_btns_state(kb)


		if kb.btns_state[0] and kb.dir_idx in range(1,4) : # Joy-stick Click + direction = character set swap, no typing here

			kb.last_arr_idx = kb.dir_idx
			kb.last_dir_idx = -1 # reset after a character swap
			kb.last_btns_state = kb.btns_state 

			kb.reset_joystick_path()  # reset joystick path so we prevent joystick cycles when resets to neutral
			kb.reset_modifier_locks() # always reset modifier_locks when switching directions
			kb.reset_non_locked_modifiers()  # reset non-locked modifiers when you type a character
			
			break

		# 7 scenarios: 0, 1, or 2 buttons pressed (with cursor mode either on or off), or the blank character (typed only once to stop repeating characters)

		if kb.num_btns_pressed == 0 and kb.key_str == "" : # Nothing pressed, no Joy-stick cycle, no key_str recorded

			if not kb.btns_state == kb.last_btns_state : # we only send blank key once! (so as not to slow down code with excess BT latency)

				kb.iface.send_keys( 0, [0,0,0,0,0,0] ) # blank key, MAY NOT HAVE TO INCLUDE MOD

		elif kb.num_btns_pressed == 0 and not kb.key_str == "" : # Joy-stick cycle therefore a key_str was found (Cursor mode doesn't apply! must be memorized)

			kb = type_hid_code_from_key_str(kb)

			kb.reset_joystick_path()
			kb.reset_non_locked_modifiers() # reset non-locked modifiers whenever you type a character

		elif kb.num_btns_pressed == 1 : # button pressed, find hid code

			btn_idx = -1; # we need to find the non-zero index of kb.btns_state

			for i in range(0,len(kb.btns_state)) : # This can be replaced with a faster numpy method perhaps later, but for 5 elements it probably doesn't matter
				if kb.btns_state[i] :
					btn_idx = i

			kb.key_str = get_key_str(kb.last_arr_idx, btn_idx, kb.dir_idx)

			if cursor_mode_on :

				flash_char_cursor_from_key_str(kb) # if key_str corresponds to a character

				kb.reset_non_locked_modifiers() # reset non-locked modifiers whenever you type a character

			else : # cursor mode is off, repeated characters allowed

				kb = type_hid_code_from_key_str(kb)

        		kb.reset_joystick_path() # reset joystick path so we prevent white-space flicks when joystick resets to deadzone from cardinal direction
            
		elif kb.num_btns_pressed == 2 :

			break

			# Cascaded typing, to be done later

			#if cursor_mode_on :

				# to be coded

			#else : # cursor mode is off, repeated characters allowed

				# to be coded

		else : # kb.num_btns_pressed > 2 will run into problems with BT latency (it's impossible to know which of the 2nd and 3rd pressed buttons was pressed first)

			break # to be coded
		
		kb.last_dir_idx = kb.dir_idx
		kb.last_btns_state = kb.btns_state

		#print "\n" ,
