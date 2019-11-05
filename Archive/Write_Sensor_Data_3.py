"""
WRITE SENSOR DATA

WORKING VERSION

DESCRIPTION
	Read all values from Google Coral data collection for a 
    specified sample size then write to a csv file


"""

# Import libraries
import time
import ADS1015
import Proximity_Sensor
import Proximity_Sensor_2
from numpy import diff
import pandas as pd

# Create objects
adc = ADS1015.ADS1015()

# Create storage lists
Sensor_1_Data = []
Sensor_2_Data = []
Sensor_3_Data = []
Sensor_4_Data = []

d_Sensor_1_Data = []
d_Sensor_2_Data = []
d_Sensor_3_Data = []
d_Sensor_4_Data = []

timeTracker = []

# Set scaling ranges
Min_1 = 7000
Max_1 = 9000

Min_2 = 7000
Max_2 = 10000

Min_3 = 8000
Max_3 = 12000

Min_4 = 18000
Max_4 = 23000

# Initiatize timer
startTime = time.time()

print('Reading Google Coral Data values, press Ctrl-C to quit...')

# Print column headers
print('|  1    |   2   |   3   |  4  |   Time   |   d_1   |   d_2   |   d_3   |   d_4   |'.format(*range(2)))
print('-' * 60)

for i in range(0, 10000):
    # Read all the ADC channel values in a list
    values = [0]*8

    # Read force, proximity, and time values
    Sensor_1 = adc.read_adc(0, gain = 4)
    Sensor_2 = adc.read_adc(1, gain = 4)
    Sensor_3 = adc.read_adc(2, gain = 4)
    Sensor_4 = adc.read_adc(3, gain = 4)
    timeTracker.append(time.time() - startTime)

    # Save data to respective lists
    Sensor_1_Data.append(Sensor_1)
    Sensor_2_Data.append(Sensor_2)
    Sensor_3_Data.append(Sensor_3)
    Sensor_4_Data.append(Sensor_4)

    # Gather derivative data
    # Sensor 1
    if len(Sensor_1_Data) > 1:
        d_Sensor_1 = (Sensor_1_Data[-1] - Sensor_1_Data[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Sensor_1 = 0

    if len(Sensor_2_Data) > 1:
        d_Sensor_2 = (Sensor_2_Data[-1] - Sensor_2_Data[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Sensor_2 = 0

    if len(Sensor_3_Data) > 1:
        d_Sensor_3 = (Sensor_3_Data[-1] - Sensor_3_Data[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Sensor_3 = 0

    if len(Sensor_4_Data) > 1:
        d_Sensor_4 = (Sensor_4_Data[-1] - Sensor_4_Data[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Sensor_4 = 0

    # Save derivative data
    d_Sensor_1_Data.append(d_Sensor_1)
    d_Sensor_2_Data.append(d_Sensor_2)
    d_Sensor_3_Data.append(d_Sensor_3)
    d_Sensor_4_Data.append(d_Sensor_4)

    # Format data to view in console
    values[0] = Sensor_1
    values[1] = Sensor_2
    values[2] = Sensor_3
    values[3] = Sensor_4
    values[4] = d_Sensor_1
    values[5] = d_Sensor_2
    values[6] = d_Sensor_3
    values[7] = d_Sensor_4
    print('|', '%.4f'%values[0], ' |', '%.4f'%values[1], '|', '%.4f'%values[2], '|', '%.4f'%values[3], '|', '%.4f'%values[4], '|', '%.4f'%values[5], '|', '%.4f'%values[6], '|', '%.4f'%values[7], '|')
    # Pause for display
    time.sleep(0)

# Excel Spreadsheet (within current folder)
SensorData = {'timeTracker': timeTracker, 'Sensor 1': Sensor_1_Data, 'Sensor 2': Sensor_2_Data, 'Sensor 3': Sensor_3_Data, 'Sensor 4': Sensor_4_Data, 'd_Sensor 1': d_Sensor_1_Data, 'd_Sensor 2': d_Sensor_2_Data, 'd_Sensor 3': d_Sensor_3_Data, 'd_Sensor 4': d_Sensor_4_Data}
Results = pd.DataFrame(data = SensorData)
writer = pd.ExcelWriter('SensorData.xlsx', engine='xlsxwriter')
Results.to_excel(writer, sheet_name = 'Sheet1')
writer.save()