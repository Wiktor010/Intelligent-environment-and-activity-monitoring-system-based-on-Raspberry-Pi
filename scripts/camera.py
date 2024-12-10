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
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)  # ZwiÄ™kszona czuĹ‚oĹ›Ä‡

        # Inicjalizacja trackera
        self.tracker = cv2.TrackerKCF_create()
        self.tracking_started = False

        # Zmienna do Ĺ›ledzenia czasu, kiedy obiekt zostaĹ‚ utracony
        self.loss_time = 0
        self.loss_threshold = 5  # Liczba klatek, po ktĂłrej tracker jest ponownie inicjowany

        # Flaga rejestracji
        self.is_recording = False
        self.video_writer = None  # Obiekt do zapisu wideo

        # Parametry zapisu wideo
        self.video_codec = cv2.VideoWriter_fourcc(*'mp4v')  # Codec dla formatu MP4
        self.video_fps = framerate
        self.video_resolution = resolution

    def generate_filename(self):
        # Generowanie unikalnej nazwy pliku na podstawie aktualnej daty i czasu
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.mp4"
    
    def start_recording(self):
            # Inicjalizacja zapisu wideo z unikalnÄ… nazwÄ… pliku
        self.video_file = self.generate_filename()
        self.video_writer = cv2.VideoWriter(self.video_file, self.video_codec, self.video_fps, self.video_resolution)

    def stop_recording(self):
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

            # Konwertujemy obraz na RGB, aby byĹ‚ kompatybilny z trackerem
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            gray_image = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2GRAY)

            # Tworzenie maski tĹ‚a
            if not self.tracking_started:
                fg_mask = self.bg_subtractor.apply(gray_image)
                kernel = np.ones((3, 3), np.uint8)  # Mniejszy kernel dla wiÄ™kszej szczegĂłĹ‚owoĹ›ci
                fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)

                contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for contour in contours:
                    if cv2.contourArea(contour) > 500:  # Mniejsza wartoĹ›Ä‡ dla wiÄ™kszej czuĹ‚oĹ›ci
                        (x, y, w, h) = cv2.boundingRect(contour)

                        # Filtrowanie konturĂłw na podstawie proporcji
                        aspect_ratio = h / float(w)
                        if 1.2 < aspect_ratio < 5.0:  # Szerszy zakres proporcji dla wiÄ™kszej elastycznoĹ›ci
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

                    # JeĹ›li obiekt jest Ĺ›ledzony, uruchamiamy rejestracjÄ™, jeĹ›li nie jest jeszcze uruchomiona
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

                        # Zatrzymanie rejestracji, jeĹ›li byĹ‚a aktywna
                        if self.is_recording:
                            self.stop_recording()
                            self.is_recording = False

            else:
                # JeĹ›li tracker nie dziaĹ‚a, zatrzymujemy rejestracjÄ™, jeĹ›li byĹ‚a aktywna
                if self.is_recording:
                    self.stop_recording()
                    self.is_recording = False

            # Zapis klatek wideo, jeĹ›li nagrywanie jest aktywne
            if self.is_recording and self.video_writer:
                self.video_writer.write(cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR))

            # # WyĹ›wietlanie obrazu w GUI
            # self.update_frame(image_rgb)

            # # Przerwanie pÄ™tli GUI, jeĹ›li naciĹ›niesz 'q'
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            # # PrzeĹ‚Ä…czanie GUI
            # self.root.update()
        self.camera.close()
        print("Camera stopped.")

    def stop(self):
        self.camera.close()
        print("Camera stopped.")