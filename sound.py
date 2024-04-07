import time
import soundfile  # pip install soundfile
import tcod.sdl.audio

step_cnt = 0
device = tcod.sdl.audio.open()  # Open the default output device.

step_sounds = []
for i in range(1, 6):
    sound, sample_rate = soundfile.read("audio/stony_step_" + str(i) + ".wav", dtype="float32")  # Load an audio sample using SoundFile.
    step_sounds.append(device.convert(sound, sample_rate))  # Convert this sample to the format expected by the device.

sound, sample_rate = soundfile.read("audio/floating.wav", dtype="float32")  # Load an audio sample using SoundFile.
floating_music = (device.convert(sound, sample_rate))  # Convert this sample to the format expected by the device.

def step(step_cnt):

    if device.queued_samples == 0:
        device.queue_audio(step_sounds[step_cnt % 5])  # Play audio synchronously by appending it to the device buffer.
        return step_cnt + 1

    return step_cnt

def background_music():

    if device.queued_samples == 0:
        device.queue_audio(floating_music)  # Play audio synchronously by appending it to the device buffer.

##########################