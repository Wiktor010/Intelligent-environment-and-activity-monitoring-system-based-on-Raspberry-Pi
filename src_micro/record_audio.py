import sounddevice as sd
from scipy.io.wavfile import write

# Konfiguracja nagrywania
SAMPLE_RATE = 44100  # Częstotliwość próbkowania (Hz)
DURATION = 5         # Czas nagrywania w sekundach
OUTPUT_FILE = "nagranie.wav"  # Nazwa pliku wyjściowego

def nagraj_dzwiek():
    print("Nagrywanie dźwięku...")
    # Rozpocznij nagrywanie
    dzwiek = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()  # Czekaj aż nagrywanie się zakończy
    print("Nagrywanie zakończone.")
    
    # Zapisz nagrany dźwięk do pliku .wav
    write(OUTPUT_FILE, SAMPLE_RATE, dzwiek)
    print(f"Dźwięk zapisany w pliku {OUTPUT_FILE}")

# Wywołaj funkcję nagrywającą
nagraj_dzwiek()
