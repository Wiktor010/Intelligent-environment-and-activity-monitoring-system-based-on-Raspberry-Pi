import tkinter as tk            # Add library for GUI
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import cv2
#matplotlib.use('TkAgg')  # Backend kompatybilny z Tkinter
from PIL import Image, ImageTk, ImageDraw

try:
    from camera import PiCameraDisplay
except ModuleNotFoundError: 
    from scripts.camera import PiCameraDisplay   
try:
    from scripts.sql import SensorDataHandler
except ModuleNotFoundError:
    from sql import SensorDataHandler

try:
    from scripts.globals import Globals
except ModuleNotFoundError:
    from globals import Globals

try:
    from scripts.sensors_handling import Sensors
except ModuleNotFoundError:
    from sensors_handling import Sensors

try:
    from scripts.MicrophoneRecorder import MicrophoneRecorder
except ModuleNotFoundError:
    from MicrophoneRecorder import MicrophoneRecorder

class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor App")
        self.root.geometry("1280x720")  # Ustawia rozmiar okna (szerokość x wysokość)
        # self.root.attributes('-fullscreen', True)

        # Notebook (zakładki)
        self.notebook = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.tab3 = ttk.Frame(self.notebook)

        self.notebook.add(self.tab1, text = "Dane i Kamera")
        self.notebook.add(self.tab2, text = "Wykresy")
        self.notebook.add(self.tab3, text = "Analiza nagrań audio")
        self.notebook.pack(expand=True, fill="both")

        self.normalized_filtered_audio_data = []
        self.time_stamps = []
        self.fft_freq = []
        self.fft_amp = []
        self.after_record = False

        # Zakładka 1: Dane i kamera
        self.setup_tab1()

        # Zakładka 2: Wykresy
        self.setup_tab2()

        # Zakładka 3: Analiza nagrań audio
        self.setup_tab3()

        self.g = Globals()

        # Utwórz instancję klasy kamery
        try:
            self.camera_display = PiCameraDisplay()
        except Exception as e:
            print(f"Nie można zainicjować kamery: {e}")
            self.camera_display = None  # Ustaw na None, jeśli kamera nie jest dostępna

        try:
            self.sql_data_handling = SensorDataHandler()
        except Exception as e:
            print(f"Nie można zainicjować klasy bazy danych: {e}")
            self.sql_data_handling = None

        try:
            self.microphone = MicrophoneRecorder()
        except Exception as e:
            self.microphone = None
            print(f"Nie można zainicjować klasy mikrofonu: {e}")

        # Uruchom aktualizację danych 
        self.update_data()
        self.start_camera()
        self.check_to_update_plots()

    def setup_tab1(self):
        self.data_frame = tk.Frame(self.tab1)
        self.data_frame.pack(side="left", padx=15, pady=15)

        for i in range(2):
            self.data_frame.columnconfigure(2, weight = 1, uniform = "col")
        
        for i in range(4):
            self.data_frame.rowconfigure(i, weight = 1, uniform = "row")
        
        # Ikony i etykiety dla danych
        self.icons = {
            "temperatura": ImageTk.PhotoImage(Image.open("icons/thermometer.png").resize((100, 100))),
            "cisnienie": ImageTk.PhotoImage(Image.open("icons/pressure.png").resize((100, 100))),
            "wilgotnosc": ImageTk.PhotoImage(Image.open("icons/humidity.png").resize((100, 100))),
            "natezenie_swiatla": ImageTk.PhotoImage(Image.open("icons/light_intensity.png").resize((100, 100))),
        }

        self.labels = {}
        for i, key in enumerate(["temperatura", "cisnienie", "wilgotnosc", "natezenie_swiatla"]):
            tk.Label(self.data_frame, image=self.icons[key]).grid(row=i, column=0, padx=5, pady=5)
            self.labels[key] = tk.Label(self.data_frame, text="---", font=("Arial", 24))
            self.labels[key].grid(row=i, column=1, padx=5, pady=5)

        # Obraz z kamery
        self.camera_frame = tk.Frame(self.tab1)
        self.camera_frame.pack(side="right", padx=15, pady=15)
        self.camera_label = tk.Label(self.camera_frame)
        self.camera_label.pack()

        # # Closing GUI button
        # tk.Button(self.data_frame, text = "Zamknij", font = ("Arial", 12), command = self.root.destroy).pack(side = "bottom", padx = (20, 20), pady = 20)

    def setup_tab2(self):
        # Ustawienia kontenera dla wszystkich elementów
        self.tab2_frame = tk.Frame(self.tab2)
        self.tab2_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Sekcja wyboru zakresu dat i przycisku (na górze)
        self.date_frame = tk.Frame(self.tab2_frame)
        self.date_frame.pack(pady=10)

        tk.Label(self.date_frame, text="Od:").pack(side="left", padx=5)
        self.start_date = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")
        self.start_date.pack(side="left", padx=5)

        tk.Label(self.date_frame, text="Do:").pack(side="left", padx=5)
        self.end_date = DateEntry(self.date_frame, date_pattern="yyyy-mm-dd")
        self.end_date.pack(side="left", padx=5)

        self.fetch_button = tk.Button(self.date_frame, text="Pobierz dane", command=self.update_plots_by_date)
        self.fetch_button.pack(side="left", padx=10)

        # Wykresy w dwóch rzędach po dwa (poniżej dat i przycisku)
        self.plot_frame = tk.Frame(self.tab2_frame)
        self.plot_frame.pack(expand=True, fill="both")

        self.figure, self.axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.5, 'wspace': 0.3})
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")


    def setup_tab3(self):
        # Ustawienia kontenera dla wszystkich elementów
        self.tab3_frame = tk.Frame(self.tab3)
        self.tab3_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Wykresy w dwóch rzędach po dwa (poniżej dat i przycisku)
        self.plot_frame1 = tk.Frame(self.tab3_frame)
        self.plot_frame1.pack(expand=True, fill="both")

        self.figure1, self.axs1 = plt.subplots(1, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.5, 'wspace': 0.3})
        self.figure1.tight_layout()
        self.canvas1 = FigureCanvasTkAgg(self.figure1, self.plot_frame1)
        self.canvas1.get_tk_widget().pack(expand=True, fill="both")


    def update_data(self):
        database_choice = 'test'  # Wybór bazy danych
        if self.sql_data_handling:
            self.sql_data_handling.fetch_latest_sensor_data(database_choice)

        if self.g.sensor_temperature is not None:
            self.labels["temperatura"].config(text=f"{self.g.sensor_temperature:.2f} °C")
        else:
            self.labels["temperatura"].config(text="Brak danych")

        if self.g.sensor_pressure is not None:
            self.labels["cisnienie"].config(text=f"{self.g.sensor_pressure:.2f} hPa")
        else:
            self.labels["cisnienie"].config(text="Brak danych")

        if self.g.sensor_humidity is not None:
            self.labels["wilgotnosc"].config(text=f"{self.g.sensor_humidity:.2f} %")
        else:
            self.labels["wilgotnosc"].config(text="Brak danych")

        if self.g.sensor_light_intensity is not None:
            self.labels["natezenie_swiatla"].config(text=f"{self.g.sensor_light_intensity:.2f} lx")
        else:
            self.labels["natezenie_swiatla"].config(text="Brak danych")

        self.root.after(1000, self.update_data)  # Aktualizacja danych co 1 sekundę

    def start_camera(self):
        if self.camera_display:
            try:
                frame = self.camera_display.get_frame()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            except Exception as e:
                print(f"Błąd przy uzyskiwaniu klatki z kamery: {e}")

        self.root.after(30, self.start_camera)  # Odświeżanie co 30 ms

    def check_to_update_plots(self):
        if self.after_record:
            self.update_audio_analysis()
            self.after_record = False

        self.root.after(1000, self.check_to_update_plots)

    def update_plots_by_date(self):
        start_date = self.start_date.get_date()
        end_date = self.end_date.get_date()

        if self.sql_data_handling:
            data = self.sql_data_handling.fetch_data_by_date(start_date, end_date)
            if data:
                # Przetwarzanie danych i rysowanie wykresów
                self.draw_plots(data)
            else:
                print("Brak danych dla wybranego zakresu dat.")

    def draw_plots(self, data):
        for ax in self.axs.flat:
            ax.clear()

        timestamps = [row['timestamp'] for row in data]
        temperatures = [row['temperature'] for row in data]
        pressures = [row['pressure'] for row in data]
        humidities = [row['humidity'] for row in data]
        light_intensities = [row['light_intensity'] for row in data]

        self.axs[0, 0].plot(timestamps, temperatures, label='Temperatura')
        self.axs[0, 1].plot(timestamps, pressures, label='Ciśnienie')
        self.axs[1, 0].plot(timestamps, humidities, label='Wilgotność')
        self.axs[1, 1].plot(timestamps, light_intensities, label='Natężenie światła')

        for ax in self.axs.flat:
            ax.legend()
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.tick_params(axis='x', rotation=45)

        self.canvas.draw()

    def update_audio_analysis(self):
        if self.microphone:
            self.microphone.process_audio()
            self.normalized_filtered_audio_data = self.microphone.get_filtered_audio()
            self.fft_freq, self.fft_amp = self.microphone.get_fft()

        self.axs1[0].clear()
        self.axs1[0].plot(self.normalized_filtered_audio_data, label='Przefiltrowane dane audio')
        self.axs1[0].legend()

        self.axs1[1].clear()
        self.axs1[1].plot(self.fft_freq, self.fft_amp, label='Widmo FFT')
        self.axs1[1].legend()

        self.canvas1.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.mainloop()
