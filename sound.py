"""
from IPython.display import Audio # awesome IPython tool to embed audio directly in the notebook
from scipy.signal import square
import math
import numpy as np

t = np.linspace(0, 0.1, 1000)
Audio(data=square(2 * math.pi * 100 * t), rate=5000, autoplay=True) 
"""
import time

import numpy as np
import pyaudio
from scipy.signal import square
import math 
import matplotlib.pyplot as plt

def play_square_sound_with_envelope(freq, duration, duty_cycle = 0.5, sample_freq=1000, envelope_duration=0.1):
    t = np.arange(0, duration, 1/sample_freq)
    s = square(2 * math.pi * freq * t, duty=duty_cycle) * (1 - np.exp(-t * envelope_duration))
    print(t)
    return t, s
    #display(Audio(s, rate=sample_freq))

p = pyaudio.PyAudio()

volume = 0.5  # range [0.0, 1.0]
#fs = 44100  # sampling rate, Hz, must be integer
#duration = 0.5  # in seconds, may be float
#f = 440.0  # sine frequency, Hz, may be float

# generate samples, note conversion to float32 array
#samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)
#samples = play_square_sound_with_envelope(freq=(10, 1000, 50), duration=(0.1, 0.5, 0.1), duty_cycle=(0.1, 0.9, 0.01), sample_freq=(10e3), envelope_duration=(0.1, 100, 0.1))
t, samples = play_square_sound_with_envelope(freq=50, duration=0.1, duty_cycle=0.01, sample_freq=1000, envelope_duration=0.1)
plt.plot(t, samples)
plt.show()


# per @yahweh comment explicitly convert to bytes sequence
output_bytes = (volume * samples).tobytes()

# for paFloat32 sample values must be in range [-1.0, 1.0]
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=1000, output=True)


# play. May repeat with different volume values (if done interactively)
start_time = time.time()
stream.write(output_bytes)
print("Played sound for {:.2f} seconds".format(time.time() - start_time))

stream.stop_stream()
stream.close()

p.terminate()