# main.py

import time
from scripts.sensors_handling import Sensors
from scripts.globals import Globals
from scripts.sql import SensorDataHandler

if __name__ == "__main__":
    # read_sensors_data()
    # print_sensors_data()
    # # # Wait a few seconds before reading again
    # update_sensor_data(g.sensor_temperature, g.sensor_pressure, g.sensor_humidity, g.sensor_light_intensity)
    # insert_sensor_data('test')
    # time.sleep(5)
    sql1 = SensorDataHandler()
    temperatures, pressures, humidities, light_intensities, timestamps = sql1.fetch_all_sensor_data('test')
    print(timestamps)
    # last_temperature, last_pressure, last_humidity, last_light_intensit = fetch_latest_sensor_data('test')
    # temperatures, pressures, humidities, light_intensities = fetch_all_sensor_data('test')
    # time.sleep(15)

