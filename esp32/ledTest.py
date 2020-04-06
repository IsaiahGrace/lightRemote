# Isaiah Grace
# 5 April 2020
# Quarantine in Richmond

# This script tests controlling two SK6812 LEDs
# using the neopixel micropython library on a ESP32 Feather Huzzah board

import machine, neopixel

# Configure a NeoPixel LED strip on pin 14 with 2 LEDs on the strip
np = neopixel.NeoPixel(machine.Pin(14),2)

np[0] = (65,0,0)
np[1] = (0,65,0)

np.write()


