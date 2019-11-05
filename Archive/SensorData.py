import smbus2
import time
import Proximity_Sensor

sensor = Proximity_Sensor.VCNL4010()

while True:

	print(sensor.proximity)