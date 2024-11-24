from sql import fetch_latest_sensor_data
import tkinter as tk
from tkinter import ttk

def refresh_data():
    """
    Aktualizuje dane w GUI na podstawie najnowszych wartości z bazy danych.
    """
    database_choice = 'test'  # Wybór bazy danych
    temp, press, hum, light = fetch_latest_sensor_data(database_choice)  # Pobranie najnowszych danych

    # Aktualizacja etykiet w GUI
    temperature_label.config(text=f"Temperatura: {temp:.2f} °C" if last_temperature is not None else "Temperatura: Brak danych")
    pressure_label.config(text=f"Ciśnienie: {press:.2f} hPa" if last_pressure is not None else "Ciśnienie: Brak danych")
    humidity_label.config(text=f"Wilgotność: {hum:.2f} %" if last_humidity is not None else "Wilgotność: Brak danych")
    light_intensity_label.config(text=f"Natężenie światła: {light:.2f} lux" if last_light_intensity is not None else "Natężenie światła: Brak danych")

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