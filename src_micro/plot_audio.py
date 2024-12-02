import wave
import numpy as np
import matplotlib.pyplot as plt

# Replace 'yourfile.wav' with the path to your .wav file
wav_file = 'test3.wav'

# Open the .wav file
with wave.open(wav_file, 'r') as wav:
    # Extract parameters
    n_channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    frame_rate = wav.getframerate()
    n_frames = wav.getnframes()
    
    # Print file info
    print(f"Channels: {n_channels}")
    print(f"Sample Width: {sample_width} bytes")
    print(f"Frame Rate: {frame_rate} Hz")
    print(f"Total Frames: {n_frames}")
    
    # Read frames and convert to numpy array
    frames = wav.readframes(n_frames)
    audio_data = np.frombuffer(frames, dtype=np.int16)

# Create time axis for plotting
time = np.linspace(0, n_frames / frame_rate, num=n_frames)

# Plot the waveform
plt.figure(figsize=(12, 6))
plt.plot(time, audio_data)
plt.title("Waveform of " + wav_file)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid()
plt.show()
