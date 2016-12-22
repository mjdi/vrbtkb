FYDP NE2017_11: Repurposing http://yetanotherpointlesstechblog.blogspot.ca/2016/04/emulating-bluetooth-keyboard-with.html in a 4-button + clickable analog joystick Raspberry Pi (RPi) Zero based bluetooth controller used for emulating a regular QWERTY keyboard's functionality on a VR-enabled Android smartphone while in the VR environment (with no touch-screen access)

Add line '@bash /home/pi/vrbtkb/startuo_script.sh' to the end of '/home/pi/.config/lxsession/LXDE/autostart' file for headless operation waiting about ~2 minutes for RPi to boot (and be running bt_server.py which accepts connections to a previously paired device) to then connect the VR-enabled Android smartphone to the RPi via bluetooth

 Button GPIO pins:

GPIO.setmode(GPIO.BOARD)

		self.btn2_pin = 33
		self.btn3_pin = 31
		self.btn4_pin = 35
		self.btn5_pin = 37

**INSTRUCTIONS FOR SETTING UP WITH Next Thing Co. CHIP (all scripts have been updated specifically for the CHIP) **

Flash 4.4 (non-headless, trying now) headless (FEL mode shorting FEL and GND) http://flash.getchip.com/

(git is for some reason not included)
sudo apt-get install git

~sudo apt-get remove blueman (conflicts with 'sudo /etc/init.d/bluetooth stop' command?~ No, turns out I just forgot to use '&; at the end to run in a separate process, so remember to use '&'!

Did you try do install the device tree overlay in /etc/rc.local? It is in /lib/firmware !
https://bbs.nextthing.co/t/spi-serial-communication-on-chip/11937/5

sudo modprobe spidev  http://www.chip-community.org/index.php/SPI_support
(short MOSI and MISO to test spidev with the instructions there)

~the 4.4.13 ? kernel somehow already includes the DTC? or was that what I downloaded, via the dtc git clone, probably ya~ (so SPI and GPIO work off the bat!!)

^^ Turns out the latest 4.4 CHIP kernel does set the CONFIG_CONGIFS on https://github.com/xtacocorex/CHIP_IO
("OverlayManager requires a 4.4 kernel with the CONFIG_OF_CONFIGFS option enabled in the kernel config.")

#make sure to clone this repo as well as the CHIP_IO repo (following the install instructions there specifically for python2.7)

#Use crontab to allow for headless operation (run <man 5 crontab> to learn more about it)

begin add to <crontab -e>:

SHELL=/bin/bash
MAILTO=""
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
@reboot root bash /home/chip/vrbtkb/startup.sh

: end add to <crontab -e>

CHIP_IO pin names: https://github.com/xtacocorex/CHIP_IO

		self.btn2_pin = "GPIO2"
		self.btn3_pin = "GPIO3"
		self.btn4_pin = "GPIO4"
		self.btn5_pin = "GPIO5"
