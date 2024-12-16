import tkinter as tk            # Add library for GUI
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')  # Backend kompatybilny z Tkinter
from PIL import Image, ImageTk, ImageDraw
from detekcja_krawedzi import PiCameraDisplay
from stream_5 import PiCameraDisplay
try:
    from scripts.sql import fetch_latest_sensor_data, fetch_all_sensor_data
except ModuleNotFoundError:
    from sql import fetch_latest_sensor_data, fetch_all_sensor_data

try:
    import scripts.globals as g
except ModuleNotFoundError:
    import globals as g


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor App")
        # self.root.geometry("1920x1080")  # Ustawia rozmiar okna (szerokość x wysokość)
        self.root.attributes('-fullscreen', True)

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

        # Zakładka 3: analiza audio
        # self.setup_tab3()
        # Utwórz instancję klasy kamery
        try:
            self.camera_display = PiCameraDisplay()
        except Exception as e:
            print(f"Nie można zainicjować kamery: {e}")
            self.camera_display = None  # Ustaw na None, jeśli kamera nie jest dostępna

        # try:
        #     self.microphone = microphone()
        # except Exception as e:
        #     print(f"Nie znaleziono mikrofonu")
        #     self.microphone = None

        # Uruchom aktualizację danych co 15 sekund
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

        # Closing GUI button
        tk.Button(self.data_frame, text = "Zamknij", font = ("Arial", 12), command = self.root.destroy).pack(side = "bottom", padx = (20, 20), pady = 20)

    def setup_tab2(self):
        # Ustawienia figury i os
        self.figure, self.axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.5, 'wspace': 0.3})
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab2)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

        # Przycisk do aktualizacji wykresów
        self.refresh_button = tk.Button(self.tab2, text="Aktualizuj Wykresy", command=self.update_plots)
        self.refresh_button.pack(pady=10)

    def update_data(self):
        """Aktualizacja danych czujników."""
        database_choice = 'test'  # Wybór bazy danych
        fetch_latest_sensor_data(database_choice)  # Pobranie najnowszych danych

        if g.db_temperature is not None:
            self.labels["temperatura"].config(text=f"{g.db_temperature:.2f} °C")
        else:
            self.labels["temperatura"].config(text="Brak danych")

        if g.db_pressure is not None:
            self.labels["cisnienie"].config(text=f"{g.db_pressure:.2f} hPa")
        else:
            self.labels["cisnienie"].config(text="Brak danych")

        if g.db_humidity is not None:
            self.labels["wilgotnosc"].config(text=f"{g.db_humidity:.2f} %")
        else:
            self.labels["wilgotnosc"].config(text="Brak danych")

        if g.db_light_intensity is not None:
            self.labels["natezenie_swiatla"].config(text=f"{g.db_light_intensity:.2f} lx")
        else:
            self.labels["natezenie_swiatla"].config(text="Brak danych")

        # Zaplanuj aktualizację co 15 sekund
        self.root.after(15000, self.update_data)

    def start_camera(self):
        """Uruchamia podgląd z kamery."""
        self.update_camera()

    def update_camera(self):
        # Sprawdź, czy kamera została poprawnie zainicjalizowana
        if self.camera_display is not None:
            try:
                frame = self.camera_display.get_processed_frame()
                if frame is not None:
                    img = ImageTk.PhotoImage(Image.fromarray(frame))
                    self.camera_label.imgtk = img
                    self.camera_label.configure(image=img)
            except Exception as e:
                print(f"Błąd kamery: {e}")
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
        """Aktualizuje wykresy na podstawie danych z bazy danych."""
        database_choice = 'test'
        try:
            temperatures, pressures, humidities, light_intensities, timestamps = fetch_all_sensor_data(database_choice)
            self.plot_sensor_data(timestamps, temperatures, pressures, humidities, light_intensities)
        except Exception as e:
            print(f"Błąd podczas aktualizacji wykresów: {e}")

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
        
        date_format = mdates.DateFormatter('%d %H:%M:%S')  # Format dnia i godziny
        self.axs[0, 0].xaxis.set_major_formatter(date_format)
        self.axs[0, 1].xaxis.set_major_formatter(date_format)
        self.axs[1, 0].xaxis.set_major_formatter(date_format)
        self.axs[1, 1].xaxis.set_major_formatter(date_format)

        # Formatowanie etykiet osi X (obrót o 45 stopni, aby były czytelne)
        for ax in self.axs.flatten():
            ax.tick_params(axis='x', rotation=45)  # Obrót etykiet osi X o 45°

        # Rysowanie wykresów na canvasie
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.camera_display.stop(), root.destroy()))
    root.mainloop()
