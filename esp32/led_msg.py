# Isaiah Grace
# 7 April 2020
# Fear of Coronavirus is real

# This module is an attempt to replace led_info.py with a more memory efficient implimentation

#from machine import Timer, Pin
#import neopixel

# The color arguments should be indexable in the form (r,g,b)
# each color value must be an int between 0-255

# The interrupt for the timers are only executed every 20ms, so all ms arguments have a maximum resolution of 20ms
# This gives an update frequency of 50Hz for the LEDs, plenty good for what we're up to.

# Global refrences to resources
__timer__ = None
__leds__ = [0,0]

__LED1__ = (0,0,0)
__LED2__ = (0,0,0)
__LED1_STEP__ = (0,0,0)
__LED2_STEP__ = (0,0,0)

# fade MSG state
__RISE__ = 0
__FALL__ = 0
__RISE_SCALE__ = 0
__FALL_SCALE__ = 0

# flash MSG state
__HIGH__ = 0
__LOW__ = 0
__DUR__ = 0

# MSG active
__active__ = False

def is_active():
	return __active__

def stop_all():
	global __active__
	if not __active__:
		return

	__timer__.deinit()
	__leds__[0] = (0,0,0)
	__leds__[1] = (0,0,0)
	__leds__.write()
	__active__ = False

def fade_msg(color1, color2=None, rise_time_ms=1000, fall_time_ms=1000):
	global __LED1__
	global __LED2__
	global __LED1_STEP__
	global __LED2_STEP__
	global __RISE__
	global __FALL__
	global __RISE_SCALE__
	global __FALL_SCALE__
	global __leds__
	global __timer__
	global __active__

	# Okay, we've got to do some serious figuring out to make a smooth transition to any color
	# We can't do any floating point arithmetic inside the IRQ, so instead we will multiply
	# all numbers by 1000, which will give us a little more resoltion
	__LED1__ = [0,0,0]
	__LED2__ = [0,0,0]
	__LED1_STEP__ = color1
	__LED2_STEP__ = color2 if color2 != None else color1
	__RISE__ = rise_time_ms
	__FALL__ = fall_time_ms
	__RISE_SCALE__ = rise_time_ms // 20
	__FALL_SCALE__ = fall_time_ms // 20
	#__leds__ = neopixel.NeoPixel(Pin(14),2)
	#__timer__ = Timer(1)
	#__timer__.init(period=20, mode=Timer.PERIODIC, callback=irq_fade_msg)
	__active__ = True
	
def irq_fade_msg(arg1):
	global __LED1__
	global __LED2__
	global __LED1_STEP__
	global __LED2_STEP__
	global __RISE__
	global __FALL__
	global __RISE_SCALE__
	global __FALL_SCALE__
	global __leds__
	global __timer__
	global __active__
	
	if __RISE__ > 20:
		__RISE__ = __RISE__ - 20
		__LED1__ = __LED1__ + __LED1_STEP__
		__LED2__ = __LED2__ + __LED2_STEP__
		__leds__[0] = __LED1__ // __RISE_SCALE__
		__leds__[1] = __LED2__ // __RISE_SCALE__		
	elif __FALL__ > 20:
		__FALL__ = __FALL__ - 20
		__LED1__ = __LED1__ - __LED1_STEP__
		__LED2__ = __LED2__ - __LED2_STEP__
		__leds__[0] = __LED1__ // __FALL_SCALE__
		__leds__[1] = __LED2__ // __FALL_SCALE__
	else:
		__leds__[0] = [0,0,0]
		__leds__[1] = [0,0,0]
		#__timer__.deinit()
		__active__ = False
	#__leds__.write()
	
	

def flash_msg(color1, color2=None, high_time_ms=500, low_time_ms=500, duration_ms=2000):
	if color2 == None:
		color2 = color1

def irq_flash_msg(arg1):
	pass
