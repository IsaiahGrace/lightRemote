# Isaiah Grace
# 9 April 2020

# A small test of the analog slide potentiometer:
#           ADC
#            |
#  +3.3V--/\/\/\--GND
#         1k Ohm

from machine import ADC, Pin
from time import sleep_ms
import neopixel

sliders = []
sliders.append(ADC(Pin(34)))
sliders.append(ADC(Pin(39)))
sliders.append(ADC(Pin(36)))

led = neopixel.NeoPixel(Pin(14),2)

# Attenuate the input to give a maximum of ~3.6v
for slider in sliders:
	slider.atten(ADC.ATTN_11DB)

color = [0,0,0]
print("Reading from ADC:")
while(True):
	print('\r',end='')
	for i in range(3):
		# scale ADC reading from [0:4095] to [0:255]
		color[i] = sliders[i].read() // 16 
		print('{:03d}'.format(color[i]),end=' ')
	led[0] = color
	# make the other LED half as bright,
	# this is good on my eyes and doesn't seem to affect color
	led[1] = [color[0] // 2, color[1] // 2, color[2] // 2] 
	led.write()
	sleep_ms(100)

# Looks like the range is good between 0000 to 4095!
