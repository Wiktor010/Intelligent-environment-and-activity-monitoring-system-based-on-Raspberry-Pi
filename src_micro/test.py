import sounddevice as sd
import numpy as np

sd.default.device = (1, None)  # Replace 1 with the index of your microphone

print("Recording for 5 seconds...")
duration = 5  # seconds
sample_rate = 44100  # Hz
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()
print("Recording complete.")
print("Recorded data shape:", np.shape(recording))
