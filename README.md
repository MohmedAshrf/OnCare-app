# OnCare-app

## Introduction:

An app which is installed on the Rasperry pi and resposable for uplading the patient's data to the database.

I am using the Raspberry Pi (RPI) as an interface between the Arduino which sends the sensors data, and the Database.

RPI takes the sensor’s data from the Arduino using a serial communication UART and sends this data to the Firebase Realtime database through a wireless connection. So, the end-user ex. the doctor will be able to see the indications of each patient.

RPI sends the data to the cloud (Firebase). And the Mobile and the LabVIEW applications will retrieve the data from the firebase and display it to the doctor and anyone who has the access to the server. 
