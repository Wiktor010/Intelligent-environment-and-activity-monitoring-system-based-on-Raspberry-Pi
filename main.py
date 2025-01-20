import threading
import time
import tkinter as tk
from scripts.sensors_handling import Sensors
from scripts.globals import Globals
from scripts.sql import SensorDataHandler
from scripts.MicrophoneRecorder import MicrophoneRecorder
from scripts.GUI import SensorApp

def run_gui():
    root = tk.Tk()
    app = SensorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.camera_display.stop() if app.camera_display else None, root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    # Inicjalizacja komponentów
    sensors = Sensors()
    database_handler = SensorDataHandler()
    variables = Globals()

    # Tworzenie i uruchomienie wątku dla GUI
    gui_thread = threading.Thread(target=run_gui, daemon=True)
    gui_thread.start()

    # Pętla główna działająca w wątku głównym
    while True:
        sensors.read_sensors_data()
        database_handler.update_sensor_data('test')
        database_handler.insert_sensor_data('test')
        time.sleep(1000)  # Opcjonalny timeout, aby ograniczyć obciążenie CPU

