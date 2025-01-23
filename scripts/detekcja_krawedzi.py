import cv2

# Tworzenie obiektu do odejmowania tła
bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=30)

# Wczytaj wideo
cap = cv2.VideoCapture('/home/pi/Intelligent-environment-and-activity-monitoring-system-based-on-Raspberry-Pi/recording_2025-01-19_15-01-43.mp4')
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Zastosowanie odejmowania tłaS
    fg_mask = bg_subtractor.apply(frame)

    # Wyświetlanie wyniku
    cv2.imshow('Frame', frame)
    cv2.imshow('Foreground Mask', fg_mask)

    if cv2.waitKey(150) & 0xFF == 27:  # Naciśnij ESC, aby wyjść
        break

cap.release()
cv2.destroyAllWindows()

# import tkinter as tk
# from tkinter import Label
# from PIL import Image, ImageTk
# from picamera2 import Picamera2
# import numpy as np

# class CameraApp:
#     def __init__(self, window, window_title):
#         self.window = window
#         self.window.title(window_title)

#         # Inicjalizacja kamery
#         self.camera = Picamera2()
#         config = self.camera.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
#         self.camera.configure(config)
#         self.camera.start()

#         # Tworzenie etykiety do wyświetlania obrazu
#         self.vid = Label(window)
#         self.vid.pack()

#         # Uruchamianie aktualizacji obrazu
#         self.update()

#         self.window.mainloop()

#     def update(self):
#         # Pobieranie obrazu z kamery
#         frame = self.camera.capture_array()

#         # Konwersja obrazu do formatu RGB
#         img = Image.fromarray(frame)
#         imgtk = ImageTk.PhotoImage(image=img)
#         self.vid.imgtk = imgtk
#         self.vid.configure(image=imgtk)

#         # Aktualizacja obrazu co 10 ms
#         self.window.after(10, self.update)

#     def __del__(self):
#         if self.camera.running:
#             self.camera.stop()

# # Uruchamianie aplikacji
# root = tk.Tk()
# app = CameraApp(root, "Camera Feed")

