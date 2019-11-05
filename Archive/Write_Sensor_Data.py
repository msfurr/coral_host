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
proximity_1 = Proximity_Sensor.VCNL4010()
proximity_2 = Proximity_Sensor_2.VCNL4010()

# Create storage lists
ForceData = []
ProximityData_1 = []
ProximityData_2 = []
d_ForceData = []
d_ProximityData_1 = []
d_ProximityData_2 = []
timeTracker = []

# Set scaling ranges
Min_Force = 1500
Max_Force = 28000
Min_Proximity = 2100
Max_Proximity = 16000

# Initiatize timer
startTime = time.time()

print('Reading Google Coral Data values, press Ctrl-C to quit...')

# Print column headers
print('|  ADS    | VCNL_1 | VCNL_2 |  Time  |  dADS  |dVCNL_1 |dVCNL_2  |'.format(*range(2)))
print('-' * 60)

for i in range(0, 700):
    # Read all the ADC channel values in a list
    values = [0]*7

    # Read force, proximity, and time values
    Force = adc.read_adc(0, gain = 2/3)
    Proximity_1 = proximity_1.proximity
    Proximity_2 = proximity_2.proximity
    timeTracker.append(time.time() - startTime)

    # Scale 0-1 according to projected min and max values
    # Force
    if adc.read_adc(0) > Max_Force:
        Force = 1
    elif adc.read_adc(0) < Min_Force:
        Force = 0
    else:
        Force = (adc.read_adc(0) - Min_Force) / (Max_Force - Min_Force)

    # Proximity_1
    if proximity_1.proximity > Max_Proximity:
        Proximity_1 = 1
    elif proximity_1.proximity < Min_Proximity:
        Proximity_1 = 0
    else:
        Proximity_1 = (proximity_1.proximity - Min_Proximity) / (Max_Proximity - Min_Proximity)

    # Proximity_2
    if proximity_2.proximity > Max_Proximity:
        Proximity_2 = 1
    elif proximity_2.proximity < Min_Proximity:
        Proximity_2 = 0
    else:
        Proximity_2 = (proximity_2.proximity - Min_Proximity) / (Max_Proximity - Min_Proximity)

    # Save data to respective lists
    ForceData.append(Force)
    ProximityData_1.append(Proximity_1)
    ProximityData_2.append(Proximity_2)

    # Gather derivative data
    # Force
    if len(ForceData) > 1:
        d_Force = (ForceData[-1] - ForceData[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Force = 0

    # Proximity 1
    if len(ProximityData_1) > 1:
        d_Proximity_1 = (ProximityData_1[-1] - ProximityData_1[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Proximity_1 = 0

    # Proximity 2
    if len(ProximityData_2) > 1:
        d_Proximity_2 = (ProximityData_2[-1] - ProximityData_2[-2]) / (timeTracker[-1] - timeTracker[-2])
    else:
        d_Proximity_2 = 0

    # Save derivative data
    d_ForceData.append(Force)
    d_ProximityData_1.append(Proximity_1)
    d_ProximityData_2.append(Proximity_2)

    # Format data to view in console
    values[0] = Force
    values[1] = Proximity_1
    values[2] = Proximity_2
    values[3] = timeTracker[-1]
    values[4] = d_Force
    values[5] = d_Proximity_1
    values[6] = d_Proximity_2
    print('|', '%.4f'%values[0], ' |', '%.4f'%values[1], '|', '%.4f'%values[2], '|', '%.4f'%values[3], '|', '%.4f'%values[4], '|', '%.4f'%values[5], '|', '%.4f'%values[6], '|')
    # Pause for display
    time.sleep(0)

# Excel Spreadsheet (within current folder)
SensorData = {'timeTracker': timeTracker, 'Force': ForceData, 'Proximity_1': d_ProximityData_1, 'Proximity_2': ProximityData_2, 'd_Force': d_ForceData, 'd_Proximity_1': d_ProximityData_1, 'd_Proximity_2': d_ProximityData_2}
Results = pd.DataFrame(data = SensorData)
writer = pd.ExcelWriter('SensorData.xlsx', engine='xlsxwriter')
Results.to_excel(writer, sheet_name = 'Sheet1')
writer.save()