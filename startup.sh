#!bin/usr/env bash

sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time &

sleep 5

sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master &

sleep 5

sudo python ~/vrbtkb/server/btk_server.py left &
# sudo python ~/vrbtkb/server/btk_server.py right &
