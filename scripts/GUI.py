import tkinter as tk            #Add librabry for GUI
from tkinter import ttk
try:
    from scripts.sql import fetch_latest_sensor_data
except ModuleNotFoundError:
    from sql import fetch_latest_sensor_data

try:
    import scripts.globals as g
except ModuleNotFoundError:
    import globals as g


def refresh_data():
    """
    Aktualizuje dane w GUI na podstawie najnowszych wartości z bazy danych.
    """
    database_choice = 'test'  # Wybór bazy danych
    fetch_latest_sensor_data(database_choice)  # Pobranie najnowszych danych

    # Aktualizacja etykiet w GUI
    temperature_label.config(text=f"Temperatura: {g.db_temperature:.2f} °C" if g.db_temperature is not None else "Temperatura: Brak danych")
    pressure_label.config(text=f"Ciśnienie: {g.db_pressure:.2f} hPa" if g.db_pressure is not None else "Ciśnienie: Brak danych")
    humidity_label.config(text=f"Wilgotność: {g.db_humidity:.2f} %" if g.db_humidity is not None else "Wilgotność: Brak danych")
    light_intensity_label.config(text=f"Natężenie światła: {g.db_light_intensity:.2f} lux" if g.db_light_intensity is not None else "Natężenie światła: Brak danych")

def run_gui():
    """
    Uruchamia GUI.
    """
    global temperature_label, pressure_label, humidity_label, light_intensity_label

    # Tworzenie GUI
    root = tk.Tk()
    root.title("Dane z czujników")

    # Główna ramka
    frame = ttk.Frame(root, padding="20")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Etykiety do wyświetlania danych
    temperature_label = ttk.Label(frame, text="Temperatura: Brak danych", font=("Arial", 14))
    temperature_label.grid(row=0, column=0, pady=10)

    pressure_label = ttk.Label(frame, text="Ciśnienie: Brak danych", font=("Arial", 14))
    pressure_label.grid(row=1, column=0, pady=10)

    humidity_label = ttk.Label(frame, text="Wilgotność: Brak danych", font=("Arial", 14))
    humidity_label.grid(row=2, column=0, pady=10)

    light_intensity_label = ttk.Label(frame, text="Natężenie światła: Brak danych", font=("Arial", 14))
    light_intensity_label.grid(row=3, column=0, pady=10)

    # Przycisk do odświeżania danych
    refresh_button = ttk.Button(frame, text="Odśwież dane", command=refresh_data)
    refresh_button.grid(row=4, column=0, pady=20)

    # Uruchomienie GUI
    root.mainloop()

if __name__ == "__main__":
    run_gui()