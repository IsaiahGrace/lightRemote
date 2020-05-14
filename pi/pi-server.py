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
#from termcolor import colored    

import stripDriver


class FunctionArray():
    # The whole purpose of this class is so that I can store one of these objects as the signals['fan']['action'],
    # call that object, and then execute both fan music_effect functions
    def __init__(self, functions):
        self.functions = functions

    def __call__(self):
        for function in self.functions:
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
            'mtime': 0,
            'message': None,
            'action' : None
        },
        'reading': {
            'mtime': 0,
            'message': None,
            'action' : None
        },
        'fan': {
            'mtime': 0,
            'message': None,
            'action' : None
        }
    }

    deltas = {
        'read_all_signals' : {
            'time'    : 0,
            'delta'   : 0,
            'duration': 0,
            'delay'   : 1
            },
        'signal_actions'   : {
            'time'    : 0,
            'delta'   : 0,
            'duration': 0,
            'delay'   : 0.1
            },
        'refresh_strips'   : {
            'time'    : 0,
            'delta'   : 0,
            'duration': 0,
            'delay'   : 0.1
            }
    }
    
    SIGNAL_PATH = '/home/pi/lightRemote/pi/signals/'
    
    def __init__(self, verbose=False, timing=False, printout=False):
        self.verbose = verbose
        self.timing = timing
        self.printout = printout

        for signal in self.signals:
            self.signals[signal]['action'] = self.nop
        
        for strip in self.strips:
            self.strips[strip] = stripDriver.StripDriver(self.strip_config[strip])

        self.scheduler = sched.scheduler(time.time, time.sleep)
        
        # Each of these functions schedule themselves after their execution,
        # so we just need to run them this first time, and they'll keep themselves running.
        self.read_all_signals()
        self.signal_actions()
        self.refresh_strips()
        
        if self.timing:
            self.scheduler_status()

        if self.printout:
            self.print_colors()
                
        
    def read_all_signals(self):
        self.update_delta('read_all_signals')
        
        # for each of the signal names, and their coresponding data dicts:
        for sig, sigData in self.signals.items():
            # Check if the file has been modified since we last looked
            if sigData['mtime'] != os.path.getmtime(self.SIGNAL_PATH + sig):
                # does mutating a Dict while iterating through it bork the universe?
                self.signals[sig]['message'] = self.read_signal(sig)
                self.signals[sig]['mtime'] = os.path.getmtime(self.SIGNAL_PATH + sig)
                self.update_action(sig)
                
                if self.verbose:
                    print('Recieved', sig, 'signal')

        # The scheduler is not periodic, so we have to re-schedule ourselves if we want to execute again
        self.scheduler.enter(self.deltas['read_all_signals']['delay'], 1, self.read_all_signals)

        
    def read_signal(self, signal):
        with open(self.SIGNAL_PATH + signal, "r") as f:
            message = json.load(f)
        return message

    def update_action(self, sig):
        if sig == 'music':
            if self.signals['music']['message']['is_playing']:
                self.strips['external'].set_base_color_from_valence(self.signals['music']['message']['valence'])
                self.strips['external'].tolerance = 50
                self.strips['external'].mutation_rate = 100
            else:
                self.strips['external'].set_base_color_from_RGB(0,0,0)
                self.strips['external'].tolerance = 0
                self.strips['external'].mutation_rate = 0
                
            self.signals['music']['action'] = self.strips['external'].music_effect
                
        if sig == 'reading':
            pass

        # The monsterous OR part of this if makes sure we update the fan valence when a new song starts
        if sig == 'fan' or self.signals['fan']['message']:
            if self.signals['fan']['message']['fan_on']:
                if self.signals['fan']['message']['mode'] == 'MUSIC':
                    if self.signals['music']['message']['is_playing']:
                        self.strips['top_fan'].set_base_color_from_valence(self.signals['music']['message']['valence'])
                        self.strips['top_fan'].tolerance = 20
                        self.strips['top_fan'].mutation_rate = 100
                        self.strips['bottom_fan'].set_base_color_from_valence(self.signals['music']['message']['valence'])
                        self.strips['bottom_fan'].tolerance = 20
                        self.strips['bottom_fan'].mutation_rate = 100
                    else:
                        self.strips['top_fan'].set_base_color_from_RGB(0,0,0)
                        self.strips['top_fan'].tolerance = 0
                        self.strips['top_fan'].mutation_rate = 0
                        self.strips['bottom_fan'].set_base_color_from_RGB(0,0,0)
                        self.strips['bottom_fan'].tolerance = 0
                        self.strips['bottom_fan'].mutation_rate = 0

                    # See the wizardry above in the class FunctionArray.
                    # This creates a callable object that will in turn call these music_effect functions
                    self.signals['fan']['action'] = FunctionArray((self.strips['top_fan'].music_effect,
                                                                 self.strips['bottom_fan'].music_effect))

                if self.signals['fan']['message']['mode'] == 'FX':
                    pass
                if self.signals['fan']['message']['mode'] == 'NOTIFY':
                    pass
                
            else:
                self.strips['top_fan'].clear()
                self.strips['bottom_fan'].clear()
                self.signals['fan']['action'] = self.nop
        
        
    def signal_actions(self):
        self.update_delta('signal_actions')

        for signal in self.signals:
            self.signals[signal]['action']()

        self.scheduler.enter(self.deltas['signal_actions']['delay'], 2, self.signal_actions)
        
    def refresh_strips(self):
        # I'd love to get my own function name during runtime programatically,
        # But you can't do that in Python! (without bodging the stack)
        self.update_delta('refresh_strips')
        
        for strip in self.strips.values():
            strip.refresh()
            
        self.scheduler.enter(self.deltas['refresh_strips']['delay'], 3, self.refresh_strips)
        

    def update_delta(self, name):
        if not self.timing:
            return
        
        curr_time = time.time()
        # The time since we last called this function:
        self.deltas[name]['delta'] = curr_time - self.deltas[name]['time']
        # The time the last function call took to execute (delta - delay)
        self.deltas[name]['duration'] = self.deltas[name]['delta'] - self.deltas[name]['delay']
        self.deltas[name]['time'] = curr_time
        
            
    def scheduler_status(self):
        # print out some status information
        #pp(self.scheduler.queue)
        pp(self.deltas)
        #for delta in self.deltas:
        #    print(delta, ":", self.deltas[delta]['delta'])

        self.scheduler.enter(2, 1, self.scheduler_status)
        

    def print_colors(self):
        message = ''
        for strip in self.strips:
            message = message + strip + '\n' + self.strips[strip].print_colors() + '\n'

        with open(self.SIGNAL_PATH + 'printout','w') as f:
            f.write(message)
            
        self.scheduler.enter(1, 1, self.print_colors)

        
    def nop(self):
        # This is needed so that signal actions can always be callable even if there is nothing to do
        pass    
    
        
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '-q':
        sys.stdout = open(os.devnull, 'w')

    server = PiServer(timing=False, verbose=True, printout=True)

    # The scheduler is blocking, so this is our infinite loop:
    server.scheduler.run()

