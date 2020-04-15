import epaper1in54
from machine import SPI,Pin

#spi = SPI(3, SPI.MASTER, baudrate=2000000, polarity=0, phase=0)
spi = SPI(1,baudrate=2000000, polarity=0, phase=0, sck=Pin(14),mosi=Pin(13),miso=Pin(12))
cs = Pin(21)
dc = Pin(17)
rst = Pin(19)
busy = Pin(5)

e = epaper1in54.EPD(spi, cs, dc, rst, busy)
e.init()

w = 200
h = 200
x = 0
y = 0

# --------------------

# write hello world with black bg and white text
#from image_dark import hello_world_dark
#e.clear_frame_memory(b'\xFF')
#e.set_frame_memory(hello_world_dark, x, y, w, h)
#e.display_frame()

# --------------------

# write hello world with white bg and black text
#from image_light import hello_world_light
#e.clear_frame_memory(b'\xFF')
#e.set_frame_memory(hello_world_light, x, y, w, h)
#e.display_frame()

# --------------------

# clear display
e.clear_frame_memory(b'\xFF')
e.display_frame()

# use a frame buffer
# 200 * 200 / 8 = 4736 - thats a lot of pixels
import framebuf
buf = bytearray(200 * 200 // 8)
fb = framebuf.FrameBuffer(buf, 200, 200, framebuf.MONO_HLSB)
black = 0
white = 1
fb.fill(white)
#fb.text('Hello World',30,0,black)
#fb.pixel(30, 10, black)
#fb.hline(30, 30, 10, black)
#fb.vline(30, 50, 10, black)
#fb.line(30, 70, 40, 80, black)
#fb.rect(30, 90, 10, 10, black)
fb.fill_rect(1, 0, 8, 8, black)

from uos import urandom
import color_name

for row in range(0,25):
	fb.text(str('{:02d}'.format(row)),10,row*8,black)

	fb.rect(1,row*8,8,8,black)
	rand_color = urandom(3)
	rand_color_name = color_name.ColorNames.findNearestWebColorName(rand_color)
	fb.text(rand_color_name,30,row*8,black)
	print(list(rand_color),rand_color_name)
	
e.set_frame_memory(buf, x, y, w, h)
e.display_frame()


## NEW Landscape mode
'''
h = 200;  w = 200 # e-paper heigth and width.

buf_black        = bytearray(w * h // 8) # used by frame buffer (landscape)
buf_epaper_black = bytearray(w * h // 8) # used to display on e-paper after bytes have been

#import framebuf
fb_black = framebuf.FrameBuffer(buf_black, w, h, framebuf.MONO_VLSB)

#clear red & black screens, write in black on top left and in red bootom right
fb_black.fill(white)
fb_black.text('Hello world!', 20, 20,black)

# Move frame buffer bytes to e-paper buffer to match e-paper bytes oranisation.
# That is landscape mode to portrait mode. (for red and black buffers)
n = 0
for i in range(0, 25):
    for j in range(0, 200):
        m = (n-x)+(n-y)*24
        buf_epaper_black[m] = buf_black[n]
        n +=1
    x = n+i+1
    y = n-1

print('Sending to display')
e.set_frame_memory(buf_epaper_black,0,0,200,200)
e.display_frame()
print('Done!.......')
'''
