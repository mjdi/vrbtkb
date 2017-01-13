#!bin/usr/env bash

xterm -hold -e 'sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time' &

sleep 5

xterm -hold -e 'sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master' &

sleep 5

xterm -hold -e 'sudo python /home/pi/vrbtkb/server/RPi_btk_server.py' &

# RPi_btk_server.py will automatically run /home/pi/vrbtkb/vrkeyboard/RPI_kb_client.py if it accepts a connection
