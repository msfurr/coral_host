"""
VCNL4010 PROXIMITY SENSOR TEST

WORKING VERSION

DESCRIPTION
    Pulls values from the proximity sensor on the Coral and prints result

"""

import time

# Import the Proximity Library
import Proximity_Sensor_2

# Create object
sensor = Proximity_Sensor_2.VCNL4010()

print('Reading VCNL4010 values, press Ctrl-C to quit...')

# Print a column header
print('| VCNL4010 Values |')
print('-' * 20)

while True:
    # Read all the values into a list
    value = sensor.proximity
    print(value)
    # Pause for half a second.
    time.sleep(0.5)