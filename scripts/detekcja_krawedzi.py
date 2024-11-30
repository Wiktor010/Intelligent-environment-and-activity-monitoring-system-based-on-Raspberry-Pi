import cv2
from picamera2 import Picamera2
from PIL import Image, ImageTk
import time

class PiCameraDisplay:
    def __init__(self, resolution=(640, 480), framerate=40):
        self.camera = Picamera2()
        video_config = self.camera.create_video_configuration(main={"size": resolution})
        self.camera.configure(video_config)
        self.camera.set_controls({"FrameRate": framerate})
        self.camera.start()
        time.sleep(0.1)  # Czas na rozruch kamery

    def get_processed_frame(self):
        """Pobiera klatkę, przetwarza ją (detekcja krawędzi) i zwraca."""
        image = self.camera.capture_array()
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_image, 100, 200)  # Detekcja krawędzi
        return edges

    def stop(self):
        """Zatrzymuje kamerę."""
        self.camera.close()
        
if __name__ == "__main__":
    # Tworzenie obiektu klasy PiCameraDisplay i uruchomienie wyświetlania
    camera_display = PiCameraDisplay()
    camera_display.display_feed()
    camera_display.stop()