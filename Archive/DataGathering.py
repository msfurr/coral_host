"""
DESCRIPTION
	Current working version of data collection code
	Pull data in real time, perform inference based on given TFLite model
"""

# Import Libraries
import Proximity_Sensor
import ADS1015
import time

# Setup Sensor Objects
Proximity = Proximity_Sensor.VCNL4010()
Force = ADS1015.ADS1015()

# Instantiate TF Lite Model
interpreter = Interpreter(model_path = "my_tflite_model_4.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Create Empty Data Storage
Raw_Data = []
Predictions = []

while(True):

	input_data = np.float32([Proximity.proximity, Force.read_adc(0), Force.read_adc(0), Force.read_adc(0), Force.read_adc(0), Force.read_adc(0), Force.read_adc(0), Force.read_adc(0)])
	Raw_Data.append(input_data)

	interpreter.set_tensor(input_details[0]['index'], input_data)
	interpreter.invoke()

	if len(Predictions) < 5:
		Current_Class = np.argmax(interpreter.get_tensor(output_details[0]['index']))
		Predictions.append(np.argmax(interpreter.get_tensor(output_details[0]['index'])))
		print(Current_Class)

	else:
		Predictions.append(np.arg(interpreter.get_tensor(output_details[0]['index'])))
		Predictions = classSwitch(Predictions)
		Current_Class = Predictions[-1]
		print(Current_Class)

	if len(Predictions) > 1:
		print(Predictions[-1])

"""
FUTURE WORK
Place Data Acq in its own thread
Then create a buffer between for holding the data
Then classify off of the most recent data
"""