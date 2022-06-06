print("Importing tensorflow")
import tensorflow as tf
print("tensorflow imported")
import serial
import time
import numpy as np
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()

new_model = tf.keras.models.load_model('model.h5')
HB= 0
SpO2=0
ecg= list()
ecg_r = 0
Co2 =0
temp =0
counter = 0
def detect_condition(number):
    if number == 0:
        return "Normal Beat"
    if number == 1:
        return "Unknown"
    if number == 2:
        return "Ventricular Ectopic Beat"
    if number == 3:
        return "Supraventricular Ectopic Beat"
    if number == 4:
        return "Fusion Beat"
def add_ecg(reading):
    global counter, ecg
    if counter <186:
        ecg.append(int(reading))
        counter +=1
    if counter == 186:
        counter = 0
        return 1
    return 0

def get_predictions(lst):
    ecg_array = np.array(lst)
    ecg_array = ecg_array.reshape(1, 186, 1)
    ecg_array = ecg_array/1000
    predictions = new_model.predict(ecg_array)
    predictions=int(np.argmax(predictions,axis=1))
    return predictions
def add_to_ecg_file(text):
    f = open("ecg.txt", "w")
    if type(text) != 'str':
        text = str(text)
    f.write(text)
    f.close()

def add_to_p(text):
    f = open("Predictions.txt", "w")
    if type(text) != 'str':
        text = str(text)
    f.write(text)
    f.close()

def add_to_r(text):
    f = open("reading.txt", "w")
    if type(text) != 'str':
        text = str(text)
    f.write(text)
    f.close()

while True:
    print("checking the connection")
    if ser.in_waiting > 0:
        try:
            print("ecg",ecg_r,"temp= ",temp,"Spo2= ",SpO2,"HB= ",HB,"Co2= ",Co2)
            data = {"ecg":ecg_r,"temp":temp,"SpO2":SpO2,"HB":HB,"Co2":Co2}
            add_to_r(data)
            line = ser.readline().decode('utf-8').rstrip()
            line = line.split(":")
            if line[0] == "ecg":
                ecg_r = line[1]
                if(add_ecg(line[1]) == 1):
                    add_to_ecg_file(ecg)
                    add_to_p(detect_condition(get_predictions(ecg)))
                    ecg = []
            elif line[0] == "SpO2":
                SpO2 = line[1]
            elif line[0] == "Co2":
                Co2 = line[1]
            elif line[0] == "HB":
                HB = line[1]
            elif line[0] == "temp":
                temp = line[1]
        except Exception as e:
            print(e)

            
    