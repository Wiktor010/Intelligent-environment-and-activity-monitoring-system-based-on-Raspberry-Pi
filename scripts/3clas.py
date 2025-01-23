import os
import cv2
import time
import pyaudio
import wave
import numpy as np
from scipy.signal import butter, lfilter
from threading import Thread
from datetime import datetime

# Helper functions for audio processing
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

class AudioRecorder(Thread):
    def __init__(self, output_dir):
        super().__init__()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.output_dir = output_dir
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.running = False

    def run(self):
        self.stream = self.audio.open(format=self.format, channels=self.channels,
                                      rate=self.rate, input=True, frames_per_buffer=self.chunk)
        self.running = True
        print("Audio recording started.")

        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

    def stop(self):
        self.running = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        # Save raw audio
        raw_audio_path = os.path.join(self.output_dir, f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
        with wave.open(raw_audio_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

        print(f"Audio recording saved to {raw_audio_path}.")

class VideoRecorder(Thread):
    def __init__(self, output_dir):
        super().__init__()
        self.output_dir = output_dir
        self.camera = cv2.VideoCapture(0)
        self.running = False
        self.video_writer = None

    def run(self):
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_path = os.path.join(self.output_dir, f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
        frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))
        self.running = True
        print("Video recording started.")

        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                break

            # Show frame with simple rectangle (example for future object tracking)
            cv2.rectangle(frame, (50, 50), (200, 200), (0, 255, 0), 2)
            cv2.imshow('Video Stream', frame)
            self.video_writer.write(frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False

    def stop(self):
        self.running = False
        self.camera.release()
        self.video_writer.release()
        cv2.destroyAllWindows()
        print("Video recording stopped.")

class RecorderManager:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.audio_recorder = AudioRecorder(output_dir)
        self.video_recorder = VideoRecorder(output_dir)

    def start_recording(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.audio_recorder.start()
        self.video_recorder.start()
        print("Recording started.")

    def stop_recording(self):
        self.audio_recorder.stop()
        self.video_recorder.stop()
        print("Recording stopped.")

if __name__ == "__main__":
    output_dir = "./recordings"
    manager = RecorderManager(output_dir)

    try:
        manager.start_recording()
        time.sleep(10)  # Simulate recording duration
    except KeyboardInterrupt:
        print("Recording interrupted by user.")
    finally:
        manager.stop_recording()
