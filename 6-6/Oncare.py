import PySimpleGUI as sg
import json
import pyrebase
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import threading
from subprocess import call
def thread_second():
    call(["python", "testconv.py > out.txt &"]) # will be replaced by updateInBackground.py
processThread = threading.Thread(target=thread_second)
processThread.start()

config = {
#place your config from your firebase project console
}
  
Valid_user = False
user_id=''
user_token=''

#initial values
HP= 0
SpO2=0
ecg= 0
Co2 =0
temp =0
Aiclassification=""
readings={}

#Database initalizaion
firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()
#firestore
cred = credentials.Certificate("spry-autumn-250814-firebase-adminsdk-wqkqc-f98064d5a3.json")
firebase_admin.initialize_app(cred)
fire = firestore.client()

sg.theme('DarkGreen3')

email = ''
password = ''
Description = ''
Government=''
phone = ''
gender = ''
name=''
age=''
list_gov=["Alexandria","Assiut","Aswan","Beheira","Bani Suef","Cairo","Daqahliya","Damietta","Fayyoum","Gharbiya","Giza","Helwan","Ismailia","Kafr El Sheikh","Luxor","Marsa Matrouh","Minya"
    ,"Monofiya","New Valley","North Sinai","Port Said","Qalioubiya"
    ,"Qena","Red Sea","Sharqiya","Sohag","South Sinai","Suez","Tanta"]

