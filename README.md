# micropython-longwave
WAV player for MicroPython board

Uses double buffered approach to load chunks of samples.
Needs to be polled frequently so the chunks can be refreshed.

# Usage
    from longwave import LongWave
    lw = LongWave() # Default uses DAC1 and Timer4
    lw.play('hisnibs.wav')

    lw.play('hisnibs.wav', 120) # 120% speed

(Make sure you call lw.poll() at least every 100ms)

# History
2015-04-26 Initial upload
