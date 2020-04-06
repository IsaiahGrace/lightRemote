# Isaiah Grace
# 5 April 2020

from machine import Timer,Pin
import gc
import neopixel
import ujson

info_msg = 0
info_index = 0
leds = None
timer = None
active = False
info = []

# The info array is an array of arrays
# 0 - wakeup(slow green fade in)
# 1 - wifi-connected(flash green)
# 2 - no-wifi-found(flash red)
# 3 - mqtt-connected(flash gold)
# Each element of a msg array is a tuple of the LED color
#    ((r1,g1,b1),(r2,g2,b2))
# This allows any animation


def setup():
	# Sets up the timer based interrupt that will manage the lights
	# A period of 17ms means that every 60 updates will take 1020ms,
	# close enough to 60Hz refresh rate for me.
	global timer
	global info_index
	global info_msg
	global active
	global info
	global leds
	

	# Start the garbage collection
	gc.enable()

	with open('led_info_data','r') as info_f:
		info = ujson.load(info_f)

	leds = neopixel.NeoPixel(Pin(14),2)
	info_index = len(info[0]) - 1
	info_msg = 0
	tim = Timer(0)
	tim.init(period=17, mode=Timer.PERIODIC, callback=__irq_led_info_update)
	timer = tim
	active = True


def stop():
	global timer
	global leds
	global active

	if not active:
		print("ERROR, led_info module is not active")
		return

	# Turn off the led_info timer
	timer.deinit()

	# Turn off the LEDs
	leds[0] = (0,0,0)
	leds[1] = (0,0,0)
	
	leds.write()
	info = []
	leds = None

	# Do a garbage collection to hopefully get rid of the msg data
	gc.collect()
	active = False

	
def is_active():
	global active
	return active


def animation_done():
	global info_msg
	global info_index
	global info
	global active
	return True if not active or len(info[info_msg]) - 1 <= info_index else False


def send_msg(msg):
	# This function will initiate the message
	# msg must be an int, see above for valid values
	global info_msg
	global info_index
	global active

	if not active:
		print("ERROR, led_info module is not active")
		return

	if info_msg > len(info) - 1:
		print("ERROR, msg out of range. msg: " + msg + " len(info): " + len(info))
		raise ValueError

	
	info_msg = msg
	info_index = 0


def __irq_led_info_update(arg):
	# looks at two global variables:
    #    info_msg
    #    info_index
    # Should be executed at 60Hz
    # Will incriment index,
	# but will stop at the last entry
    # To send a new message, just set:
    #    info_msg = new value
    #    THEN
    #    info_index = 0
    # The last entry (info[*][-1]) should always be:
    #    ((0,0,0),(0,0,0))
    # will set the LEDs to the value specified by:
    # info[msg][index] = ((r1,g1,b1),(r2,g2,b2))

	global info
	global leds
	global info
	global info_msg
	global info_index
	global active
		
	leds[0] = info[info_msg][info_index]
	leds[1] = info[info_msg][info_index]
	
	leds.write()
	
	if info_index < len(info[info_msg]) - 1:
		info_index = info_index + 1

		
def self_test():
	global info

	start_mem = gc.mem_alloc()
	
	for i in range(10):
		stop()
		setup()
		
		assert is_active()
		assert animation_done()
	
		for msg in range(len(info)):
			send_msg(msg)
			assert not animation_done()
			while not animation_done():
				pass
			assert animation_done()

		stop()

		assert not is_active()
		assert animation_done()

	end_mem = gc.mem_alloc()
	print("start mem " + str(start_mem))
	print("end mem   " + str(end_mem))
