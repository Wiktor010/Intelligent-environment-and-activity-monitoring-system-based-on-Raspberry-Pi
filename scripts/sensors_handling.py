import time
from bme280 import BME280  # Pimoroni BME280 library
from subprocess import PIPE, Popen
import board               # Adafruit library for board configuration
import busio               # Adafruit library for I2C
import adafruit_bh1750     # Adafruit BH1750 light sensor library
from smbus2 import SMBus   # SMBus for compatibility with BME280
# from globals

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

# factor = 0.9  # Smaller numbers adjust temp down, vice versa
# smooth_size = 10  # Dampens jitter due to rapid CPU temp changes

# cpu_temps = []


# Main loop to read and print sensor values
def read_sensors_data():

    # Read values from BME280
    temperature = bme280.get_temperature()
    humidity = bme280.get_humidity()
    pressure = bme280.get_pressure()

    # cpu_temp = get_cpu_temperature()
    # cpu_temps.append(cpu_temp)

    # if len(cpu_temps) > smooth_size:
    #     cpu_temps = cpu_temps[1:]

    # smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

    # comp_temp = temperature - ((smoothed_cpu_temp - temperature) / factor)

    # Read light intensity from BH1750
    light_level = bh1750.lux

    # Print the sensor readings
    print(f"RAW Temperature: {temperature:.2f}°C") #print(f"RAW Temperature: {temperature:.2f}, Compensated: {comp_temp:05.2f}°C")
    print(f"Humidity: {humidity:.2f} %")
    print(f"Pressure: {pressure:.2f} hPa")
    print(f"Light Level: {light_level:.2f} lux")
    print("-" * 30)