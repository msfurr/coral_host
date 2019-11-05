# Import Libraries
import Proximity_Sensor
import time

# Setup Sensor Objects
Proximity = Proximity_Sensor.VCNL4010()

# Instantiate TF Lite Model
interpreter = Interpreter(model_path = "my_tflite_model_4.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Create Empty Data Storage
Raw_Data = []
Predictions = []

while(True):

	input_data = np.float32([Proximity.proximity])
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

return Predictions

"""
Place Data Acq in its own thread
Then create a buffer between for holding the data
Then classify off of the most recent data
"""