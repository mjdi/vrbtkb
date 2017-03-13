#!bin/usr/env bash

sudo /etc/init.d/bluetooth stop; sudo /usr/sbin/bluetoothd --nodetach --debug -p time &

sleep 3

sudo hciconfig hcio; sudo hciconfig hcio up; sudo hciconfig hcio lm master &

sleep 3

device=$(ls /home | perl -pe 'chomp if eof')

# $1 is the first argument taken by startup.sh ( which should be either "left" or "right" in the /etc/crontab entry, no quotations )

sudo python /home/$device/vrbtkb/server/btk_server.py $1 & # using ~/ causes /root/ instead

sudo python /home/$device/vrbtkb/vrkeyboard/kb_ignition.py $1 & # using ~/ causes /root/ instead
