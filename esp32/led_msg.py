# Isaiah Grace
# 7 April 2020
# Fear of Coronavirus is real

# This module is an attempt to replace led_info.py with a more memory efficient implimentation

from machine import Timer, Pin
import neopixel

# The color arguments should be indexable in the form (r,g,b)
# each color value must be an int between 0-255

# The interrupt for the timers are only executed every 20ms, so all ms arguments have a maximum resolution of 20ms
# This gives an update frequency of 50Hz for the LEDs, plenty good for what we're up to.

# Global refrences to resources
TIMER = None
LEDS = [0,0]

LED1 = (0,0,0)
LED2 = (0,0,0)
LED1_STEP = (0,0,0)
LED2_STEP = (0,0,0)

# fade MSG state
RISE = 0
FALL = 0
RISE_SCALE = 0
FALL_SCALE = 0

# flash MSG state
HIGH = 0
LOW = 0
DUR = 0
STATE = False
RED = (40,0,0)
GREEN = (0,40,0)
BLUE = (0,0,40)

# MSG active
ACTIVE = False

def is_active():
	return ACTIVE

def stop_all():
	global ACTIVE
	if not ACTIVE:
		return

	TIMER.deinit()
	LEDS[0] = (0,0,0)
	LEDS[1] = (0,0,0)
	LEDS.write()
	ACTIVE = False

def fade_msg(color1, color2=None):
	global LED1
	global LED2
	global LED1_STEP
	global LED2_STEP
	global RISE
	global FALL
	global RISE_SCALE
	global FALL_SCALE
	global LEDS
	global TIMER
	global ACTIVE

	# Okay, we've got to do some serious figuring out to make a smooth transition to any color
	# We can't do any floating point arithmetic inside the IRQ, so instead we will multiply
	# all numbers by 1000, which will give us a little more resoltion
	LED1 = [0,0,0]
	LED2 = [0,0,0]
	LED1_STEP = color1
	LED2_STEP = color2 if color2 != None else color1
	RISE = rise_time_ms
	FALL = fall_time_ms
	RISE_SCALE = rise_time_ms // 20
	FALL_SCALE = fall_time_ms // 20
	LEDS = neopixel.NeoPixel(Pin(14),2)
	TIMER = Timer(1)
	TIMER.init(period=20, mode=Timer.PERIODIC, callback=irq_fade_msg)
	ACTIVE = True
	
def irq_fade_msg(arg1):
	global LED1
	global LED2
	global LED1_STEP
	global LED2_STEP
	global RISE
	global FALL
	global RISE_SCALE
	global FALL_SCALE
	global LEDS
	global TIMER
	global ACTIVE
	
	if RISE > 20:
		RISE = RISE - 20
		LED1 = LED1 + LED1_STEP
		LED2 = LED2 + LED2_STEP
		LEDS[0] = LED1 // RISE_SCALE
		LEDS[1] = LED2 // RISE_SCALE		
	elif FALL > 20:
		FALL = FALL - 20
		LED1 = LED1 - LED1_STEP
		LED2 = LED2 - LED2_STEP
		LEDS[0] = LED1 // FALL_SCALE
		LEDS[1] = LED2 // FALL_SCALE
	else:
		LEDS[0] = [0,0,0]
		LEDS[1] = [0,0,0]
		#TIMER.deinit()
		ACTIVE = False
	#LEDS.write()
	
	

def flash_msg(color1, color2=None, period_ms=500,  duration_ms=2000):
	global TIMER
	global LEDS
	global ACTIVE
	global PERIOD
	global DURATION
	global STATE
	global LED1
	global LED2
	if ACTIVE :
		print("ERROR, led_msg is still active, cannot start new message yet")
		return

	if color2 == None:
		color2 = color1

	LED1 = color1
	LED2 = color2
	PERIOD = period_ms
	DURATION = duration_ms
	STATE = False

	LEDS = neopixel.NeoPixel(Pin(14),2)
	TIMER = Timer(1)
	TIMER.init(period=PERIOD, mode=Timer.PERIODIC, callback=irq_flash_msg)
	ACTIVE = True

def irq_flash_msg(arg1):
	global LEDS
	global TIMER
	global LED1
	global LED2
	global PERIOD
	global DURATION
	global STATE
	global ACTIVE

	if DURATION < PERIOD:
		STATE = True
		ACTIVE = False
		TIMER.deinit()

	if STATE:
		LEDS[0] = (0,0,0)
		LEDS[1] = (0,0,0)
	else:
		LEDS[0] = LED1
		LEDS[1] = LED2

	LEDS.write()
	
	STATE = not STATE

	DURATION = DURATION - PERIOD

	
