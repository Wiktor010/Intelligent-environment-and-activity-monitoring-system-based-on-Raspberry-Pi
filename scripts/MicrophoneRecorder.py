import pyaudio
import wave
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time
import datetime
from scipy.io import wavfile
from scipy.signal import butter, filtfilt

class MicrophoneRecorder:
    def __init__(self, 
                 filename_prefix="nagranie", 
                 chunk=1024, 
                 format=pyaudio.paInt16, 
                 channels=1, 
                 rate=44100, 
                 duration=10,
                 noise_suppression=True, 
                 sound_boost=True, 
                 boost_factor=2.0):
        # Inicializacja parametrów nagrywania
        self.filename_prefix = filename_prefix # Prefiks do nazwy pliku -> "nagranie"
        self.chunk = chunk # Ile próbek dzwięku jest czytanych (jednorazowo) -> 1024
        self.format = format # Format dzwięku -> paInt16 (16-bitowy dzwięk)
        self.channels = channels # Liczba kanałów (1 = mono, 2 = stereo)
        self.rate = rate # Częstotliwość próbkowania -> 44100 [Hz]
        self.duration = duration # Czas nagrywania (dostosować do czasu trwania nagrywania z kamery!!)
        # Inicjalizacja parametrów filtracji
        self.noise_suppression = noise_suppression # Odcięcie szumów
        self.sound_boost = sound_boost # Podbicie dzwięku
        self.boost_factor = boost_factor # Wartość podbicia dzwięku
        # Inicializacja strumienia PyAudio
        self.p = pyaudio.PyAudio() 
        self.stream = None
        self.frames = [] # Lista do przechowywania danych dzwiękowych
        self.is_recording = False
        # Inicializacja ustawień wykresu
        self.audio_data = [] 
        self.time_stamps = []
        self.start_time = None  # Wyłapywanie momentu rozpoczęcia nagrywania
        #self.fig, self.ax = plt.subplots()
    # Definicja przetwarzania dzwięku
    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a
    def bandpass_filter(self, data, lowcut, highcut, fs):
        b, a = self.butter_bandpass(lowcut, highcut, fs)
        return filtfilt(b, a, data)
    def apply_noise_suppression(self, audio_data):
        if self.noise_suppression:
            lowcut = 300.0  # Dolna granica odcięcia szumów
            highcut = 3400.0  # Górna granica odcięcia szumów
            audio_data = self.bandpass_filter(audio_data, lowcut, highcut, self.rate)
        return audio_data
    def apply_sound_boost(self, audio_data):
        if self.sound_boost:
            audio_data *= self.boost_factor  # Boost sygnału audio
        return audio_data
    # Normalizacja amplitudy mocy sygnału audio z formatu pa.Int16 do wartości [-1 1]
    def amplitude_normalization(self, audio_data, ref=32768):
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
        return audio_data / ref
    # Wyrysowanie danych i zapis do pliku /uniknięcie konfliktu z GUI
    def plot_audio_after_recording(self):
        print(f"Rysowanie wykresu dla nagranego audio...")
        plt.figure() #figsize=(12, 6)
        plt.plot(self.time_stamps, self.audio_data)
        plt.title("Nagranie audio")
        plt.xlabel("Czas [s]")
        plt.ylabel("Amplituda")
        plt.grid(True)
        # Zapisanie wykresu do pliku
        plot_filename = self.filename.replace(".wav", "_plot.png")
        plt.savefig(plot_filename)
        print(f"Wykres zapisano jako: {plot_filename}")
        plt.show()
        plt.close()
    # Rozpoczęcie nagrywania audio z mikrofonu
    def start_recording(self):
        print("Rozpoczecie akwizycji danych z mikrofonu...")
        self.filename = self.generate_filename() # Wygenerowanie nazwy pliku zgodnie z "filename_prefix" tj. nagranie_RR-MM-DD_HH-M-SS.wav
        self.filtered_filename = self.filename.replace("nagranie", "f_nagranie") # Wygenerowanie nazwy pliku dla dzwięku po filtracji
        # Strumień audio otwarty
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        self.is_recording = True
        self.frames = []
        self.start_time = time.time()  # Wykrycie momentu rozpoczęcia nagrywania
        # Otworzenie wątku do rozpoczęcia nagrywania audio
        record_thread = threading.Thread(target=self.record_audio)
        record_thread.start()
        # Wywołanie funkcji rysowania wykresów
        #self.start_plotting()
    def record_audio(self):
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
                # Magazynowanie danych do wykresu
                normalized_data = self.amplitude_normalization(data)
                self.audio_data.extend(normalized_data)
                elapsed_time = time.time() - self.start_time
                self.time_stamps.extend(
                    np.linspace(elapsed_time - len(normalized_data) / self.rate, elapsed_time, len(normalized_data))
                )
                # if elapsed_time >= self.duration: # Wywołanie "stop_recording" gdy upłynie czas nagrywania
                #     self.stop_recording()
                #     break
            except Exception as e:
                print(f"Blad nagrywania: {e}")
                break
    # Zatrzymanie nagrywania
    def stop_recording(self):
        print(f"Nagrywanie zakonczone. Zapisywanie jako {self.filename}")
        if self.stream is not None: # Zamknięcie pętli strumienia
            self.stream.stop_stream()
            self.stream.close()
        self.is_recording = False
        # Zapisanie do pliku .wav
        with wave.open(self.filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))
        print(f"Audio zapisano jako {self.filename}")
        #self.save_live_plot()
        self.plot_data_ready = True # Dane gotowe do plotu
        # Filtracja dzwięku
        raw_audio_data = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        filtered_audio_data = self.apply_noise_suppression(raw_audio_data)
        filtered_audio_data = self.apply_sound_boost(filtered_audio_data)
        filtered_audio_data = np.clip(filtered_audio_data, -32768, 32767).astype(np.int16)
        # Zapisanie po filtracji do pliku .wav
        with wave.open(self.filtered_filename, 'wb') as wf_filtered:
            wf_filtered.setnchannels(self.channels)
            wf_filtered.setsampwidth(self.p.get_sample_size(self.format))
            wf_filtered.setframerate(self.rate)
            wf_filtered.writeframes(filtered_audio_data.tobytes())
        print(f"Audio po filtracji zapisano jako {self.filtered_filename}")   
    # Funkcja do zapisywania wykresu audio do pliku
    def save_live_plot(self):
        live_plot_name = self.filename.replace(".wav", "_live_plot.png")
        plt.figure(figsize=(12, 6))
        plt.plot(self.time_stamps, self.audio_data)
        plt.title("Nagranie audio")
        plt.xlabel("Czas [s]")
        plt.ylabel("Amplituda")
        plt.grid(True)
        plt.savefig(live_plot_name)
        print(f"Wykres zapisano jako: {live_plot_name}")
        plt.close()
    # Rysowanie wykresu
    def start_plotting(self):
        ani = FuncAnimation(self.fig, self.update_plot, interval=100, cache_frame_data=False)
        plt.show()  
    # Aktualizacja wykresu względem nowych danych
    def update_plot(self, frame):
        self.ax.clear()
        if self.is_recording: # Jeśli nagrywanie trwa, pokaż jedynie ostatnią sekundę 
            self.ax.plot(self.time_stamps[-self.rate:], self.audio_data[-self.rate:])
        else: # Jeśli nagrywanie się zakończyło, wyświetl wykres dla całego nagrania
            self.ax.plot(self.time_stamps, self.audio_data)
        # Edycja wykresu
        self.ax.set_title("Nagrywanie audio...")
        self.ax.set_xlabel("Czas [s]")
        self.ax.set_ylabel("Amplituda")
        self.ax.set_ylim([-1.1, 1.1])
        self.ax.grid(True)
        if not self.is_recording:
            self.ax.set_xlim([self.time_stamps[0], self.time_stamps[-1]])  # Dopasowanie osi czasu dla pełnego zestawu danych   
    # Wygenerowanie nazwy pliku zgodnie z datą oraz czasem nagrywania
    def generate_filename(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{self.filename_prefix}_{timestamp}.wav"
    # Zatrzymanie strumienia PyAudio
    def stop(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        print("Strumień audio zatrzymany.")
    # Analiza FFT
    def perform_fft_analysis(self):
        print("Analiza FFT nagranego pliku...")
        audio_data = np.frombuffer(b''.join(self.frames), dtype=np.int16)
        normalized_data = self.amplitude_normalization(audio_data)
        f = np.fft.rfftfreq(len(normalized_data), 1 / self.rate)
        power2db = 20 * np.log10(np.abs(np.fft.rfft(normalized_data))) # Moc w dB
        fft_plot_name = self.filename.replace(".wav", "_fft_plot.png")
        plt.figure()
        plt.plot(f[0:len(normalized_data)//2]/1e3,power2db[0:len(power2db)-1])
        plt.xlim([0, ((f[0:len(normalized_data)//2])[-1]) / 1e3])
        plt.title("Analiza FFT nagranego audio")
        plt.xlabel("Częstotliwość [kHz]")
        plt.ylabel("Amplituda [dB]")
        plt.grid(True)
        plt.savefig(fft_plot_name)
        print(f"Wykres analizy FFT zapisano jako {fft_plot_name}")
        plt.show()  
        plt.close() 

if __name__ == "__main__":
    FILENAME_PREFIX = "nagranie"
    DURATION = 10
    print(f"Rozpoczęcie nagrywania dźwięku na {DURATION} sekund...")
    recorder = MicrophoneRecorder(filename_prefix=FILENAME_PREFIX, duration=DURATION)
    recorder.start_recording()
    while recorder.is_recording:
        time.sleep(0.1)
    #if hasattr(recorder, 'plot_data_ready') and recorder.plot_data_ready:
        #recorder.save_live_plot()
    recorder.plot_audio_after_recording()
    print("Nagrywanie zakończone.")
    recorder.perform_fft_analysis()