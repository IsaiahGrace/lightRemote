#! /usr/bin/env python3


#from os.path import getmtime

from colorsys import hsv_to_rgb
from rpi_ws281x import *
from random import randint
import json
import time
import signal
import sys
import os
import sched
import pprint
#from termcolor import colored    

#import stripDriver

class PiServer():
    # LED strip configuration:
    # NOTE: because of the drivers for the PWM module, this script MUST be run with administrator privileges
    #       I don't like it, but the driver needs to call mmap()
    # TODO: Should I use a different DMA channel for each LED strip?
    strips = {
        'external': {
            'COUNT'      : 150,     # Number of LED pixels. 36 on bottom, 38, on side, 150 total
            'PIN'        : 10,      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
            'FREQ_HZ'    : 800000,  # LED signal frequency in hertz (usually 800khz)
            'DMA'        : 10,      # DMA channel to use for generating signal (try 10)
            'BRIGHTNESS' : 255,     # Set to 0 for darkest and 255 for brightest
            'INVERT'     : False,   # True to invert the signal (when using NPN transistor level shift)
            'CHANNEL'    : 0,       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        },
        'top_fan': {
            'COUNT'      : 8,       # 8 LEDs on the top case fan
            'PIN'        : 18,      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
            'FREQ_HZ'    : 800000,  # LED signal frequency in hertz (usually 800khz)
            'DMA'        : 10,      # DMA channel to use for generating signal (try 10)
            'BRIGHTNESS' : 255,     # Set to 0 for darkest and 255 for brightest
            'INVERT'     : False,   # True to invert the signal (when using NPN transistor level shift)
            'CHANNEL'    : 0,       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        },
        'bottom_fan': {
            'COUNT'      : 8,       # 8 LEDs on the bottom case fan
            'PIN'        : 13,      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
            'FREQ_HZ'    : 800000,  # LED signal frequency in hertz (usually 800khz)
            'DMA'        : 10,      # DMA channel to use for generating signal (try 10)
            'BRIGHTNESS' : 255,     # Set to 0 for darkest and 255 for brightest
            'INVERT'     : False,   # True to invert the signal (when using NPN transistor level shift)
            'CHANNEL'    : 1,       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        }
    }
    
    signals = {
        'music': {
            'time': 0,
            'message': None
        },
        'reading': {
            'time': 0,
            'message': None
        },
        'fan': {
            'time': 0,
            'message': None
        }
    }

    SIGNAL_PATH = '/home/pi/lightRemote/pi/signals/'
    
    def __init__(self):
        self.scheduler = sched.scheduler(time.time, time.sleep)
        #                delay, priority
        self.scheduler.enter(1, 1, self.read_all_signals)
        

    def read_all_signals(self):
        # for each of the signal names, and their coresponding data dicts:
        for sig, sigData in self.signals.items():
            # Check if the file has been modified since we last looked
            if sigData['time'] != os.path.getmtime(self.SIGNAL_PATH + sig):
                # does mutating a Dict while iterating through it bork the universe?
                self.signals[sig]['message'] = self.read_signal(sig)
                self.signals[sig]['time'] = os.path.getmtime(self.SIGNAL_PATH + sig)

        # The scheduler is not periodic, so we have to re-schedule ourselves if we want to execute again
        self.scheduler.enter(1, 1, self.read_all_signals)

        
    def read_signal(self, signal):
        with open(self.SIGNAL_PATH + signal, "r") as f:
            message = json.load(f)
        return message

    
    def scheduler_status(self):
        # print out some status information
        print(self.scheduler.queue)
        #pprint.pprint(self.signals)
        
        
    
    
        
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        sys.stdout = open(os.devnull, 'w')

    server = PiServer()

    # The scheduler is blocking, so this is our infinite loop:
    server.scheduler.run()

