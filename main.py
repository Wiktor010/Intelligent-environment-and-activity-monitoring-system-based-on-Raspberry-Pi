import threading
import time
import tkinter as tk
from queue import Queue
from scripts.sensors_handling import Sensors
from scripts.globals import Globals
from scripts.sql import SensorDataHandler
from scripts.MicrophoneRecorder import MicrophoneRecorder
from scripts.GUI import SensorApp

# Kolejka do komunikacji między wątkami
gui_queue = Queue()

def run_gui():
    global app
    root = tk.Tk()
    app = SensorApp(root)
    gui_queue.put(gui_app)  # Przekazanie instancji do kolejki
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

    # Czekaj na inicjalizację GUI
    while gui_queue.empty():
        time.sleep(0.1)
    gui_app = gui_queue.get()  # Pobierz instancję GUI z kolejki

    # Pętla główna działająca w wątku głównym
    try:
        while True:
            sensors.read_sensors_data()
            database_handler.update_sensor_data()
            database_handler.insert_sensor_data('test')
            time.sleep(2)  # Opcjonalny timeout, aby ograniczyć obciążenie CPU

            # Wywołaj funkcję aktualizacji wykresów w GUI w wątku głównym
            gui_app.root.after(0, gui_app.xxx)  # Metoda `after` wywołuje funkcję w wątku GUI
    except KeyboardInterrupt as e:
        print(f"Zamykanie aplikacji z powodu: {e}")
