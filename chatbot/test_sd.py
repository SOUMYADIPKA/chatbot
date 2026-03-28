import sounddevice as sd
import numpy as np
print('devices', sd.query_devices())
sd.default.device=(1, 3)
fs=16000
dur=3
print('recording')
rec=sd.rec(int(fs*dur), samplerate=fs, channels=1, dtype='int16')
sd.wait()
print('done', rec.shape)