class keyboard():
    def __init__(self, location=(None, None), font=('Arial', 16)):
        sg.theme('DarkGreen4')
        self.location = location
        self.font = font
        numberRow = '@1234567890'
        topRow = 'QWERTYUIOP'
        midRow = 'ASDFGHJKL'
        bottomRow = 'ZXCVBNM.'
        keyboard_layout = [[sg.Button(c, key=c, size=(2, 1), font=self.font) for c in numberRow] + [
            sg.Button('⌫', key='back', size=(2, 1), font=self.font),
            sg.Button('ESC', key='close', size=(4, 1), font=self.font)],
            [sg.Text(' ' * 2)] + [sg.Button(c, key=c.lower(), size=(2, 1), font=self.font) for c in
                               topRow] + [sg.Stretch()],
            [sg.Text(' ' * 5)] + [sg.Button(c, key=c.lower(), size=(2, 1), font=self.font) for c in
                                midRow] + [sg.Stretch()],
            [sg.Text(' ' * 9)] + [sg.Button(c, key=c.lower(), size=(2, 1), font=self.font) for c in
                                bottomRow] + [sg.Stretch()]]

        self.window = sg.Window('keyboard', keyboard_layout, keep_on_top=True, alpha_channel=0,
                                no_titlebar=True, element_padding=(5, 5), location=location, finalize=True,margins=(2, 2))
        self.hide()

    def _keyboardhandler(self):
        self.location = self.window.current_location()
        if self.event is not None:
            if self.event == 'close':
                self.hide()
            elif len(self.event) == 1:
                self.focus.update(self.focus.Get() + self.event)
            elif self.event == 'back':
                Text = self.focus.Get()
                if len(Text) > 0:
                    Text = Text[:-1]
                    self.focus.update(Text)

    def hide(self):
        self.visible = False
        self.window.Disappear()

    def show(self):
        self.visible = True
        self.window.Reappear()

    def togglevis(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def update(self, focus):
        self.event, _ = self.window.read(timeout=0)
        if focus is not None:
            self.focus = focus
        self._keyboardhandler()

    def close(self):
        self.window.close()
        sg.theme('DarkGreen3')


#Functions:
def progress_bar(id,token):
    layout = [[sg.Text('Uploading ...')],
            [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progbar', bar_color=('brown','white'))],
            [sg.Cancel()]]

    window = sg.Window('Please wait', layout)
    for i in range(100):
        event, values = window.read(timeout=1)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        if i ==50:
            upload_readings(id,token)
            window['progbar'].update_bar(i + 50)
        window['progbar'].update_bar(i + 1)
    window.close()

def create_account():
    global email, password,Valid_user,phone,Description,gender,name,age
    if Valid_user: #create new user and delete the past email and password
        email=''
        password = ''
        
    layout = [[sg.Text("Email", size =(10, 1),font=16), sg.InputText(email,key='-email-', font=16)],
             [sg.Text("Password", size =(10, 1), font=16), sg.InputText(password,key='-pwd-', font=16, password_char='*')],
              [sg.Text("Name", size =(10, 1), font=16), sg.InputText(name,key='-name-', font=16)],
              [sg.Text("Age", size =(10, 1), font=16), sg.InputText(age,key='-age-', font=16)],
              [sg.Text("Gender", size =(10, 1), font=16),sg.Radio('Male', "RADIO1", default=True, key="-M-")\
               ,sg.T("         "), sg.Radio('Female', "RADIO1", default=False , key ='-F-')],
              [sg.Text("Phone", size =(10, 1), font=16), sg.InputText(phone,key='-phone-', font=16)],
              [sg.Text("Governorate", size =(10, 1), font=16),sg.Combo(list_gov,default_value='Cairo',key='-Government-',size =(10, 1),font=16)],
              [sg.Text("Description", size =(10, 1), font=16), sg.InputText(Description,key='-Description-', font=10)],
             [sg.Button("Submit"), sg.Button("Cancel")]]
    window = sg.Window("Sign Up", layout, no_titlebar=False, finalize=True,location=(14,46),resizable=True,grab_anywhere=True)
    window.Maximize()
    window['-email-'].bind('<FocusIn>', '')
    window['-pwd-'].bind('<FocusIn>', '')
    window['-name-'].bind('<FocusIn>', '')
    window['-age-'].bind('<FocusIn>', '')
    window['-phone-'].bind('<FocusIn>', '')
    window['-Description-'].bind('<FocusIn>', '')
    window['-M-'].bind('<FocusIn>', '')
    window['-F-'].bind('<FocusIn>', '')
    window['-Government-'].bind('<FocusIn>', '')
    
    kboard = keyboard((-10,320)) #after trail and error on the RPI
    
    focus = None    
    window.Element('-email-').SetFocus()
    
    while True:
        cur_focus = window.find_element_with_focus()
        if cur_focus is not None:
            focus = cur_focus   
        event,values = window.read(timeout=50, timeout_key='timeout')
        if focus is not None:
            kboard.update(focus)
        if event == '-email-' or event == "-pwd-" or event == "-name-"\
        or event == "-age-" or event == "-phone-" or event == "-Description-" or event == "-Government-":
            kboard.show()
            #kboard.update(focus)
        if values['-F-'] == True:
            gender = "Female"
        if values['-M-'] == True:
            gender = "Male"
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            Valid_user=False
            break    
        else:
            if event == "Submit":
                kboard.close()
                password = values['-pwd-']
                email = values['-email-']
                name = values["-name-"]
                age = values["-age-"]
                phone = values["-phone-"]
                Government = values["-Government-"]
                Description = values["-Description-"]
                try:
                    user_id , user_token = create_user(email,password,name,age,phone,Description,gender,Government)
                    doc_ref = fire.collection('users').document(user_id)
                    doc_ref.set({
                        'date': datetime.now(),
                        'email': email,
                        'name': name,
                        'uid': user_id
                    })
                    window.close()
                    sg.popup("Sucessfully created user. uploading the data...")
                    Valid_user = True
                    progress_bar(user_id,user_token)
                    sg.popup("Data uploaded. login to display")
                    login_existing(email,password)
                    break
                except Exception as e:
                    try:
                        res= json.loads(e.args[1])
                        Valid_user = False
                        if res["error"]["message"] == "INVALID_EMAIL":
                            print("please write a valid email")
                            sg.popup_auto_close("Invalid Email",title="Error")
                            kboard.close()
                            create_account()
                            break
                        elif res["error"]["message"] == "EMAIL_EXISTS":
                            print("please login")
                            sg.popup_ok("Email exists",title="Error")
                            login_existing(email,password)
                            kboard.close()
                            window.close()
                            break
                        elif res["error"]["message"].split(" ")[0] == "WEAK_PASSWORD":
                            print("please enter longer password")
                            sg.popup_ok("Weak password",title="Error")
                            kboard.close()
                            create_account()
                            break
                        else:
                            print("please review the error: "+ res["error"]["message"])
                            sg.popup_ok(res["error"]["message"],title="Error")
                            kboard.close()
                            create_account()
                            break
                    except:
                        sg.popup_auto_close("Please check the Wi-Fi connection",title="Error")
                        window.close()
                        kboard.close()
                break
    kboard.close()
    window.close()
    


def login_existing(e="",p=""):
    global email,password,Valid_user,user_id,user_token
    layout = [[sg.Text('Please enter you email and password')],
            [sg.Text("Email", size =(15, 1), font=16),sg.InputText(e,key='-email-', font=16)],
            [sg.Text("Password", size =(15, 1), font=16),sg.InputText(p,key='-pwd-', password_char='*', font=16)],
            [sg.Button('Ok'),sg.Button('Cancel')]]
    
    window = sg.Window('Login', layout, no_titlebar=False, finalize=True,location=(14,46),resizable=True,grab_anywhere=True)
    window.Maximize()
    window['-email-'].bind('<FocusIn>', '')
    window['-pwd-'].bind('<FocusIn>', '')
    
   
    kboard = keyboard((-7,245))
    
    focus = None
    window.Element('-email-').SetFocus()
    while True:
        cur_focus = window.find_element_with_focus()
        if cur_focus is not None:
            focus = cur_focus   
        event,values = window.read(timeout=50, timeout_key='timeout')
        if focus is not None:
            kboard.update(focus)
        if event == '-email-' or event == "-pwd-":
            kboard.show()
            #kboard.update(focus)
            
        elif event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        else:
            if event == "Ok":
                kboard.close()
                password = values['-pwd-']
                email = values['-email-']
                try:
                    user_id,user_token = login_to_user(email,password)
                    window.close()
                    sg.popup("Sucessfully logged in")
                    Valid_user = True #loged in successfully 
                    progress_bar(user_id,user_token)
                    #sg.popup("Data uploaded")
                    #read_data(get_data(user_id,user_token))
                    display_data(user_id,user_token)
                    break
                except Exception as e:
                    print(e)
                    try:
                        res= json.loads(e.args[1])
                        if res["error"]["message"] == "INVALID_PASSWORD":
                            print("Please check the password and try again")
                            sg.popup_auto_close("Please check the password and try again",title="Error")
                            window.close()
                            password = ""
                            login_existing(email,password) #password incorrect retry
                            break
                        elif res["error"]["message"] == "INVALID_EMAIL":
                            print("Please check the Email and try again")
                            sg.popup_auto_close("Please check the Email and try again",title="Error")
                            kboard.close()
                            window.close()
                            break
                        elif res["error"]["message"] == "EMAIL_NOT_FOUND":
                            print("Email not found please signup")
                            sg.popup_auto_close("Email not found please signup",title="Error")
                            kboard.close()
                            window.close()
                            create_account()
                        else:
                            print("Please check the error",res["error"]["message"])
                            kboard.close()
                            window.close()
                            break
                    except:
                        sg.popup_auto_close("Please check the Wi-Fi connection",title="Error")
                        window.close()
                        kboard.close()
                break
    kboard.close()
    window.close()
    
def display_data(id="",token=""):
    to_be_centered = [[sg.Text("Heart Beat", size =(15, 1),font=16), sg.Text(HP,size = (30,1),pad=(40, (10, 0)), font=16,key='-HP-')],
              [sg.Text("Tempreture", size =(15, 1),font=16), sg.Text(temp, font=16,size = (30,1),pad=(40, (10, 0)),key='-temp-')],
              [sg.Text("SpO2", size =(15, 1),font=16), sg.Text(SpO2, font=16,size = (30,1),pad=(40, (10, 0)),key='-sp-')],
              [sg.Text("Co2", size =(15, 1),font=16), sg.Text(Co2, font=16,size = (30,1),pad=(40, (10, 0)) ,key='-Co2-')],
              [sg.Text("ECG", size =(15, 1),font=16), sg.Text(ecg, font=16 ,size = (30,1),pad=(40, (10, 0)),key='-ecg-')],
              [sg.Text("Classification", size =(15, 1),font=16), sg.Text(ecg, font=16 ,size = (30,1),key='-class-')],
                [sg.Button("Cancel",size=(20,2),pad=(60, (20, 0)))]]
    layout = [[sg.Column(to_be_centered, vertical_alignment='center',pad=(600,200,0,0))]]
    window=sg.Window("Readings", layout, resizable=True,finalize=True,grab_anywhere=True)
    window.Maximize()
    while True:
        event, values = window.read(timeout=10)
        if token != "": #if user has signed in
            read_data(upload_readings(id,token)) #upload the data then read
        else:
            read_data(set_data_UART()) #read the data wihout upload
            
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            window.close()
            break
        else:
            window['-HP-'].update(HP)
            window['-temp-'].update(temp)
            window['-sp-'].update(SpO2)
            window['-Co2-'].update(Co2)
            window['-ecg-'].update(ecg)
            window['-class-'].update(Aiclassification)
            
def login_to_user(email,passwd):
    user = auth.sign_in_with_email_and_password(email,passwd)
    return (user["localId"],user["idToken"])
    

def upload_readings(uid,token):
    data = set_data_UART()
    db.child("patients").child(uid).child("readings").set(data,token)
    return data

def create_user(email,password,name,age,phone,Description,gender,Government):
    user = auth.create_user_with_email_and_password(email,password)
    uid = user["localId"]
    token = user["idToken"]
    data={"Name":name,"Email":email,"age":age,"Gender":gender,"Governorate":Government,"Description":Description,"phoneNumber":phone}
    db.child("patients").child(uid).set(data,token)
    return (uid,token)
    
def get_data(uid,token):
    return dict(db.child("patients").child(uid).child("readings").get(token).val())

def read_data(dic):
    global HP,SpO2,ecg,Co2,temp,Aiclassification
    HP = dic["HB"]
    SpO2 = dic["SpO2"]
    ecg = dic["ecg"]
    Co2 = dic["Co2"]
    temp = dic["temp"]
    Aiclassification = dic["Aiclassification"]

    
def set_data_UART():
    global classification,readings
    line =''
    with open('reading.txt','r') as f:
        line = f.readline()
    if line != '':
        line = line.replace("\'", "\"")
        readings = json.loads(line)
    line = ''
    readings["Aiclassification"] = "still working"
    with open('Predictions.txt','r') as f:
        line = f.readline()
    if line != '':
        classification = line
        readings["Aiclassification"] = classification
    return readings


def select_option():
    my_img = sg.Image(filename="oncarelogo3.png",key='-Logo-',pad = (60,30,10,60))
    column_to_be_centered = [[sg.Text('Welcome!',size=(30,1),justification='c')],
                             [sg.Text('Please Select an Option',size=(30,1),justification='c')],
            [sg.Button('Login',size=(30,2))],
            [sg.Button('Signup',size=(30,2))],
            [sg.Button('Display Offline',size=(30,2))],
            [sg.Button('Cancel',size=(30,2))]]
    
    
    layout = [[sg.Text('', pad=(0,0)),              # the thing that expands from left
               [sg.Column([[my_img]], justification='center')],
               sg.Column(column_to_be_centered, vertical_alignment='center', 
                         justification='center')]]
    
    window = sg.Window('OnCare', layout, resizable=True,finalize=True,grab_anywhere=True, no_titlebar=False, use_default_focus=False)
    window.Maximize()
    
    while True:
        event, values = window.read(timeout=100)
        if(Valid_user):
            read_data(upload_readings(user_id,user_token))
        else:
            read_data(set_data_UART())
        if event == 'Cancel' or event == sg.WIN_CLOSED:
            break
        elif (event == "Login"):
            login_existing()
        elif (event == "Signup"):
            create_account()
        elif (event == "Display Offline"):
            display_data(user_id,user_token)
            
    window.close()
    
select_option()
