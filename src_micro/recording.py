import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

# List all devices to find the index of your USB microphone
print(sd.query_devices())

# Replace 1 with the index of your USB microphone
sd.default.device = (3, None)  # Input device, Output device (None if not needed)

# Configuration
SAMPLE_RATE = 44100  # Sampling rate in Hz
DURATION = 5         # Recording duration in seconds
BASE_FILE_NAME = "nagranie"  # Base name for output files
THRESHOLD = 0.02     # Sound amplitude threshold for triggering recording

def get_next_file_name(base_name, extension=".wav"):
    """
    Generates the next file name with an incremental number appended.
    Example: nagranie_1.wav, nagranie_2.wav, etc.
    """
    i = 1
    while True:
        file_name = f"{base_name}_{i}{extension}"
        if not os.path.exists(file_name):  # Check if file already exists
            return file_name
        i += 1

def wait_for_sound(threshold, duration, samplerate):
    print(f"Listening for sound above the threshold {threshold}...")
    with sd.InputStream(samplerate=samplerate, channels=1, dtype='float32') as stream:
        while True:
            # Read a small chunk of data to monitor the sound
            data, _ = stream.read(int(samplerate * 0.1))  # 0.1-second chunks
            amplitude = np.abs(data).mean()  # Compute the mean amplitude
            if amplitude > threshold:
                print(f"Sound detected! Amplitude: {amplitude:.4f}")
                return

def record_sound(duration, samplerate, output_file):
    print("Recording sound...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait for the recording to finish
    print("Recording finished.")

    # Save the recorded sound to a file
    write(output_file, samplerate, audio)
    print(f"Sound saved to {output_file}")

# Main logic
file_name = get_next_file_name(BASE_FILE_NAME)
wait_for_sound(THRESHOLD, DURATION, SAMPLE_RATE)
record_sound(DURATION, SAMPLE_RATE, file_name)
