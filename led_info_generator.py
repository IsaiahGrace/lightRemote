# Isaiah Grace
# 5 April 2020
# This file DOES NOT go onto the ESP32 board.
# The point is to create the led_info_data file that led_info.py will use

import pprint as pp
import json

info = []
	# 0 - wakeup(slow green fade in)
	# 1 - wifi-connected(flash green)
	# 2 - no-wifi-found(flash red)
	# 3 - mqtt-connected(flash gold)

# create msg 0 - wakeup(slow green fade in)
info.append([])
for i in range(0,90):
	color = i // 3
	info[0].append((0, color, 0))
for i in range(0,90):
	color = 90 // 3 - i // 3
	info[0].append((0, color, 0))

# create msg 1 - wifi-connected(flash green)
info.append([])
for i in range(0,40*3):
	color =  15 if i // 20 % 2 == 0 else 0
	info[1].append((0, color, 0))

# create msg 2 - no-wifi-found(flash red)
info.append([])
for i in range(0,40*3):
	color =  20 if i // 20 % 2 == 0 else 0
	info[2].append((color, 0, 0))

# create msg 3 - mqtt-connected(flash gold)
info.append([])
for i in range(0,40*3):
	# This color is a dark blue/purple. 
	color =  (64 // 8, 0, 128 // 4) if i // 20 % 2 == 0 else (0,0,0)
	info[3].append(color)

# Ensure that the last entry in each msg is to turn off the LEDs
for msg in info:
	msg[-1] = (0,0,0)

# Write the info data to a file
with open("led_info_data","w") as f:
	f.write(json.dumps(info))
	
#pp.pprint(info)
