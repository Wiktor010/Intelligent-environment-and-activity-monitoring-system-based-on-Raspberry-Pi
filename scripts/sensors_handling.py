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

# Initialize SMBus for BME280
i2c_bus = SMBus(1)  # Use I2C bus 1
bme280 = BME280(i2c_dev=i2c_bus)

# Initialize I2C for BH1750 using Adafruit's busio.I2C
i2c = busio.I2C(board.SCL, board.SDA)
bh1750 = adafruit_bh1750.BH1750(i2c)

def get_cpu_temperature():
    process = Popen(["vcgencmd", "measure_temp"], stdout=PIPE)
    output, _error = process.communicate()
    output = output.decode()
    return float(output[output.index("=") + 1 : output.rindex("'")])

def read_sensors_data():
    # Read values from BME280
    g.sensor_temperature = bme280.get_temperature()
    g.sensor_humidity = bme280.get_humidity()
    g.sensor_pressure = bme280.get_pressure()

    # Read light intensity from BH1750
    g.sensor_light_intensity = bh1750.lux

def print_sensors_data():
    # Print the sensor readings
    print(f"Odczyt danych z czujników:")
    print(f"Temperature: {g.sensor_temperature:.2f}°C") 
    print(f"Humidity: {g.sensor_humidity:.2f} %")
    print(f"Pressure: {g.sensor_pressure:.2f} hPa")
    print(f"Light intesity: {g.sensor_light_intensity:.2f} lux")
    print("-" * 30)

if __name__ == "__main__":  
    cpu_temp = get_cpu_temperature()
    print(f"Temperatura CPU: {cpu_temp:.2f}")
    time.sleep(2)
    read_sensors_data()
    print_sensors_data()
    time.sleep(2)
