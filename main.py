import time
from bme280 import BME280  # Pimoroni BME280 library
import board               # Adafruit library for board configuration
import busio               # Adafruit library for I2C
import adafruit_bh1750     # Adafruit BH1750 light sensor library
from smbus2 import SMBus   # SMBus for compatibility with BME280

# Initialize SMBus for BME280
i2c_bus = SMBus(1)  # Use I2C bus 1
bme280 = BME280(i2c_dev=i2c_bus)

# Initialize I2C for BH1750 using Adafruit's busio.I2C
i2c = busio.I2C(board.SCL, board.SDA)
bh1750 = adafruit_bh1750.BH1750(i2c)

# Main loop to read and print sensor values
# while True:
#     # Read values from BME280
#     temperature = bme280.get_temperature()
#     humidity = bme280.get_humidity()
#     pressure = bme280.get_pressure()

#     # Read light intensity from BH1750
#     light_level = bh1750.lux

#     # Print the sensor readings
#     print(f"Temperature: {temperature:.2f} °C")
#     print(f"Humidity: {humidity:.2f} %")
#     print(f"Pressure: {pressure:.2f} hPa")
#     print(f"Light Level: {light_level:.2f} lux")
#     print("-" * 30)

#     # Wait a few seconds before reading again
#     time.sleep(2)
