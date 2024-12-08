import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from PIL import Image, ImageTk
import time
import cv2
from picamera2 import Picamera2
import numpy as np
import datetime

# Zakładamy, że masz wcześniej zaimportowane funkcje do obsługi bazy danych
try:
    from scripts.sql import fetch_latest_sensor_data, fetch_all_sensor_data
except ModuleNotFoundError:
    from sql import fetch_latest_sensor_data, fetch_all_sensor_data

try:
    import scripts.globals as g
except ModuleNotFoundError:
    import globals as g


class PiCameraDisplay:
    def __init__(self, root, camera_label, recording_label, resolution=(640, 480), framerate=40):
        self.root = root  # Przechowujemy root w obiekcie klasy
        self.camera = Picamera2()

        # Konfiguracja kamery
        video_config = self.camera.create_video_configuration(main={"size": resolution})
        self.camera.configure(video_config)
        self.camera.set_controls({"FrameRate": framerate})
        self.camera.start()
        time.sleep(0.1)

        # Tworzenie obiektu do background subtraction
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)

        # Inicjalizacja trackera
        self.tracker = cv2.TrackerKCF_create()
        self.tracking_started = False

        # Zmienna do śledzenia czasu, kiedy obiekt został utracony
        self.loss_time = 0
        self.loss_threshold = 5

        # Flaga rejestracji
        self.is_recording = False
        self.video_writer = None

        # Parametry zapisu wideo
        self.video_codec = cv2.VideoWriter_fourcc(*'mp4v')  # Codec dla formatu MP4
        self.video_fps = framerate
        self.video_resolution = resolution

        # Etykieta do wyświetlania statusu nagrywania
        self.recording_label = recording_label  # Przechowujemy etykietę przekazaną z zewnątrz

        # Ustawienie przekazanej etykiety do wyświetlania obrazu
        self.label = camera_label


    def stop_recording(self):
        # Funkcja zatrzymujÄ…ca rejestracjÄ™ (np. zapis do pliku)
        print(f"Recording stopped. File saved as: {self.video_file}")
        self.recording_label.config(text="Recording stopped", fg="red")

        # Zatrzymanie zapisu wideo
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            
    def generate_filename(self):
        # Generowanie unikalnej nazwy pliku na podstawie aktualnej daty i czasu
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.mp4"    

    def get_frame(self):
        """Zwraca pojedynczą klatkę z kamery."""
        frame = self.camera.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Przekształcenie do RGB dla Tkinter

    def stop(self):
        """Zatrzymuje kamerę."""
        self.camera.close()

    def start_recording(self):
        # Funkcja uruchamiajÄ…ca rejestracjÄ™ (np. zapis do pliku)
        print("Recording started.")
        self.recording_label.config(text="Recording started", fg="green")

        # Inicjalizacja zapisu wideo z unikalnÄ… nazwÄ… pliku
        self.video_file = self.generate_filename()
        self.video_writer = cv2.VideoWriter(
            self.video_file, self.video_codec, self.video_fps, self.video_resolution
        )

    def update_frame(self, frame):
        """Aktualizacja obrazu w GUI."""
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Zmiana RGB na BGR dla PIL
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

    def display_feed(self):
        """Przechwytywanie i przetwarzanie obrazu z kamery."""
        while True:
            # Przechwytywanie obrazu z kamery
            image = self.camera.capture_array()

            # Konwertujemy obraz na RGB, aby był kompatybilny z trackerem
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

            # Tworzenie maski tła
            if not self.tracking_started:
                fg_mask = self.bg_subtractor.apply(gray_image)
                kernel = np.ones((3, 3), np.uint8)  # Mniejszy kernel dla większej szczegółowości
                fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

                contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > 500:  # Mniejsza wartość dla większej czułości
                        (x, y, w, h) = cv2.boundingRect(contour)

                        # Filtrowanie konturów na podstawie proporcji
                        aspect_ratio = h / float(w)
                        if 1.2 < aspect_ratio < 5.0:  # Szerszy zakres proporcji dla większej elastyczności
                            roi = (x, y, w, h)
                            self.tracker.init(image_rgb, roi)
                            self.tracking_started = True
                            print("Tracking started.")
                            break

            if self.tracking_started:
                # Aktualizacja trackera
                success, bbox = self.tracker.update(image_rgb)
                if success:
                    self.loss_time = 0  # Zresetowanie licznika utraty
                    (x, y, w, h) = [int(v) for v in bbox]
                    cv2.rectangle(image_rgb, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(image_rgb, "Person being tracked", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                    # Jeżeli obiekt jest śledzony, uruchamiamy rejestrację, jeżeli nie jest jeszcze uruchomiona
                    if not self.is_recording:
                        self.start_recording()
                        self.is_recording = True
                else:
                    self.loss_time += 1
                    if self.loss_time > self.loss_threshold:
                        print("Person lost. Reinitializing tracker.")
                        self.tracking_started = False
                        self.loss_time = 0
                        # Ponowna inicjalizacja trackera
                        self.tracker = cv2.TrackerKCF_create()

                        # Zatrzymanie rejestracji, jeżeli była aktywna
                        if self.is_recording:
                            self.stop_recording()
                            self.is_recording = False

            else:
                # Jeżeli tracker nie działa, zatrzymujemy rejestrację, jeżeli była aktywna
                if self.is_recording:
                    self.stop_recording()
                    self.is_recording = False

            # Zapis klatek wideo, jeżeli nagrywanie jest aktywne
            if self.is_recording and self.video_writer:
                self.video_writer.write(cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))

            # Wyświetlanie obrazu w GUI
            self.update_frame(image_rgb)

            # Przerwanie pętli GUI, jeżeli naciśniesz 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Przełączanie GUI
            self.root.update()

        self.camera.close()
        print("Camera stopped.")
        self.root.quit()


class SensorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sensor App")
        self.root.geometry("1920x1080")

        # Tworzenie notebooka (zakładki) przed utworzeniem etykiety
        self.notebook = ttk.Notebook(root)
        self.tab1 = ttk.Frame(self.notebook)
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="Dane i Kamera")
        self.notebook.add(self.tab2, text="Wykresy")
        self.notebook.pack(expand=True, fill="both")
        
        # Dodanie kamery do aplikacji po utworzeniu zakładek
        self.camera_label = tk.Label(self.tab1)  # Przeniesienie etykiety do zakładki 1
        self.camera_label.pack()

        # Tworzenie etykiety statusu nagrywania w zakładce "Dane i Kamera"
        self.recording_label = tk.Label(self.tab1, text="", font=("Helvetica", 14), fg="red")
        self.recording_label.pack(pady=10)  # Upewnij się, że etykieta jest widoczna

        # Inicjalizacja kamery i jej wyświetlanie
        self.camera_display = PiCameraDisplay(self.root, self.camera_label, self.recording_label)

        # Ustawienie zakładek po inicjalizacji komponentów
        self.setup_tab1()  # Zainicjalizuj tab1 po ustawieniu kamery
        self.setup_tab2()  # Ustawienia wykresów

        # Uruchomienie cyklicznej aktualizacji danych
        self.update_data()

        # Rozpoczynamy wyświetlanie obrazu z kamery
        self.camera_display.display_feed()  # Uruchamia funkcję odpowiedzialną za feed kamery

    def setup_tab1(self):
        self.data_frame = tk.Frame(self.tab1)
        self.data_frame.pack(side="left", padx=15, pady=15)

    
        # self.camera_label = tk.Label(self.tab1)
        # self.camera_label.pack()

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

    def setup_tab2(self):
        # Ustawienia figury i os
        self.figure, self.axs = plt.subplots(2, 2, figsize=(14, 10), gridspec_kw={'hspace': 0.5, 'wspace': 0.3})
        self.figure.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab2)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

        # Przycisk do aktualizacji wykresów
        self.refresh_button = tk.Button(self.tab2, text="Aktualizuj Wykresy", command=self.update_plots)
        self.refresh_button.pack(pady=10)

    def update_plots(self):
        """Aktualizuje wykresy na podstawie danych z bazy danych."""
        timestamps, temperatures, pressures, humidities, light_intensities = fetch_all_sensor_data()

        # Temperatura
        if temperatures:
            self.axs[0, 0].plot(timestamps, temperatures, marker='o', label="Temperatura (°C)", color='red')
            self.axs[0, 0].set_title("Temperatura")
            self.axs[0, 0].grid(True)
            self.axs[0, 0].set_xlabel("Pomiar")
            self.axs[0, 0].set_ylabel("Temperatura (°C)")
            self.axs[0, 0].xaxis.set_major_locator(mdates.WeekdayLocator())  # Oznaczenia na osi X jako dni tygodnia
            self.axs[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

        # Ciśnienie
        if pressures:
            self.axs[0, 1].plot(timestamps, pressures, marker='o', label="Ciśnienie (hPa)", color='blue')
            self.axs[0, 1].set_title("Ciśnienie")
            self.axs[0, 1].grid(True)
            self.axs[0, 1].set_xlabel("Pomiar")
            self.axs[0, 1].set_ylabel("Ciśnienie (hPa)")
            self.axs[0, 1].xaxis.set_major_locator(mdates.WeekdayLocator())  # Oznaczenia na osi X jako dni tygodnia
            self.axs[0, 1].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

        # Wilgotność
        if humidities:
            self.axs[1, 0].plot(timestamps, humidities, marker='o', label="Wilgotność (%)", color='green')
            self.axs[1, 0].set_title("Wilgotność")
            self.axs[1, 0].grid(True)
            self.axs[1, 0].set_xlabel("Pomiar")
            self.axs[1, 0].set_ylabel("Wilgotność (%)")
            self.axs[1, 0].xaxis.set_major_locator(mdates.WeekdayLocator())  # Oznaczenia na osi X jako dni tygodnia
            self.axs[1, 0].xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))

        # Natężenie światła
        if light_intensities:
            self.axs[1, 1].plot(timestamps, light_intensities, marker='o', label="Natężenie światła (lx)", color='purple')
            self.axs[1, 1].set_title("Natężenie światła")
            self.axs[1, 1].grid(True)
            self.axs[1, 1].set_xlabel("Pomiar")
            self.axs[1, 1].set_ylabel("Natężenie światła (lx)")
            self.axs[0, 0].xaxis.set_major_locator(MaxNLocator(5))  # Ustawienie max 5 etykiet na osi X

        # Odtwarzanie wykresu
        self.canvas.draw()

    def stop(self):
        """Zatrzymanie aplikacji i kamery."""
        self.camera_display.stop()
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = SensorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop(), root.destroy()))
    root.mainloop()

