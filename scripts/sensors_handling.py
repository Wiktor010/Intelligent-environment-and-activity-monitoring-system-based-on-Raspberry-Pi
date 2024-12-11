import time
from bme280 import BME280  # Pimoroni BME280 library
from subprocess import PIPE, Popen
import board               # Adafruit library for board configuration
import busio               # Adafruit library for I2C
import adafruit_bh1750     # Adafruit BH1750 light sensor library
from smbus2 import SMBus   # SMBus for compatibility with BME280
try:
    from scripts import globals as g  # When script is used as module (eg. in main.py file)
except ModuleNotFoundError:
    import globals as g  # When scirpt is running alone


class Sensors:
    def __init__(self):
        # Initialization of I2C for used sensors
        self.i2c_bus = SMBus(1)
        self.i2c_bh = busio.I2C(board.SCL, board.SDA)

        # self.bme280 = BME280(i2c_dev = self.i2c_bus)
        self.bh1750 = adafruit_bh1750.BH1750(self.i2c_bh)

        # # Variables to store sensor data
        # self.sensor_temperature = None
        # self.sensor_humidity = None
        # self.sensor_pressure = None
        # self.sensor_light_intensity = None

    def get_cpu_temperature(self):
        process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE)
        output, _error = process.communicate()
        output = output.decode()
        return float(output[output.index("=") + 1 : output.rindex("'")])

    def read_sensors_data(self):
        # Read values from BME280
        # g.sensor_temperature = self.bme280.get_temperature()
        # g.sensor_humidity = self.bme280.get_humidity()
        # g.sensor_pressure = self.bme280.get_pressure()

        # Read light intensity from BH1750
        g.sensor_light_intensity = self.bh1750.lux

    def print_sensors_data(self):
        # Print all sensor data
        print(f"Odczyt danych z czujników:")
        # print(f"Temperature: {g.sensor_temperature:.2f}°C")
        # print(f"Humidity: {g.sensor_humidity:.2f} %")
        # print(f"Pressure: {g.sensor_pressure:.2f} hPa")
        print(f"Light intensity: {g.sensor_light_intensity:.2f} lux")
        print("-" * 30)

if __name__ == "__main__":  
    sensors = Sensors()
    cpu_temp = sensors.get_cpu_temperature()
    print(f"Temperatura CPU: {cpu_temp:.2f}")
    time.sleep(2)
    sensors.read_sensors_data()
    sensors.print_sensors_data()
    time.sleep(2)
