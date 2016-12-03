# -*- coding: utf8 -*-

#!/usr/bin/python
#
# Adapted from www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
#

import RPi.GPIO as GPIO  #to use the GPIO pins
import spidev   #to use joystick
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import os
#import vr_keytable_left_and_right
import numpy as np

char_str_2_HID_code = {		
	"Ee" : 41, 	# Escape			
	"1_" : 30,
	"!_" : 30, 	# requires Shift Modkey			
	"2_" : 31,
	"@_" : 31, 	# requires Shift Modkey	
	"3_" : 32,
	"#_" : 32, 	# requires Shift Modkey			
	"4_" : 33,
	"$_" : 33, 	# requires Shift Modkey
	"5_" : 34,
	"%_" : 34, 	# requires Shift Modkey
	"6_" : 35,
	"^_" : 35, 	# requires Shift Modkey
	"7_" : 36,
	"&_" : 36, 	# requires Shift Modkey
	"8_" : 37,
	"*_" : 37, 	# requires Shift Modkey
	"9_" : 38,
	"(_" : 38, 	# requires Shift Modkey
	"0_" : 39,
	")_" : 39, 	# requires Shift Modkey			
	"-_" : 45, 
	"__" : 45, 	# requires Shift Modkey
	"=_" : 46,
	"+_" : 46,	# requires Shift Modkey
	"Be" : 42,	# Backspace
	"Tb" : 43,	# Tab
	"UT" : 43,	# Un-Tab, requires Shift Modkey
	"q_" : 20,
	"Q_" : 20,	# requires Shift Modkey
	"w_" : 26,	
	"W_" : 26,	# requires Shift Modkey
	"e_" : 8,
	"E_" : 8,	# requires Shift Modkey
	"r_" : 21,
	"R_" : 21,	# requires Shift Modkey
	"t_" : 23,
	"T_" : 23,	# requires Shift Modkey
	"y_" : 28,
	"Y_" : 28,	# requires Shift Modkey
	"u_" : 24,
	"U_" : 24,	# requires Shift Modkey
	"i_" : 12,
	"I_" : 12,	# requires Shift Modkey
	"o_" : 18,
	"O_" : 18,	# requires Shift Modkey
	"p_" : 19,
	"P_" : 19,	# requires Shift Modkey
	"[_" : 47,
	"{_" : 47,	# requires Shift Modkey
	"]_" : 48,
	"}_" : 48,	# requires Shift Modkey
	"Er" : 40,	# Enter/Return
	#"KEY_LEFTCONTROL" : 224,	# Left Control, ================== Control ============
	"a_" : 4,
	"A_" : 4,	# requires Shift Modkey
	"s_" : 22,
	"S_" : 22,	# requires Shift Modkey
	"d_" : 7,
	"D_" : 7,	# requires Shift Modkey
	"f_" : 9,
	"F_" : 9,	# requires Shift Modkey
	"g_" : 10,
	"G_" : 10,	# requires Shift Modkey
	"h_" : 11,
	"H_" : 11,	# requires Shift Modkey
	"j_" : 13,
	"J_" : 13,	# requires Shift Modkey
	"k_" : 14,
	"K_" : 14,	# requires Shift Modkey
	"l_" : 15,
	"L_" : 15,	# requires Shift Modkey
	";_" : 51,
	":_" : 51,	# requires Shift Modkey
	"'_" : 52,	# Apostrophe
	"\"_" : 52,  	# Double quotes, requires Shift Modkey
	"`_" : 53,	# Grave
	"~_" : 53,	# requires Shift Modkey
	#"KEY_LEFTSHIFT" : 225,	# No Shift key, using Joystick set ============= SHIFT ==========  
	"\\_" : 50,	# Backslash	
	"|_" : 50, 	# Vertical Bar, requires Shift Modkey
	"z_" : 29,
	"Z_" : 29,	# requires Shift Modkey
	"x_" : 27,
	"X_" : 27,	# requires Shift Modkey
	"c_" : 6,
	"C_" : 6,	# requires Shift Modkey
	"v_" : 25,
	"V_" : 25,	# requires Shift Modkey
	"b_" : 5,
	"B_" : 5,	# requires Shift Modkey
	"n_" : 17,
	"N_" : 17,	# requires Shift Modkey
	"m_" : 16,
	"M_" : 16,	# requires Shift Modkey
	",_" : 54,
	"<_" : 54,	# Less than, requires Shift Modkey
	"._" : 55,
	">_" : 55,	# requires Shift Modkey
	"/_" : 56,
	"?_" : 56, # requires Shift Modkey
	#"KEY_RIGHTSHIFT" : 229,
	# "AT" : 226,	# Left Alt, we really only need one Alt  # ===============ALT========
	"Se" : 44,	# Space
	#"KEY_CAPSLOCK" : 57,	# Don't really need if we have a joystic-Shift set
	"F1" : 58,
	"F2" : 59,
	"F3" : 60,
	"F4" : 61,
	"F5" : 62,
	"F6" : 63,
	"F7" : 64,
	"F8" : 65,
	"F9" : 66,
	"10" : 67,	# F10
	"11" : 68,	# F11
	"12" : 69,	# F12
	#"KEY_RIGHTCTRL" : 228,
	#"KEY_RIGHTALT" : 230,
	"He" : 74,	# Home
	"Up" : 82,	# Up
	"PU" : 75,	# Page Up
	"Lt" : 80,	# Left
	"Rt" : 79,	# Right
	"Ed" : 77,	# End
	"Dn" : 81,	# Down
	"PD" : 78,	# Page Down
	"It" : 73,	# Insert
	"De" : 76,	# Delete
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

char_str_requires_shift_mod = {		
	"Ee" : 0, 	# Escape			
	"1_" : 0,
	"!_" : 1, 	# requires Shift Modkey			
	"2_" : 0,
	"@_" : 1, 	# requires Shift Modkey	
	"3_" : 0,
	"#_" : 1, 	# requires Shift Modkey			
	"4_" : 0,
	"$_" : 1, 	# requires Shift Modkey
	"5_" : 0,
	"%_" : 1, 	# requires Shift Modkey
	"6_" : 0,
	"^_" : 1, 	# requires Shift Modkey
	"7_" : 0,
	"&_" : 1, 	# requires Shift Modkey
	"8_" : 0,
	"*_" : 1, 	# requires Shift Modkey
	"9_" : 0,
	"(_" : 1, 	# requires Shift Modkey
	"0_" : 0,
	")_" : 1, 	# requires Shift Modkey			
	"-_" : 0, 
	"__" : 1, 	# requires Shift Modkey
	"=_" : 0,
	"+_" : 1,	# requires Shift Modkey
	"Be" : 0,	# Backspace
	"Tb" : 0,	# Tab
	"UT" : 1,	# Un-Tab, requires Shift Modkey
	"q_" : 0,
	"Q_" : 1,	# requires Shift Modkey
	"w_" : 0,	
	"W_" : 1,	# requires Shift Modkey
	"e_" : 0,
	"E_" : 1,	# requires Shift Modkey
	"r_" : 0,
	"R_" : 1,	# requires Shift Modkey
	"t_" : 0,
	"T_" : 1,	# requires Shift Modkey
	"y_" : 0,
	"Y_" : 1,	# requires Shift Modkey
	"u_" : 0,
	"U_" : 1,	# requires Shift Modkey
	"i_" : 0,
	"I_" : 1,	# requires Shift Modkey
	"o_" : 0,
	"O_" : 1,	# requires Shift Modkey
	"p_" : 0,
	"P_" : 1,	# requires Shift Modkey
	"[_" : 0,
	"{_" : 1,	# requires Shift Modkey
	"]_" : 0,
	"}_" : 1,	# requires Shift Modkey
	"Er" : 0,	# Enter/Return
	#"KEY_LEFTCONTROL" : 224,	# Left Control, ================== Control ============
	"a_" : 0,
	"A_" : 1,	# requires Shift Modkey
	"s_" : 0,
	"S_" : 1,	# requires Shift Modkey
	"d_" : 0,
	"D_" : 1,	# requires Shift Modkey
	"f_" : 0,
	"F_" : 1,	# requires Shift Modkey
	"g_" : 0,
	"G_" : 1,	# requires Shift Modkey
	"h_" : 0,
	"H_" : 1,	# requires Shift Modkey
	"j_" : 0,
	"J_" : 1,	# requires Shift Modkey
	"k_" : 0,
	"K_" : 1,	# requires Shift Modkey
	"l_" : 0,
	"L_" : 1,	# requires Shift Modkey
	";_" : 0,
	":_" : 1,	# requires Shift Modkey
	"'_" : 0,	# Apostrophe
	"\"_" : 1,  	# Double quotes, requires Shift Modkey
	"`_" : 0,	# Grave
	"~_" : 1,	# requires Shift Modkey
	#"KEY_LEFTSHIFT" : 0,	# No Shift key, using Joystick set ============= SHIFT ==========  
	"\\_" : 0,	# Backslash	
	"|_" : 1, 	# Vertical Bar, requires Shift Modkey
	"z_" : 0,
	"Z_" : 1,	# requires Shift Modkey
	"x_" : 0,
	"X_" : 1,	# requires Shift Modkey
	"c_" : 0,
	"C_" : 1,	# requires Shift Modkey
	"v_" : 0,
	"V_" : 1,	# requires Shift Modkey
	"b_" : 0,
	"B_" : 1,	# requires Shift Modkey
	"n_" : 0,
	"N_" : 1,	# requires Shift Modkey
	"m_" : 0,
	"M_" : 1,	# requires Shift Modkey
	",_" : 0,
	"<_" : 1,	# Less than, requires Shift Modkey
	"._" : 0,
	">_" : 1,	# requires Shift Modkey
	"/_" : 0,
	"?_" : 1, # requires Shift Modkey
	#"KEY_RIGHTSHIFT" : 0,
	# "AT" : 0,	# Left Alt, we really only need one Alt  # ===============ALT========
	"Se" : 0,	# Space
	#"KEY_CAPSLOCK" : 0,	# Don't really need if we have a joystic-Shift set
	"F1" : 0,
	"F2" : 0,
	"F3" : 0,
	"F4" : 0,
	"F5" : 0,
	"F6" : 0,
	"F7" : 0,
	"F8" : 0,
	"F9" : 0,
	"10" : 0,	# F10
	"11" : 0,	# F11
	"12" : 0,	# F12
	#"KEY_RIGHTCTRL" : 0,
	#"KEY_RIGHTALT" : 0,
	"He" : 0,	# Home
	"Up" : 0,	# Up
	"PU" : 0,	# Page Up
	"Lt" : 0,	# Left
	"Rt" : 0,	# Right
	"Ed" : 0,	# End
	"Dn" : 0,	# Down
	"PD" : 0,	# Page Down
	"It" : 0,	# Insert
	"De" : 0,	# Delete
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

# accessed via Joyclick-North, since Number keys are on top side of qwerty keyboard
numspecial_str_2D_array = np.array([
	["1_","=_",")_","#_","(_"],
	["2_","-_","It","$_","Ee"],
	["3_","+_","Be","%_","De"],
	["4_","*_","]_","^_","[_"],
	["5_","__","__","__","__"],
	["6_","__","__","__","__"],
	["7_","!_","}_","/_","{_"],
	["8_","@_","It","\\_","Ee"],
	["9_","&_","Be","|_","De"],
	["0_",":_",">_",";_","<_"]],
	dtype="a2"
	)

left_numspecial_str_2D_array = np.array([
	["1_","=_",")_","#_","(_"],
	["2_","-_","It","$_","Ee"],
	["3_","+_","Be","%_","De"],
	["4_","*_","]_","^_","[_"],
	["5_","__","__","__","__"],
	["6_","__","__","__","__"],
	["7_","!_","}_","/_","{_"],
	["8_","@_","It","\\_","Ee"],
	["9_","&_","Be","|_","De"],
	["0_",":_",">_",";_","<_"]],
	dtype="a2"
	)

right_numspecial_str_2D_array = np.array([
	["0_",":_",">_",";_","<_"],
	["9_","&_","Be","|_","De"],
	["8_","@_","It","\\_","Ee"],
	["7_","!_","}_","/_","{_"],
	["6_","__","__","__","__"],
	["5_","__","__","__","__"],
	["4_","*_",")_","^_","(_"],
	["3_","+_","Be","%_","De"],
	["2_","-_","It","$_","Ee"],
	["1_","=_",")_","#_","(_"]],
	dtype="a2"
	)

# accessed via Joyclick-East, since Arrow keys are on top side of qwerty keyboard
arrow_str_2D_array = np.array([
	["Lt","F1","__","11","__"],
	["Dn","F2","It","12","Ee"],
	["Up","F3","Be","__","De"],
	["Rt","F4","__","__","__"],
	["F5","__","__","__","__"],
	["F6","__","__","__","__"],
	["He_","F7","__","__","__"],
	["PD_","F8","Ee",",_","It"],
	["PU_","F9","Be","._","De"],
	["Ed_","10","__","__","__"]],
	dtype="a2"
	)

# accessed via Joyclick-South, (default mode)
alpha_str_2D_array = np.array([
	["a_","q_","'_","z_","`_"],
	["s_","w_","It","x_","Ee"],
	["e_","d_","Be","c_","De"],
	["t_","f_","r_","v_","g_"],
	["__","__","__","__","__"],
	["__","__","__","__","__"],
	["n_","u_","m_","j_","h_"],
	["i_","k_","It",",_","Ee"],
	["o_","l_","Be","._","De"],
	["p_","y_","/_","b_",";_"]],
	dtype="a2"
	)

# accessed via Joyclick-South, (default mode)
left_alpha_str_2D_array = np.array([
	["a_","q_","'_","z_","`_"],
	["s_","w_","It","x_","Ee"],
	["e_","d_","Be","c_","De"],
	["t_","f_","r_","v_","g_"],
	["__","__","__","__","__"],
	["__","__","__","__","__"],
	["n_","u_","m_","j_","h_"],
	["i_","k_","It",",_","Ee"],
	["o_","l_","Be","._","De"],
	["p_","y_","/_","b_",";_"]],
	dtype="a2"
	)

# accessed via Joyclick-South, (default mode)
right_alpha_str_2D_array = np.array([
	["p_","y_","/_","b_",";_"],
	["o_","l_","Be","._","De"],
	["i_","k_","It",",_","Ee"],
	["n_","u_","m_","j_","h_"],
	["__","__","__","__","__"],
	["__","__","__","__","__"],
	["t_","f_","r_","v_","g_"],
	["e_","d_","Be","c_","De"],
	["s_","w_","It","x_","Ee"],
	["a_","q_","'_","z_","`_"]],
	dtype="a2"
	)

# accessed via Joyclick-West, since Shift key is on left side of qwerty keyboard
caps_str_2D_array = np.array([
	["A_","Q_","\"_","Z_","~_"],
	["S_","W_","It","X_","Ee"],
	["E_","D_","Be","C_","De"],
	["T_","F_","R_","V_","G_"],
	["__","__","__","__","__"],
	["__","__","__","__","__"],
	["N_","U_","M_","J_","H_"],
	["I_","K_","It","<_","Ee"],
	["O_","L_","Be",">_","De"],
	["P_","Y_","?_","B_",":_"]],
	dtype="a2"
	)

def get_numspecial_char_str(hand, btn_idx, dir_idx):
    if   hand == "left" :
    	return left_numspecial_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
	return right_numspecial_str_2D_array[btn_idx][dir_idx]

def get_arrow_char_str(btn_idx, dir_idx):
    return arrow_str_2D_array[btn_idx][dir_idx] 

def get_alpha_char_str(hand, btn_idx, dir_idx):
    if   hand == "left" :
    	return left_alpha_str_2D_array[btn_idx][dir_idx]
    elif hand == "right" :
    	return right_alpha_str_2D_array[btn_idx][dir_idx]

def get_caps_char_str(btn_idx, dir_idx):
    return caps_str_2D_array[btn_idx][dir_idx]

def get_HID(char_str) :
    return char_str_2_HID_code[char_str]

def get_Shift_Required(char_str):
    return char_str_requires_shift_mod[char_str]

# ======================
# Analog Joystick Setup
# ======================

print "opening up SPI Bus to read Analog Pins"
	
#open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

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

		GPIO.setmode(GPIO.BOARD)

		self.btn2_pin = 33
		self.btn3_pin = 31
		self.btn4_pin = 35
		self.btn5_pin = 37

		GPIO.setup(self.btn2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # index finger
		GPIO.setup(self.btn3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # middle finger
		GPIO.setup(self.btn4_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # ring finger
		GPIO.setup(self.btn5_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # pinky finger
	
		# Define sensor channels
		# (channels 3 to 7 unused)
		#self.swt_channel = 0
		#self.vrx_channel = 1
		#self.vry_channel = 2

		self.analog_dimension = 1024 	# 2^10 

		# Harcoded deadzone width;
		self.deadzone_width = 64	# 2^7 / 2

		# used to access the alpha_str_2D_array, for debugging purposes right now

		self.arr_idx = 4;

		#self.arr_idx = 3; # direction = {neutral=0, north=1, east=2, south=3, west=4}, counting clockwise

		self.hand = "left"

		# Initialize last variables

		# Think about using a coniditional to check for in-valid index at start-up
		self.last_btn_idx = -1
		self.last_dir_idx = -1
		self.last_arr_idx = 4 # default to lowercase letters

		self.btn_queue = [-1 -1 -1 -1] # USE THIS TO ACT JUST LIKE PRESSED KEYS in java code...

		self.reset_joystick_path()

		# modifier lockers: none -> once -> always (locked) -> none => kb.L_ == 0 -> kb.L_ == 1 -> kb.L_ == 1 and kb.L__lock == 1 -> kb.L_ = 0

		self.depressed_analog_shift_modifier = 1 # required to prevent holding Analog Click (Shift) from rapidly cycling through
		self.reset_modifier_locks()

		self.reset_modifiers()

		# end of __init__

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

		btn4 = GPIO.input(kb.btn4_pin)
		if btn4 == 1:
			btn_idx = 1

		btn3 = GPIO.input(kb.btn3_pin)
		if btn3 == 1:
			btn_idx = 2

		btn2 = GPIO.input(kb.btn2_pin)
		if btn2 == 1:
			btn_idx = 3

		# read z-click on the analog stick
		# off = ~1024 , on = 0
		btn1 = ReadChannel(0)
		if btn1 == 0:
			btn_idx = 4
		else :
			#print "depress" ,
			kb.depressed_analog_shift_modifier = 1 # records that we've depressed the analog click, necessary for Analog Click Shift Modifier to function

		# DEBUGGING Button/Direction recognition
		# print "btn5 = " + str(btn5) + "\tbtn4 = " + str(btn4) + "\tbtn3 = " + str(btn3) + "\tbtn2 = " + str(btn2) + "\tbtn1 = " + str(btn1) + "\tLHdirection =" + LH_direction , 

		mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)

		# print "\tmod_bit_str=" + mod_bit_str ,

		mod_lock_bit_str = str(kb.LM_lock) + str(kb.LA_lock) + str(kb.LS_lock) + str(kb.LC_lock) + str(kb.RM_lock) + str(kb.RA_lock) + str(kb.RS_lock) + str(kb.RC_lock)

		# print "\tmod_lock_bit_str=" + mod_lock_bit_str ,

 		# print "\tdepressed_analog_shift_modifier = " + str(kb.depressed_analog_shift_modifier) , 

 		# print "\tkb.LS = " + str(kb.LS) + "\tkb.LS_lock = " + str(kb.LS_lock) ,

		# ====================================================================
		# get HID code and perform keyboard function with necessary modifiers
		# ====================================================================

		if (dir_idx > -1 and btn_idx > -1) or not char_str == "" : # if direction and button properly identified, or whitespace char_str has been assigned

			# Mechanism for changing character sets, using analog click (joyclick) + cardinal direction to change to new set (N=numsp,E=arrow,S=alpha,W=shift)

			if (btn_idx == 4 or btn_idx == 5) : # Left or Right Analog clicks respectively
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
							print "in loop"

							kb.depressed_analog_shift_modifier = -1 # don't allow more toggling until analog-click is depressed, then re-pressed
						
						hid = -1 # prevent typing

			mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)

			# DEBUGGING Shift toggle via Analog Click (not for numbers, where analog click becomes 5 or 6)
			# print "\tmod_bit_str" + mod_bit_str ,
			
			if not hid == -1 :
				arr_idx = kb.last_arr_idx # Get array index for determining which set of character we are currently typing
	
				if char_str == "" : # if no white-space flick char_str assigned
					if   arr_idx == 1 :
						char_str = get_numspecial_char_str(kb.hand, btn_idx, dir_idx) 
					elif arr_idx == 2 :
						kb.hand = "right"
						char_str = get_alpha_char_str(kb.hand, btn_idx, dir_idx) 
						#char_str = get_arrow_char_str(btn_idx, dir_idx) 
					elif arr_idx == 3 :
						char_str = get_arrow_char_str(btn_idx, dir_idx)
						#char_str = get_alpha_char_str(btn_idx, dir_idx) 
					elif arr_idx == 4 :
						kb.hand = "left"
						char_str = get_alpha_char_str(kb.hand,btn_idx, dir_idx) 
						#char_str = get_caps_char_str(btn_idx, dir_idx)

				if get_Shift_Required(char_str) == 1 :
					kb.LS = 1 # turn left shift modifier on
	
				hid = get_HID(char_str)

				mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)
	
				# DEBUGGING final character set index (arr_idx), 2-character long key string, hid code, & modifier bit string 
				# print "\tarr_idx =" + str(arr_idx) + "\tchar_str = " + char_str + "\tHID = " + str(hid) + "\tmod_bit_str" + mod_bit_str ,
		
				kb.iface.send_keys( int(mod_bit_str,2), [hid,0,0,0,0,0] )

				kb.reset_joystick_path() # reset joystick path so we prevent white-space flicks when joystick resets to neutral
				kb.reset_modifiers() # reset modifiers when you type a character (this will prevent ctrl and shift from being held though)
		else:
			mod_bit_str = str(kb.LM) + str(kb.LA) + str(kb.LS) + str(kb.LC) + str(kb.RM) + str(kb.RA) + str(kb.RS) + str(kb.RC)
			
			kb.iface.send_keys(int(mod_bit_str,2),[0,0,0,0,0,0]) # send only any locked modifiers (for alt-tab, etc.)

		kb.last_btn_idx = btn_idx
		kb.last_dir_idx = dir_idx

		print "\n" ,
