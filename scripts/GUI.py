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
        self.canvas = FigureCanvasTkAgg(self.figure1, self.plot_frame1)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")


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

        # Zaplanuj aktualizację co 15 sekund
        self.root.after(2000, self.update_data)

    def start_camera(self):
        """Uruchamia podgląd z kamery."""
        self.update_camera()

    def update_camera(self):
        
        # Sprawdź, czy kamera została poprawnie zainicjalizowana
        if self.camera_display is not None:
            try:
                frame = self.camera_display.get_processed_frame()
                if frame is not None:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = ImageTk.PhotoImage(Image.fromarray(frame))
                    self.camera_label.imgtk = img
                    self.camera_label.configure(image=img)
            except Exception as e:
                print(f"Błąd kamery: {e}")
                img = self.create_placeholder_image()
                self.camera_label.imgtk = img
                self.camera_label.configure(image=img)
        else:
            print(f"Nie podłączono kamery")
            img = self.create_placeholder_image()
            self.camera_label.imgtk = img
            self.camera_label.configure(image=img)

        # Zaplanuj kolejną aktualizację po 100 ms
        self.root.after(100, self.update_camera)

    def create_placeholder_image(self):
        # Tworzenie pustego obrazu (szary prostokąt jako placeholder)
        empty_image = Image.new("RGB", (1200, 628), color="gray")
        draw = ImageDraw.Draw(empty_image)
        draw.text((20, 220), "Brak obrazu z kamery", fill="white")
        return ImageTk.PhotoImage(empty_image)

    def update_plots(self):
        database_choice = 'test'
        try:
            temperatures, pressures, humidities, light_intensities, timestamps = self.sql_data_handling.fetch_all_sensor_data(database_choice)
            self.plot_sensor_data(timestamps, temperatures, pressures, humidities, light_intensities)
        except Exception as e:
            print(f"Błąd podczas aktualizacji wykresów: {e}")

    def plot_microphone_data(self, timestamps, data1, data2):
        # Indeksy pomiarów
        indices1 = list(range(1,len(data1)+1))
        indices2 = list(range(1,len(data2)+1))
        # Czyszczenie istniejących wykresów
        for ax in self.axs1.flatten():
            ax.clear()

        self.axs1[0,0].plot(timestamps, data1, marker = 'o', label = "", color = 'red')
        self.axs1[0,0].set_title("")
        self.axs1[0,0].grid(True)
        self.axs1[0,0].set_xlabel("Timestamp")
        self.axs1[0,0].set_ylabel("Amplituda")
        self.axs1[0,0].xaxis.set_major_locator(MaxNLocator(5))

        self.axs1[0,1].plot(timestamps, data2, marker = 'o', label = "", color = 'red')
        self.axs1[0,1].set_title("")
        self.axs1[0,1].grid(True)
        self.axs1[0,1].set_xlabel("Timestamp")
        self.axs1[0,1].set_ylabel("Amplituda")
        self.axs1[0,1].xaxis.set_major_locator(MaxNLocator(5))
        # date_format = mdates.DateFormatter('%m-%d %H:%M:%S')  # Format dnia i godziny
        # self.axs[0, 0].xaxis.set_major_formatter(date_format)

        # Formatowanie etykiet osi X (obrót o 45 stopni, aby były czytelne)
        for ax in self.axs.flatten():
            ax.tick_params(axis='x', rotation=45)  # Obrót etykiet osi X o 45°

        # Rysowanie wykresów na canvasie
        self.canvas.draw()
        
    def plot_sensor_data(self, timestamps, temperatures, pressures, humidities, light_intensities):
        # Indeksy pomiarów
        indices = list(range(1, len(temperatures) + 1))

        # Czyszczenie istniejących wykresów
        for ax in self.axs.flatten():
            ax.clear()

        # Rysowanie wykresów
        if temperatures:
            self.axs[0, 0].plot(timestamps, temperatures, marker='o', label="Temperatura (°C)", color='red')
            self.axs[0, 0].set_title("Temperatura")
            self.axs[0, 0].grid(True)
            self.axs[0, 0].set_xlabel("Pomiar")
            self.axs[0, 0].set_ylabel("Temperatura (°C)")
            self.axs[0, 0].xaxis.set_major_locator(MaxNLocator(5))  # Ustawienie max 5 etykiet na osi X
        if pressures:
            self.axs[0, 1].plot(timestamps, pressures, marker='o', label="Ciśnienie (hPa)", color='blue')
            self.axs[0, 1].set_title("Ciśnienie")
            self.axs[0, 1].grid(True)
            self.axs[0, 1].set_xlabel("Pomiar")
            self.axs[0, 1].set_ylabel("Ciśnienie (hPa)")
            self.axs[0, 0].xaxis.set_major_locator(MaxNLocator(5))  # Ustawienie max 5 etykiet na osi X
        if humidities:
            self.axs[1, 0].plot(timestamps, humidities, marker='o', label="Wilgotność (%)", color='green')
            self.axs[1, 0].set_title("Wilgotność")
            self.axs[1, 0].grid(True)
            self.axs[1, 0].set_xlabel("Pomiar")
            self.axs[1, 0].set_ylabel("Wilgotność (%)")
            self.axs[0, 0].xaxis.set_major_locator(MaxNLocator(5))  # Ustawienie max 5 etykiet na osi X
        if light_intensities:
            self.axs[1, 1].plot(timestamps, light_intensities, marker='o', label="Natężenie światła (lux)", color='orange')
            self.axs[1, 1].set_title("Natężenie światła")
            self.axs[1, 1].grid(True)
            self.axs[1, 1].set_xlabel("Pomiar")
            self.axs[1, 1].set_ylabel("Natężenie światła (lux)")
            self.axs[0, 0].xaxis.set_major_locator(MaxNLocator(5))  # Ustawienie max 5 etykiet na osi X
        
        date_format = mdates.DateFormatter('%m-%d %H:%M:%S')  # Format dnia i godziny
        self.axs[0, 0].xaxis.set_major_formatter(date_format)
        self.axs[0, 1].xaxis.set_major_formatter(date_format)
        self.axs[1, 0].xaxis.set_major_formatter(date_format)
        self.axs[1, 1].xaxis.set_major_formatter(date_format)

        # Formatowanie etykiet osi X (obrót o 45 stopni, aby były czytelne)
        for ax in self.axs.flatten():
            ax.tick_params(axis='x', rotation=45)  # Obrót etykiet osi X o 45°

        # Rysowanie wykresów na canvasie
        self.canvas.draw()

    def update_plots_by_date(self):
        database_choice = 'test'

        # Pobierz daty z widżetów DateEntry
        start_date = self.start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date.get_date().strftime("%Y-%m-%d")

        try:
            temperatures, pressures, humidities, light_intensities, timestamps = self.sql_data_handling.fetch_sensor_data_by_date(
                database_choice, start_date, end_date
            )
            self.plot_sensor_data(timestamps, temperatures, pressures, humidities, light_intensities)
        except Exception as e:
            print(f"Błąd podczas aktualizacji wykresów: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.camera_display.stop() if app.camera_display else None, root.destroy()))
    root.mainloop()
