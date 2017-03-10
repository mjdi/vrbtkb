#!bin/usr/env bash

sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time &

sleep 3

sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master &

sleep 3

device=$(ls /home | perl -pe 'chomp if eof')

sudo python /home/$device/vrbtkb/server/btk_server.py left & # using ~/ causes /root/ instead
# sudo python /home/$device/vrbtkb/server/btk_server.py right &
