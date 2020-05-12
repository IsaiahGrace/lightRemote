#! /usr/bin/env python

# Isaiah Grace
# May 11 2020

# This is an attempt to re-write the send_music_to_pi script with a sane ammount of bodging

import signal # Used to respond to Ctrl+C events
import sys
#import os
import time
import json # Used to convert Dict to Str so we can send a text file to the pi
from termcolor import colored
from pprint import pprint as pp

import "piCOM"
import "songData"
import "dbusManager"

PI_NAME = 'beacon'
PI_PATH = "/home/pi/lightRemote/pi/from_old_pi/lights/"

class AbstractFSM(): 
    def __init__(self):
        # This might call the AbstractFSM.IDLE() method, instead of the inhereted method...
        self.state = IDLE
   
    def step(self):
        self.state()

    def get_state(self):
        return self.state.__NAME__

    def IDLE(self):
        raise Error("IDLE() is abstract, you must overwrite it if inheriting from abstractFSM")

    def SHUTDOWN(self):
        raise Error("SHUTDOWN() is abstract, you must overwrite it if inheriting from abstractFSM")

    
class MusicFSM(AbstractFSM):
    def __init__(self):
        self.state = IDLE
        self.musicDbusManager = dbusManager.DbusManager()
        self.musicPiCOM = piCOM.PiCOM()
        self.musicSongData = songData.SongData()
        
    def IDLE(self):
        # Only leave IDLE state if spotify is open and we can contact the Pi
        if musicDbusManager.connect_to_spotify() and musicPiCOM.ping():
            self.state = SPOTIFY_PAUSED
        else:
            self.state = IDLE

    def SPOTIFY_PAUSED(self):
        if not musicDbusManager.isOpen():
            self.state = SHUTDOWN
        elif musicDbusManager.isPlaying():
            self.state = SPOTIFY_PLAYING
        else:
            self.state = SPOTIFY_PAUSED

    def NEW_SONG(self):
        # get song data
        musicSongData.set_playing_track()
        musicSongData.set_audio_features()
        
        # package up data for the pi
        message = json.dumps(musicSongData.get_audio_features())
        signal = "audio_features"
        
        # send the data to the pi
        musicPiCOM.sendSignal(signal, message)

        self.song_id = musicSongData.song_id()
        self.state = SPOTIFY_PLAYING
    
    def SPOTIFY_PLAYING(self):
        if not musicDbusManager.isPlaying():
            self.state = SHUTDOWN
        elif song_id != musicSongData.song_id():
            self.state = NEW_SONG
        else:
            self.state = SPOTIFY_PLAYING

    def SHUTDOWN(self):
        message = dict()
        message['is_playing'] = False
        signal = "audio_features"
        musicPiCOM.sendSignal(signal, message)
        self.state = IDLE

    
class ReadingFSM(AbstractFSM):
    def __init__(self):
        self.state = IDLE
        self.readingPiCOM = piCOM.PiCOM()
        self.timeout = 0
        
    def IDLE(self):
        self.state = IDLE
        # We've got to figure out how to initiate reading mode..

    def START_READING(self):
        message = dict()
        message['reading'] = True
        signal = 'reading'
        readingPiCOM.sendSignal(signal, message)
        self.state = READING
    
    def READING(self):
        # TODO: decriment timeout, maybe with time.time?
        if timeout == 0:
            self.state = SHUTDOWN
        else:
            self.state = READING

    def SHUTDOWN(self):
        message = dict()
        message['reading'] = False
        signal = 'reading'
        readingPiCOM.sendSignal(signal, message)
        self.state = IDLE


class FanFSM(AbstractFSM):
    def __init__(self):
        self.state = IDLE
        self.fanPiCOM = piCOM.PiCOM()

        # TODO: setup monitoring functions (callbacks? interrupts?) to signal a notification
        self.notification = None

        # TODO: setup a system to turn on music mode
        self.musicMode = False

        # TODO: setup a system to turn on FX mode
        self.fxMode = False
        self.fxNum = 0

        # TODO: setup a system to turn off the fan lights
        
    def IDLE(self):
        if self.notification != None:
            self.state = NOTIFY
        elif self.musicMode:
            self.state = MUSIC
        elif self.fxMode:
            self.state = FX
        elif self.shutdown:
            self.state = SHUTDOWN
        else:
            self.state = IDLE
            
    def MUSIC(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'MUSIC'
        signal = 'fan'
        fanPiCOM.sendSignal(signal, message)
        self.musicMode = False
        self.state = IDLE
    
    def FX(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'FX'
        message['FX'] = fxNum
        signal = 'fan'
        fanPiCOM.sendSignal(signal, message)
        self.fxMode = False
        self.state = IDLE


    def NOTIFY(self):
        message = dict()
        message['fan_on'] = True
        message['mode'] = 'FX'
        signal = 'fan'
        fanPiCOM.sendSignal(signal, message)
        self.state = IDLE
        pass
    
    def SHUTDOWN(self):
        message = dict()
        message['fan_on'] = False
        signal = 'fan'
        fanPiCOM.sendSignal(signal, message)
        self.state = IDLE
        

# This class is the top level controller for our FSMs that will coordinate the efforts of the other classes
class ControlFSM:
    def __init__(self):
        self.FSMs = [musicFSM(), readingFSM(), fanFSM()] #, fanFSM()] # maybe add another fanFSM to have seperate fan control?
        signal.signal(signal.SIGINT, handler_stop_signals)
        signal.signal(signal.SIGTERM, handler_stop_signals)

    def step(self):
        for FSM in FSMs:
            # Evaluate the FSM as many times as necessary so that a state repeats
            old_state = None
            while(FSM.get_state() != old_state):
                old_state = FSM.get_state()
                FSM.step()
                # That means that each element in the iterable FSMs must be a class with the step() function defined

    def handler_stop_signals(signum, frame):
        # shutdown all the lights
        for FSM in FSMs:
            FSM.SHUTDOWN()
        print(colored('SIGINT or SIGTERM, lights turning off','red'))
        sys.exit(0)
    

if __NAME__ == '__MAIN__':
    controlFSM = ControlFSM()
    while(True):
        controlFSM.step()
        time.sleep(1)
    
