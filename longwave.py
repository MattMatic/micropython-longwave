"""
Stuff to play long WAVE files.

2015-04-22 Matt Page
2015-04-26 Added replay ability

Double buffered, using a timer to reload the DAC and a poll function to
fill up the queue.
Works well with 200ms of audio, and polled at about 100ms

"""

import wave
import pyb
from pyb import DAC

class LongWave:
    """
    Callback for the timer.
    Switches buffers, and deactivates callback when nothing to do.
    Toggles should be interrupt-safe
    """
    def timer_callback(self, timer):
        self._have[self._doneindex]=False
        self._doneindex = (self._doneindex+1)%2        
        if (self._have[self._doneindex]):
            self._dac.write_timed(self._buf[self._doneindex], self._rate)
        else:
            self._doneindex=0
            timer.callback(None)
            self._running = False

    """
    Class variables:
    _f = wave file from wave.open
    _speed = Percent playback speed
    _rate = samples per second
    _amount = number of samples to take per chunk
    _freq = frequency of chunk switchover (4 Hertz)
    _dac = DAC object
    _have = whether we have chunks 1 and/or 2
    _buf = the buffers of samples
    _doneindex = which chunk (0 or 1) that's been completed
    _timer = timer object
    _running = whether the timer is running
    """
    def __init__(self, dac=DAC(1), timerno=4):
        global lwr
        lwr = self
        self._f = None
        self._rate = 0
        self._amount = 0
        self._freq = 4 # in Hertz
        self._dac = dac
        self._have = [False,False]
        self._buf = [None,None]
        self._doneindex = 0
        self._speed = 100
        self._timer = pyb.Timer(timerno, freq=self._freq)
        self._running = False
        self._fill()

    def __del__(self):
        self._timer.callback(None)
        self._f.close()

    def _read(self):
        return self._f.readframes(self._amount)

    """
    Fill one or two buffers if needed.
    If timer callback is not running, then kick off the timer again
    """
    def _fillbuf(self, which=0):
        if (not self._have[which]):
            self._buf[which] = self._read()
            self._have[which] = True
            
    def _fill(self):
        if (not self._f):
            return
            
        if (not self._have[0]) and (not self._have[1]):
            self._doneindex = 0
        
        self._fillbuf(0)
        self._fillbuf(1)
            
        if (not self._running):
            self._dac.write_timed(self._buf[0], self._rate)
            self._timer.callback(self.timer_callback)
            self._running = True
        
    """
    Call this regularly (faster than the buffer rate of 5Hz)
    """
    def poll(self):
        self._fill()
        
    def play(self, filename, speed=100):
        if (self._f):
            self._f.close()
        #print('Playing ',filename)
        self._have[0] = False
        self._have[1] = False
        self._running = False
        self._speed = speed
        self._f = None
        self._f = wave.open(filename)
        self._rate = (self._f.getframerate() * self._speed) // 100
        self._amount = self._rate // self._freq
        self._fill()
        
