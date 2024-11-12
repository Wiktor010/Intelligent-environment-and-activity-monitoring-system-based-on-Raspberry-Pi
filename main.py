# main.py

import time
from scripts.sensors_handling import read_sensors_data

if __name__ == "__main__":
    while True:
        read_sensors_data()
        # Wait a few seconds before reading again
        time.sleep(2)