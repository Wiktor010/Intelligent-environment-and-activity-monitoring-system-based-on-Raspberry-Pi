import time
from bme280 import BME280  # Pimoroni BME280 library
from subprocess import PIPE, Popen
import board               # Adafruit library for board configuration
import busio               # Adafruit library for I2C
import adafruit_bh1750     # Adafruit BH1750 light sensor library
from smbus2 import SMBus   # SMBus for compatibility with BME280
try:
    from scripts import globals as g  # Gdy skrypt jest używany jako moduł (plik main)
except ModuleNotFoundError:
    import globals as g  # Gdy skrypt jest uruchamiany samodzielnie

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
    g.temperature = bme280.get_temperature()
    g.humidity = bme280.get_humidity()
    g.pressure = bme280.get_pressure()

    # Read light intensity from BH1750
    g.light_intensity = bh1750.lux

def print_sensors_data():
    # Print the sensor readings
    print(f"Odczyt danych z czujników:")
    print(f"Temperature: {g.temperature:.2f}°C") #print(f"RAW Temperature: {temperature:.2f}, Compensated: {comp_temp:05.2f}°C")
    print(f"Humidity: {g.humidity:.2f} %")
    print(f"Pressure: {g.pressure:.2f} hPa")
    print(f"Light intesity: {g.light_intensity:.2f} lux")
    print("-" * 30)

if __name__ == "__main__":  
    cpu_temp = get_cpu_temperature()
    print(f"Temperatura CPU: {cpu_temp:.2f}")
    time.sleep(2)
    read_sensors_data()
    print_sensors_data()
    time.sleep(2)
