#!/usr/bin/python
#
# YAPTB Bluetooth keyboard emulator DBUS Service
# 
# Adapted from 
# www.linuxuser.co.uk/tutorials/emulate-bluetooth-keyboard-with-the-raspberry-pi
#
# Following http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html
#

#from __future__ import absolute_import, print_function, unicode_literals
from __future__ import absolute_import, print_function

from optparse import OptionParser, make_option
import os
import sys
import uuid
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import bluetooth
from bluetooth import *

# imports added for vrbtkb
import subprocess
device = subprocess.check_output("ls /home/",shell=True).rstrip()
hand = str(sys.argv[1]) # accept the handedness as an C.L. argument, sys.argv[0] is the name of the python script itself

import gtk
from dbus.mainloop.glib import DBusGMainLoop

#
#define a bluez 5 profile object for our keyboard
#
class BTKbBluezProfile(dbus.service.Object):
    fd = -1

    @dbus.service.method("org.bluez.Profile1",
                                    in_signature="", out_signature="")
    def Release(self):
            print("Release")
            mainloop.quit()

    @dbus.service.method("org.bluez.Profile1",
                                    in_signature="", out_signature="")
    def Cancel(self):
            print("Cancel")

    @dbus.service.method("org.bluez.Profile1", in_signature="oha{sv}", out_signature="")
    def NewConnection(self, path, fd, properties):
            self.fd = fd.take()
            print("NewConnection(%s, %d)" % (path, self.fd))
            for key in properties.keys():
                    if key == "Version" or key == "Features":
                            print("  %s = 0x%04x" % (key, properties[key]))
                    else:
                            print("  %s = %s" % (key, properties[key]))
            


    @dbus.service.method("org.bluez.Profile1", in_signature="o", out_signature="")
    def RequestDisconnection(self, path):
            print("RequestDisconnection(%s)" % (path))

            if (self.fd > 0):
                    os.close(self.fd)
                    self.fd = -1

    def __init__(self, bus, path):
            dbus.service.Object.__init__(self, bus, path)


#
#create a bluetooth device to emulate a HID keyboard, 
# advertize a SDP record using our bluez profile class
#
class BTKbDevice(): 
    MY_ADDRESS = subprocess.check_output("hciconfig | grep 'BD' | grep -oP '..:..:..:..:..:..'", shell=True)
	
    MY_DEV_NAME = device + "_" + hand + "_hand_wlan_not_connected"
	
    #if subprocess.check_output("hostname -I | grep -oP '...\....\..\...'", shell=True).rstrip() == "" : 
    #	MY_DEV_NAME = device + "_" + hand + "_hand_wlan_not_connected"
    #else :
    #	MY_DEV_NAME = device + "_" + hand + "_hand_" + subprocess.check_output("hostname -I | grep -oP '...\....\..\...'", shell=True).rstrip()
	
    #define some constants
    P_CTRL =17  #Service port - must match port configured in SDP record
    P_INTR =19  #Service port - must match port configured in SDP record#Interrrupt port  
    PROFILE_DBUS_PATH="/bluez/yaptb/btkb_profile" #dbus path of  the bluez profile we will create
    SDP_RECORD_PATH = sys.path[0] + "/sdp_record.xml" #file path of the sdp record to laod
    UUID="00001124-0000-1000-8000-00805f9b34fb"
             
 
    def __init__(self):

        print("Setting up BT device")

        self.init_bt_device()
        self.init_bluez_profile()
                    

    #configure the bluetooth hardware device
    def init_bt_device(self):


        print("Configuring for name "+BTKbDevice.MY_DEV_NAME)

        #set the device class to a keybord and set the name
        os.system("hciconfig hcio class 0x002540")
        os.system("hciconfig hcio name " + BTKbDevice.MY_DEV_NAME)

        #make the device discoverable
        os.system("hciconfig hcio piscan")


    #set up a bluez profile to advertise device capabilities from a loaded service record
    def init_bluez_profile(self):

        print("Configuring Bluez Profile")

        #setup profile options
        service_record=self.read_sdp_service_record()

        opts = {
            "ServiceRecord":service_record,
            "Role":"server",
            "RequireAuthentication":False,
            "RequireAuthorization":False
        }

        #retrieve a proxy for the bluez profile interface
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez","/org/bluez"), "org.bluez.ProfileManager1")

        profile = BTKbBluezProfile(bus, BTKbDevice.PROFILE_DBUS_PATH)

        manager.RegisterProfile(BTKbDevice.PROFILE_DBUS_PATH, BTKbDevice.UUID,opts)

        print("Profile registered ")


    #read and return an sdp record from a file
    def read_sdp_service_record(self):

        print("Reading service record")

        try:
            fh = open(BTKbDevice.SDP_RECORD_PATH, "r")
        except:
            sys.exit("Could not open the sdp record. Exiting...")

        return fh.read()   



    #listen for incoming client connections
    #ideally this would be handled by the Bluez 5 profile 
    #but that didn't seem to work
    def listen(self):

        print("Waiting for connections")
        self.scontrol=BluetoothSocket(L2CAP)
        self.sinterrupt=BluetoothSocket(L2CAP)

        #bind these sockets to a port - port zero to select next available		
        self.scontrol.bind((self.MY_ADDRESS,self.P_CTRL))
        self.sinterrupt.bind((self.MY_ADDRESS,self.P_INTR ))

        #Start listening on the server sockets 
        self.scontrol.listen(1) # Limit of 1 connection
        self.sinterrupt.listen(1)

        self.ccontrol,cinfo = self.scontrol.accept()
        print ("Got a connection on the control channel from " + cinfo[0])

        self.cinterrupt, cinfo = self.sinterrupt.accept()
        print ("Got a connection on the interrupt channel from " + cinfo[0])

	# ==== Initiate kb_client.py as soon as connection is made! ==== #
	
	# functionality of starting kb.py is now relegated to the kb_ignition.py script (requires Full CW and Full CCW rotations)
	#os.system("sudo python /home/" + device + "/vrbtkb/vrkeyboard/kb_client.py " + hand + " &")

    #send a string to the bluetooth host machine
    def send_string(self,message):

     #    print("Sending "+message)
         self.cinterrupt.send(message)



#define a dbus service that emulates a bluetooth keyboard
#this will enable different clients to connect to and use 
#the service
class  BTKbService(dbus.service.Object):

    def __init__(self):

        print("Setting up service")

        #set up as a dbus service
        bus_name=dbus.service.BusName("org.yaptb.btkbservice",bus=dbus.SystemBus())
        dbus.service.Object.__init__(self,bus_name,"/org/yaptb/btkbservice")

        #create and setup our device
        self.device= BTKbDevice();

        #start listening for connections
        self.device.listen();

            
    @dbus.service.method('org.yaptb.btkbservice', in_signature='yay')
    def send_keys(self,modifier_byte,keys):

        cmd_str=""
        cmd_str+=chr(0xA1)
        cmd_str+=chr(0x01)
        cmd_str+=chr(modifier_byte)
        cmd_str+=chr(0x00)

        count=0
        for key_code in keys:
            if(count<6):
                cmd_str+=chr(key_code)
            count+=1

        self.device.send_string(cmd_str);		


#main routine
if __name__ == "__main__":
    # we an only run as root
    if not os.geteuid() == 0:
       sys.exit("Only root can run this script")

    DBusGMainLoop(set_as_default=True)
    myservice = BTKbService();
    gtk.main()
	
	
