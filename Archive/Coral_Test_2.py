"""
SENSOR READ TEST

WORKING VERSION

DESCRIPTION
	Read all values from Google Coral data collection and prints in table format


"""

# Import libraries
import time
import ADS1015
import Proximity_Sensor
from tflite_runtime.interpreter import Interpreter
import numpy as np

# Create objects
adc = ADS1015.ADS1015()
proximity = Proximity_Sensor.VCNL4010()

Min_Force = 15500
Max_Force = 28000

Min_Proximity = 2100
Max_Proximity = 16000

# Instantiate TF Lite Model
interpreter = Interpreter(model_path = "my_tflite_model_4.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Create Empty Data Storage
Raw_Data = []
Predictions = []

while True:

    # Scale 0-1 according to projected min and max values
    if adc.read_adc(0) > Max_Force:
    	Force = 1
    elif adc.read_adc(0) < Min_Force:
    	Force = 0
    else:
    	Force = (adc.read_adc(0) - Min_Force) / (Max_Force - Min_Force)

    if proximity.proximity > Max_Proximity:
    	Proximity = 1
    elif proximity.proximity < Min_Proximity:
    	Proximity = 0
    else:
    	Proximity = (proximity.proximity - Min_Proximity) / (Max_Proximity - Min_Proximity)

    data = np.float32([[Proximity, Proximity, Force, Force, Proximity, Proximity, Force, Force]])
    Raw_Data.append(data)

    input_data = data

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    Current_Class = np.argmax(interpreter.get_tensor(output_details[0]['index']))
    Predictions.append(np.argmax(interpreter.get_tensor(output_details[0]['index'])))
    print(Current_Class)
    print('   ')


