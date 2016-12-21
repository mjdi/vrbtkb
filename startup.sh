#!bin/usr/env bash

#xterm -hold -e 'sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time' &
sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time &

sleep 5

#xterm -hold -e 'sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master' &
sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master &

sleep 5

#xterm -hold -e 'sudo python /home/pi/vrbtkb/btkeyboard/bt_kb_client.py' &
sudo python /home/mjd/vrbtkb/vrkeyboard/vr_kb_client.py &
