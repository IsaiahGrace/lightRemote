#!/bin/bash

echo running shutdownPi service: got this far...
scp /home/isaiah/lights/shutdown-signal pi@beacon:~/shutdown-signal
ssh -t pi@beacon 'sudo shutdown now'
touch /home/isaiah/lights/shutdown-sent
echo waiting 5 seconds for Pi to shut down before me
sleep 5


