# upy-mpu6050
A micro python library to interact with the MPU6050 for an ESP32 microcontoller

# Installation 
Just copy the mpu_6050 directory to your microcontroller and import the MPU6050 class.

# Example Usage
```python
from machine import SoftI2C, Pin
from mpu_6050 import MPU6050

# Replace YOUR_SCL_PIN_NUMBER and YOUR_SDA_PIN_NUMBER with the corresponding pins connected to the MPU6050.
i2c = SoftI2C(scl=Pin(YOUR_SCL_PIN_NUMBER), sda=Pin(YOUR_SDA_PIN_NUMBER))

# Create the sensor object
sensor = MPU6050(i2c)

# Read the current acceleration in meters / second^2
x, y, z = sensor.read_accelerometer_meters()
print(f"(x: {x:.2f}, y: {y:.2f}, z: {z:.2f})")
# Outputs: "(x: -0.14, y: 0.29, z: 9.43)"

# Read the current rotation in degrees / second
x, y, z = mpu.read_gyroscope_degrees()
# Outputs: "(x: -3.43, y: 0.18, z: 1.27)"

# Read the current temperature in degrees celsius
temperature = mpu.read_temperature_degrees()
print(f"Temperature: {temperature:.2f}")
# Outputs: "Temperature: 23.21"
```
