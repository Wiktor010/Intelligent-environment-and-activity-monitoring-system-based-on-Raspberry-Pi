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
            cv2.imshow("Raspberry Pi Camera", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()

    def stop(self):
        self.camera.close()

# Tworzenie obiektu klasy PiCameraDisplay i uruchomienie wyświetlania
camera_display = PiCameraDisplay()
camera_display.display_feed()
camera_display.stop()

