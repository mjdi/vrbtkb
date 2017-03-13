# -*- coding: utf8 -*-

#!/usr/bin/python

import os

import sys

hand = str(sys.argv[1]) # accept the handedness as an C.L. argument, sys.argv[0] is the name of the python script itself

import subprocess # also used to grep spi device Bus and Device integer values

device = subprocess.check_output("ls /home/",shell=True).rstrip()

# import CHIP_IO.OverlayManager as OM 	# https://github.com/xtacocorex/CHIP_IO, not necessary now with /etc/rc.local nano edit
# OM.load("SPI2")
import spidev   #to use joystick

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
  
class VR_Keyboard_Ignition():

	def __init__(self):
    
		self.analog_dimension = 1024 	# based on 10 bit ADC (MPC3008)

		self.deadzone_width = 64 		# 2^7 / 2, (hardcoded)
		
		self.last_dir_idx = -1

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
  
  	def debug_joystick_cycle(self):

	      print "{D2N,D2E,D2S,D2W} = [" + str(self.D2N) + str(self.D2E) + str(self.D2S) + str(self.D2W) + "], " ,
	      print "{N2W,W2S,S2E,E2N} = [" + str(self.N2W) + str(self.W2S) + str(self.S2E) + str(self.E2N) + "], " ,
	      print "{N2E,E2S,S2W,W2N} = [" + str(self.N2E) + str(self.E2S) + str(self.S2W) + str(self.W2N) + "], " ,  

	def check_joystick_deadzone_cycle_for_ignition(self):

		num_CW_edges  = self.N2E + self.E2S + self.S2W + self.W2N # number of clockwise edges traveled along deadzone cycle
		num_CCW_edges = self.N2W + self.W2S + self.S2E + self.E2N # number of counter-clockwise edges traveled along deadzone cycle

		if   num_CW_edges == 4 and num_CCW_edges == 4 : # both full counter-clockwise & full clockwise rotations

			spi.close()
			
			os.system("sudo python /home/" + device + "/vrbtkb/vrkeyboard/kb_client.py " + hand + " &")
			
			sys.exit()

if __name__ == "__main__":

	kb_gate = VR_Keynoard_Ignition()

	while True: # main while loop

		kb_gate.get_dir_idx()

		if kb.dir_idx == 0 :

		 	kb_gate.check_joystick_deadzone_cycle_for_ignition()

		kb.last_dir_idx = kb.dir_idx
