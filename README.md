FYDP NE2017_11: Repurposing http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html in a 4-button + clickable analog joystick Raspberry Pi (RPi) Zero based bluetooth controller used for emulating a regular QWERTY keyboard's functionality on a VR-enabled Android smartphone while in the VR environment (with no touch-screen access)

Add line '@bash /home/pi/vrbtkb/startup.sh' to the end of '/home/pi/.config/lxsession/LXDE/autostart' file for headless operation waiting about ~2 minutes for RPi to boot (and be running bt_server.py which accepts connections to a previously paired device) to then connect the VR-enabled Android smartphone to the RPi via bluetooth

#**RPi Button GPIO pins:**

		self.btn2_pin = 33
		self.btn3_pin = 31
		self.btn4_pin = 35
		self.btn5_pin = 37

#**INSTRUCTIONS FOR SETTING UP WITH Next Thing Co. CHIP (all scripts have been updated specifically for the CHIP)**

Flash 4.4 server (FEL mode by shorting FEL and GND pins) http://flash.getchip.com/

~~delete the driver > libusbK > Flashing Mode Chip thingee

~~download and install linux-cdc-acm.inf from this link here: https://bbs.nextthing.co/t/version-4-4-always-in-flashing-mode/4960/20

https://bbs.nextthing.co/t/updated-cdc-composite-gadget-4-4-driver-issue-on-windows/7458

#**CHIP_IO pin names**

https://github.com/xtacocorex/CHIP_IO

		self.btn2_pin = "GPIO2"
		self.btn3_pin = "GPIO3"
		self.btn4_pin = "GPIO4"
		self.btn5_pin = "GPIO5"

#**setup WiFi and SSH capabilities (Via COM port)** 

https://www.reddit.com/r/ChipCommunity/comments/5hndoj/setting_up_the_chip_under_win10_walkthrough/

	sudo nmtui
	apt-get update
	apt-get install xrdp
	echo xfce4-session >~/.xsession
	nano /etc/xrdp/startwm.sh

<- For me it have worked to just exit without any editing.

	service xrdp restart
	ip addr show
	
You are looking for something like:

Wlan0
inet 10.0.0.xxx where the 10.0.0.xxx is the CHIPs IP on your local network. Scribble down your CHIPs IP-adress.
	
	sudo reboot
	
#**setup Bluetooth (Via SSH or COM port)** 

	sudo apt-get install git

	sudo apt-get install python-gobject bluez bluez-tools bluez-firmware python-bluez python-dev python-pip 

	git clone https://github.com/mjdi/vrbtkb

	sudo cp /home/chip/vrbtkb/dbus/org.yaptb.btkbservice.conf /etc/dbus-1/system.d 
	
do the bluetoothctl setup as usual

	bluetoothctl
	
in the [bluetooth#] prompt that shows up:

	agent on
	default-agent
	scan on
	discoverable on
	
try to pair to CHIP with android smartphone (register new device)

	BEFORE PRESSING YES ON THE ANDROID PHONE, enter (yes) in the bluetoothctl prompt when it asks you to on the CHIP
	
Now, the device should be registered, and when you reboot the CHIP and wait ~ 20 sec (after it fully boots), you should be able to connect the Smartphone in order to use the CHIP as a BT keyboard

#**SpiDev setup for CHIP**

	git clone https://github.com/doceme/py-spidev
	cd ./py-spidev
	sudo python setup.py install
	cd ..

https://bbs.nextthing.co/t/spi-serial-communication-on-chip/11937/5

	sudo nano /etc/rc.local

add these two lines to the end of rc.local (so it runs on startup)

	mkdir -p /sys/kernel/config/device-tree/overlays/spi
	cat /lib/firmware/nextthingco/chip/sample-spi.dtbo > /sys/kernel/config/device-tree/overlays/spi/dtbo

then in the terminal run http://www.chip-community.org/index.php/SPI_support (short MOSI and MISO to test spidev with the instructions there)
	
	sudo modprobe spidev 
	
to activate the spidev

confirm that spidev exists with
	
	ls /dev/spidev*

#**GPIO setup for CHIP**

^^ Turns out the latest 4.4 CHIP kernel does set the CONFIG_CONGIFS on https://github.com/xtacocorex/CHIP_IO
("OverlayManager requires a 4.4 kernel with the CONFIG_OF_CONFIGFS option enabled in the kernel config.")

	sudo apt-get update
	sudo apt-get install git build-essential python-dev python-pip flex bison -y
	git clone https://github.com/atenart/dtc
	cd dtc
	make
	sudo  make install PREFIX=/usr
	cd ..
	git clone https://github.com/xtacocorex/CHIP_IO.git
	cd CHIP_IO
	sudo python setup.py install
	cd ..
	sudo rm -rf CHIP_IO
	
#**Headless setup for CHIP**

Use systemwide crontab to allow for headless operation"

	sudo nano /etc/crontab
	
add the following line to the file and use Ctrl-O to save the edit

	@reboot        chip     sleep 7; echo "chip" | sudo bash /home/chip/vrbtkb/startup.sh 

NOW REBOOT!
