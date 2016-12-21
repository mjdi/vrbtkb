#!bin/usr/env bash

#xterm -hold -e 'sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time' &

sleep 5

#xterm -hold -e 'sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master' &

sleep 5

#xterm -hold -e 'sudo python /home/pi/vrbtkb/server/btk_server.py' &
xterm -hold -e 'sudo python /home/chip/vrbtkb/server/btk_server.py' &
