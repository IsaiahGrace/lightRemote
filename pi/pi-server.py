#! /usr/bin/env python3

from time import time, ctime, sleep
from os.path import getmtime
from json import loads
from colorsys import hsv_to_rgb
from rpi_ws281x import *
from random import randint
import signal
import sys
import os
import threading
#from termcolor import colored    


class PiServer():
    # LED strip configuration:
    LED_COUNT      = 150     # Number of LED pixels. 36 on bottom, 38, on side, 150 total
    LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    signals = ['music', 'reading', 'fan']
    
    def __init__(self):
        pass

    def read_signal(self, signal):
        with open("./signals/" + signal, "r") as f:
            message = json.loads(f)
        return message
    
    def status(self):
        pass

    
    
        
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        sys.stdout = open(os.devnull, 'w')

    server = PiServer()

    while(True):
        PiServer.status()
        sleep(1)

