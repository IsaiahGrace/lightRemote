#! /usr/bin/env python3
# Isaiah Grace

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
from pprint import pprint as pp
from termcolor import colored    

import stripDriver


class FunctionArray():
    # The whole purpose of this class is so that I can store one of these objects as the signals['fan']['action'],
    # call that object, and then execute both fan music_effect functions
    def __init__(self, functions):
        self.functions = functions

    def __call__(self):
        for function in functions:
            function()
    

class PiServer():
    # LED strip configuration:
    # NOTE: because of the drivers for the PWM module, this script MUST be run with administrator privileges
    #       I don't like it, but the driver needs to call mmap()
    # TODO: Should I use a different DMA channel for each LED strip?
    strip_config = {
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

    strips = {
        'external'   : None,
        'top_fan'    : None,
        'bottom_fan' : None
    }
        
    signals = {
        'music': {
            'time': 0,
            'message': None,
            'action' : self.nop
        },
        'reading': {
            'time': 0,
            'message': None,
            'action' : self.nop
        },
        'fan': {
            'time': 0,
            'message': None,
            'action' : self.nop
        }
    }

    SIGNAL_PATH = '/home/pi/lightRemote/pi/signals/'
    
    def __init__(self, verbose):
        self.verbose = verbose
        
        for strip in self.strips:
            self.strips[strip] = stripDriver.StripDriver(strip_config[strip])

        self.scheduler = sched.scheduler(time.time, time.sleep)

        # These three variables will let us examine the timimg behaviour of our scheduler
        self.read_all_signals_time = time()
        self.signal_actions_time = time()
        self.refresh_strips_time = time()
        
        # Each of these functions schedule themselves after their execution,
        # so we just need to run them this first time, and they'll keep themselves running.
        self.read_all_signals()
        self.signal_actions()
        self.refresh_strips()
        
        if verbose:
            self.scheduler_status()
                
        
    def read_all_signals(self):
        curr_time = time()
        self.read_all_signals_delta = curr_time - self.read_all_signals_time
        self.read_all_signals_time = curr_time
        
        # for each of the signal names, and their coresponding data dicts:
        for sig, sigData in self.signals.items():
            # Check if the file has been modified since we last looked
            if sigData['time'] != os.path.getmtime(self.SIGNAL_PATH + sig):
                # does mutating a Dict while iterating through it bork the universe?
                self.signals[sig]['message'] = self.read_signal(sig)
                self.signals[sig]['time'] = os.path.getmtime(self.SIGNAL_PATH + sig)
                self.update_action(sig)
                
                if self.verbose:
                    print('Recieved', sig, 'signal')

        # The scheduler is not periodic, so we have to re-schedule ourselves if we want to execute again
        self.scheduler.enter(1, 1, self.read_all_signals)

        
    def read_signal(self, signal):
        with open(self.SIGNAL_PATH + signal, "r") as f:
            message = json.load(f)
        return message

    def update_action(self, sig):
        signal = self.signals[sig]

        if sig == 'music':
            if signal['message']['is_playing']:
                self.strips['external'].set_base_color_from_valence(signal['message']['valence'])
            else:
                self.strips['external'].set_base_color_from_RGB(0,0,0)
                
            self.signals[sig]['action'] = self.strips['external'].music_effect
                
        if sig == 'reading':
            pass
        
        if sig == 'fan':
            if signal['message']['fan_on']:
                if signal['message']['mode'] == 'MUSIC':
                    if self.signals['music']['message']['is_playing']:
                        self.strips['top_fan'].set_base_color_from_valence(self.signals['music']['message']['valence'])
                        self.strips['bottom_fan'].set_base_color_from_valence(self.signals['music']['message']['valence'])
                    else:
                        self.strips['top_fan'].set_base_color_from_RGB(0,0,0)
                        self.strips['bottom_fan'].set_base_color_from_RGB(0,0,0)

                    # See the wizardry above in the class FunctionArray.
                    # This creates a callable object that will in turn call these music_effect functions
                    self.signals[sig]['action'] = FunctionArray((self.strips['top_fan'].music_effect,
                                                                 self.strips.['bottom_fan'].music_effect))

                if signal['message']['mode'] == 'FX':
                    pass
                if signal['message']['mode'] == 'NOTIFY':
                    pass
                
            else:
                self.strips['top_fan'].clear()
                self.strips['bottom_fan'].clear()
                self.signals[sig]['action'] = self.nop
        
        
    def signal_actions(self):
        curr_time = time()
        self.signal_actions_delta = curr_time - self.signal_actions_time
        self.signal_actions_time = curr_time
        
        for signal in self.signals.items():
            signal['action']()

        self.scheduler.enter(0.1, 2, self.signal_actions)
        
    def refresh_strips(self):
        curr_time = time()
        self.refresh_strips_delta = curr_time - self.refresh_strips_time
        self.refresh_strips_time = curr_time

        for strip in self.strips.values():
            strip.refresh()
            
        self.scheduler.enter(0.1, 3, self.refresh_strips)
        
        
    def scheduler_status(self):
        # print out some status information
        print(self.scheduler.queue)
        print("read_all_signals :",self.read_all_signals_delta)
        print("signal_actions   :",self.signal_actions_delta)
        print("refresh_strips   :",self.refresh_strips_delta)

        self.scheduler.enter(2, 1, self.scheduler_status)
        

    def nop(self):
        # This is needed so that signal actions can always be callable even if there is nothing to do
        pass    
    
        
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        sys.stdout = open(os.devnull, 'w')

    server = PiServer(verbose=True)

    # The scheduler is blocking, so this is our infinite loop:
    server.scheduler.run()

