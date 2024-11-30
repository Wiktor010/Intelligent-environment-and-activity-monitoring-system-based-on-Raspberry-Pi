import cv2
from picamera2 import Picamera2
import time

class PiCameraDisplay:
    def __init__(self, resolution=(640, 480), framerate=40):
        self.camera = Picamera2()
        
        video_config = self.camera.create_video_configuration(main={"size": resolution})
        self.camera.configure(video_config)
        self.camera.set_controls({"FrameRate": framerate})
        self.camera.start()
        time.sleep(0.1)

    def display_feed(self):
        while True:
            image = self.camera.capture_array()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Konwersja do odcieni szarości (przydatne do detekcji krawędzi)
            gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Detekcja krawędzi przy użyciu algorytmu Canny'ego
            edges = cv2.Canny(gray_image, 100, 200)
            
            # Wyświetlenie wyników detekcji krawędzi
            cv2.imshow("Raspberry Pi Camera - Edge Detection", edges)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def stop(self):
        self.camera.close()
        
if __name__ == "__main__":
    # Tworzenie obiektu klasy PiCameraDisplay i uruchomienie wyświetlania
    camera_display = PiCameraDisplay()
    camera_display.display_feed()
    camera_display.stop()