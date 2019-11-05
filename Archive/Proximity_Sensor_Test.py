"""
VCNL4010 PROXIMITY SENSOR TEST

WORKING VERSION

DESCRIPTION
    Pulls values from the proximity sensor on the Coral and prints result

"""

import time

# Import the ADS1x15 module.
import Proximity_Sensor

# Create object
sensor = Proximity_Sensor.VCNL4010()

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