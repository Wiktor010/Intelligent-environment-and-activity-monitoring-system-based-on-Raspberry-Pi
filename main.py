# main.py

import time
from scripts.sensors_handling import read_sensors_data, print_sensors_data
import scripts.globals as g
from scripts.sql import insert_sensor_data, update_sensor_data, fetch_latest_sensor_data, fetch_all_sensor_data, plot_sensor_data
from scripts.GUI import run_gui

if __name__ == "__main__":
    # run_gui()
    while True:
        read_sensors_data()
        print_sensors_data()
        # # Wait a few seconds before reading again
        update_sensor_data(g.sensor_temperature, g.sensor_pressure, g.sensor_humidity, g.sensor_light_intensity)
        insert_sensor_data('test')
        time.sleep(5)
    
        # last_temperature, last_pressure, last_humidity, last_light_intensit = fetch_latest_sensor_data('test')
        # temperatures, pressures, humidities, light_intensities = fetch_all_sensor_data('test')
        # plot_sensor_data(temperatures, pressures, humidities, light_intensities)
        # time.sleep(15)

