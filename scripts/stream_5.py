import cv2
import numpy as np
from picamera2 import Picamera2
import time
import tkinter as tk
from PIL import Image, ImageTk
import datetime


class PiCameraDisplay:
    def __init__(self, resolution=(640, 480), framerate=40):
        self.camera = Picamera2()

        # Konfiguracja kamery
        video_config = self.camera.create_video_configuration(main={"size": resolution})
        self.camera.configure(video_config)
        self.camera.set_controls({"FrameRate": framerate})
        self.camera.start()
        time.sleep(0.1)

        # Tworzenie obiektu do background subtraction
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)  # Zwiększona czułość

        # Inicjalizacja trackera
        self.tracker = cv2.TrackerKCF_create()
        self.tracking_started = False

        # Zmienna do śledzenia czasu, kiedy obiekt został utracony
        self.loss_time = 0
        self.loss_threshold = 5  # Liczba klatek, po której tracker jest ponownie inicjowany

        # Flaga rejestracji
        self.is_recording = False
        self.video_writer = None  # Obiekt do zapisu wideo

        # Parametry zapisu wideo
        self.video_codec = cv2.VideoWriter_fourcc(*'mp4v')  # Codec dla formatu MP4
        self.video_fps = framerate
        self.video_resolution = resolution

        # Tworzenie GUI
        self.root = tk.Tk()
        self.root.title("Pi Camera Feed")
        self.label = tk.Label(self.root)
        self.label.pack()

        # Etykieta do wyświetlania statusu nagrywania
        self.recording_label = tk.Label(self.root, text="", font=("Helvetica", 14), fg="red")
        self.recording_label.pack()

    def generate_filename(self):
        # Generowanie unikalnej nazwy pliku na podstawie aktualnej daty i czasu
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.mp4"

    def start_recording(self):
        # Funkcja uruchamiająca rejestrację (np. zapis do pliku)
        print("Recording started.")
        self.recording_label.config(text="Recording started", fg="green")

        # Inicjalizacja zapisu wideo z unikalną nazwą pliku
        self.video_file = self.generate_filename()
        self.video_writer = cv2.VideoWriter(
            self.video_file, self.video_codec, self.video_fps, self.video_resolution
        )

    def stop_recording(self):
        # Funkcja zatrzymująca rejestrację (np. zapis do pliku)
        print(f"Recording stopped. File saved as: {self.video_file}")
        self.recording_label.config(text="Recording stopped", fg="red")

        # Zatrzymanie zapisu wideo
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

    def update_frame(self, frame):
        # Aktualizacja obrazu w GUI
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Zmiana RGB na BGR dla PIL
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.label.imgtk = imgtk
        self.label.configure(image=imgtk)

    def display_feed(self):
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

                    # Jeśli obiekt jest śledzony, uruchamiamy rejestrację, jeśli nie jest jeszcze uruchomiona
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

                        # Zatrzymanie rejestracji, jeśli była aktywna
                        if self.is_recording:
                            self.stop_recording()
                            self.is_recording = False

            else:
                # Jeśli tracker nie działa, zatrzymujemy rejestrację, jeśli była aktywna
                if self.is_recording:
                    self.stop_recording()
                    self.is_recording = False

            # Zapis klatek wideo, jeśli nagrywanie jest aktywne
            if self.is_recording and self.video_writer:
                self.video_writer.write(cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))

            # Wyświetlanie obrazu w GUI
            self.update_frame(image_rgb)

            # Przerwanie pętli GUI, jeśli naciśniesz 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Przełączanie GUI
            self.root.update()

        self.camera.close()
        print("Camera stopped.")
        self.root.quit()

    def stop(self):
        self.camera.close()
        print("Camera stopped.")


# Tworzenie obiektu klasy PiCameraDisplay i uruchomienie wyświetlania
camera_display = PiCameraDisplay()
camera_display.display_feed()
camera_display.stop()
