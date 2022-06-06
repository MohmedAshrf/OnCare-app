import random,time
HB= 0
SpO2=0
ecg= list()
ecg_r = 0
Co2 =0
temp =0
r = open("reading.txt", "w")
p = open("Predictions.txt", "w")
def add_to_p(text):
    if type(text) != 'str':
        text = str(text)
    p.seek(0)
    p.write(text+'\n')

def add_to_r(text):
    if type(text) != 'str':
        text = str(text)
    r.seek(0)
    r.write(text+'\n')
    
while True:
    try:
        data = {"HB":random.randint(100,140),"temp":random.randint(35,40), \
        "SpO2":random.randint(90,100),"ecg":random.randint(300,900),"Co2":random.randint(100,500)}
        #print(data)
        start = time.time()
        add_to_r(data)
        add_to_p("Normal Beat")
        print(time.time()-start)
    except Exception as e:
            print(e)
            r.close()
            p.close()