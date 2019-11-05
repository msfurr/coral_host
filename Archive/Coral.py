"""
CORAL BREATH DETECTION SCRIPT

WORKING VERSION

Purpose
	Gather sensor data in real time and perform predictions to actuate blowers

Outputs
	Real time actuation to blowers
	Raw data from sensors stored over period of classification
	Stored classification data

Change Log
	10.15 - Created initial script
	10.21 - Added ADS1015
	10.22 - Using "fake data" to verify that model can change predictions based on real time readings
    10.23 - Added min max scaling and second proximity sensor
    10.23 - Added derivatives of Force and Proximity sensors

"""

# Import Libraries
import ADS1015
import Proximity_Sensor
import Proximity_Sensor_2
from tflite_runtime.interpreter import Interpreter
import time

# Create helper functions
def movingAvg(Class, windowSize):
    """
    Create moving average to remove single outliers

    Args:
        Class (list): List of inhale / exhale classes
        Windowsize (int): Size of moving average window

    Returns:
        filteredClass (list): Filtered list of classes
    """
    
    filteredClass = []
    for i in range(0, len(Class)):

        if i < windowSize - 1:
            filteredClass.append(Class[i])

        elif Class[i] != Class[i - 1]:
            if sum(Class[i - (windowSize - 1):(i + 1)]) / windowSize > 1:
                filteredClass.append(2)

            elif sum(Class[i - (windowSize - 1):(i + 1)]) / windowSize < 1:
                filteredClass.append(0)

            else:
                filteredClass.append(Class[i])

        elif Class[i] == Class[i - 1]:
            filteredClass.append(Class[i])

    return filteredClass
def classSwitch(Class):
    """
    Class switch function to filter 3 classifiers down to 2 (inhale and exhale)

    Args:
        Class (list): List of inhale / exhale classes

    Returns:
        decisionClass (list): Filtered (with moving average) of resulting simplified class
    """
    
    decision = []
    switchLog = []
    for i in range(0, len(Class)):

        if i >= 1:

            if Class[i] != Class[i - 1]:
                
                # Log when it changes to 1
                if Class[i] == 1:
                    switchLog.append(i)

                # If it changes to 0 or 2, add to final
                if Class[i] == 2 or Class[i] == 0:
                    decision.append(Class[i])

            # If the values continue to be 1, change to value before switch
            if Class[i] == 1:
                decision.append(Class[switchLog[-1] - 1])

            # If the value does not change and it is not 1, add to final
            elif Class[i] == Class[i - 1] and Class[i] != 1:
                decision.append(Class[i])

        # Add first value to final

        else:
            decision.append(Class[i])

    # Return the moving average with a window of 3 for the final list
    # to remove jumps between classes
    return movingAvg(decision, 3)

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
Raw_Data = []
Predictions = []

# Create data scaling ranges
Min_Force = 1500
Max_Force = 28000
Min_Proximity = 2100
Max_Proximity = 16000

# Instantiate TF Lite Model
interpreter = Interpreter(model_path = "my_tflite_model_4.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
print('Model Initiatized')

while(True):

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

    # Pull real time data into input tensor for classification
    data = np.float32([[Force, d_Force, Proximity_1, d_Proximity_1, Proximity_2, d_Proximity_2, Force, Force]])
    Raw_Data.append(data)
    input_data = data
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    if len(Predictions) < 50:
        Current_Class = np.argmax(interpreter.get_tensor(output_details[0]['index']))
        Predictions.append(np.argmax(interpreter.get_tensor(output_details[0]['index'])))
        print(Current_Class)

    else:
        Predictions.append(np.argmax(interpreter.get_tensor(output_details[0]['index'])))
        Predictions = classSwitch(Predictions)
        Current_Class = Predictions[-1]
        print('  ', Current_Class)
        print('  ~~~  ')