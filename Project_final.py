from machine import Pin, ADC, I2C
import time
from fifo import Fifo
from piotimer import Piotimer
import ssd1306
import math
import network
import urequests as requests
import json

class isr_fifo(Fifo):
    def __init__(self,size,adc_pin_nr):
        super().__init__(size)
        self.av = ADC(adc_pin_nr )# sensor AD channel
    def handler(self, tid):
        #handler to read and store ADC value
        #this is to be registered as an ISR. Floats are not available in ISR
        self.put(self.av.read_u16())

def Sample_lst():
    lst = []
    for i in range(750):
        lst.append(samples.get())
        time.sleep(.004)
    return lst

def Avg(sample_lst):
    average = sum(sample_lst)/len(sample_lst)
    return round(average)

def Peak_lst(sample_lst):
    lst = []
    avg = Avg(sample_lst)
    thrshold = avg + (max(sample_lst)-min(sample_lst))/2
    for i in range(len(sample_lst)-1):
        if sample_lst[i] < thrshold and sample_lst[i+1] >= thrshold: #Rising edge
            lst.append(i+1)
    return lst

def ppi(peak_lst):
    ppi_lst = []
    for i in range(len(peak_lst)-1):
        ppi = (peak_lst[i+1]-peak_lst[i])*4
        if ppi > 300 and ppi < 2000:
            ppi_lst.append(ppi)
    return ppi_lst

def MeanPPI(ppi_list):
    rr_sum = 0
    for i in range(len(ppi_list)):
        rr_sum = rr_sum + ppi_list[i]
    meanPPI = rr_sum/len(ppi_list)
    return round(meanPPI)

def meanHR(mean_ppi):
    mean_hr = 60000/mean_ppi
    return round(mean_hr)

def SDNN(ppi_list, mean_ppi):
    rrdiff_sum = 0
    for i in range(len(ppi_list)):
        rrdiff_sum = rrdiff_sum + (ppi_list[i] - mean_ppi)**2
    sdnn = math.sqrt(rrdiff_sum/(len(ppi_list)-1))
    return round(sdnn)

def RMSSD(ppi_list):
    rr_diff = 0
    for i in range(len(ppi_list) -1):
        rr_diff = rr_diff + (ppi_list[i+1]-ppi_list[i])**2
    rmssd = math.sqrt(rr_diff/(len(ppi_list)-1))
    return round(rmssd)

def wifi_try_connect(ssid, password, max_wait):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    display.text("connecting...", 0, 0, 1)
    display.show()
    while max_wait and not wlan.isconnected():
        max_wait -= 1
        time.sleep(1)
    if wlan.isconnected():
        display.fill(0)
        display.text('Wifi Connected!', 0, 0, 1)
        status = wlan.ifconfig()
        display.text(f'IP: {status[0]}', 0, 10, 1)
    else:
        raise RuntimeError('!!Wifi Connection Failed!!!')
        display.text(RuntimeError, 0, 0, 1)
    display.show()

def HR():
    global switch
    time.sleep(.5)
    switch = False
    display.fill(0)
    display.text('Please Wait...', 0, 20, 1)
    display.show()
    ppi_lst = []
    norm_ppi_lst = []
    while (not switch):
        if not samples.empty():
            sample_lst = Sample_lst()
            peak_lst = Peak_lst(sample_lst)
            for i in ppi(peak_lst):
                ppi_lst.append(i)
            print(ppi_lst)
            if len(ppi_lst) > 10:
                peak_avg = Avg(ppi_lst)
                norm_ppi_lst = []
                for i in ppi_lst:
                    if i > (peak_avg-100) and i < (peak_avg+100):
                        norm_ppi_lst.append(i)
            if len(norm_ppi_lst)>= 10:
                ppi_norm = Avg(norm_ppi_lst)
                hr = 60000/ppi_norm
                display.fill(0)
                display.text('Heart Rate', 25, 0, 1)
                display.text(f'{round(hr)}',55 , 15, 1)
                display.text('BPM', 50 , 30, 1)
                display.text('>>Main Menu<<', 10, 40, 1)
                display.text('>>Press again<<', 0, 50, 1)
                display.show()
                ppi_lst.clear()
                norm_ppi_lst.clear()
                peak_lst.clear()
                sample_lst.clear()
    time.sleep(.5)            
    switch = False
    
def basic_analysis():
    global switch
    time.sleep(.5)
    display.fill(0)
    display.text('Please Wait...', 0, 20, 1)
    display.show()
    switch = False
    ppi_lst=[]
    norm_ppi_lst =[]
    while (not switch):
        if not samples.empty():
            sample_lst = Sample_lst()
            peak_lst = Peak_lst(sample_lst)
            for i in ppi(peak_lst):
                ppi_lst.append(i)
            if len(ppi_lst) > 20:
                peak_avg = Avg(ppi_lst)
                norm_ppi_lst = []
                for i in ppi_lst:
                    if i > (peak_avg-100) and i < (peak_avg+100):
                        norm_ppi_lst.append(i)
                display.fill(0)
                mean_ppi = MeanPPI(norm_ppi_lst)
                mean_hr = meanHR(mean_ppi)
                sdnn = SDNN(norm_ppi_lst, mean_ppi)
                rmssd = RMSSD(norm_ppi_lst)
                display.text(f'Mean PPI: {mean_ppi} ms', 0, 0, 1)
                display.text(f'Heart rate: {mean_hr}', 0 ,10 ,1)
                display.text(f'SDNN: {sdnn} ms', 0, 20, 1)
                display.text(f'RMSSD: {rmssd} ms', 0, 30, 1)
                display.text('>>Main Menu<<', 10, 40, 1)
                display.text('>>Press again<<', 0, 50, 1)
                display.show()
                ppi_lst.clear()
                norm_ppi_lst.clear()
                peak_lst.clear()
    time.sleep(.5)
    switch = False
    
def Kubios_HRV():
    global switch
    time.sleep(.5)
    switch = False
    display.fill(0)
    display.text('Please Wait...', 0, 20, 1)
    display.show()
    ppi_lst = []
    counter = 0
    
    while not switch:
        if not samples.empty():
            sample_lst = Sample_lst()
            peak_lst = Peak_lst(sample_lst)
            for i in ppi(peak_lst):
                ppi_lst.append(i)
            if len(ppi_lst) > 20:
                if counter < 1:
                    counter += 1                
                    APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
                    CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
                    CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"

                    LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
                    TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
                    REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"

                    response = requests.post(
                        url = TOKEN_URL,
                        data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
                        headers = {'Content-Type':'application/x-www-form-urlencoded'},
                        auth = (CLIENT_ID, CLIENT_SECRET))

                    response = response.json() #Parse JSON response into a python dictionary
                    access_token = response["access_token"] #Parse access token out of the response dictionary
                    data_set = {"type": "RRI",
                                "data": ppi_lst,
                                "analysis": {"type": "readiness"}}
                    response = requests.post(
                        url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
                        headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your KubiosCloud analysis session
                                    "X-Api-Key": APIKEY },
                        json = data_set) #dataset will be automatically converted to JSON by the urequests library
                    Kubios_result = response.json()

                    
                    display.fill(0)
                    display.text("Kubios Analysis", 0, 0, 1)
                    display.text('SNS value:', 0, 10, 1)
                    display.text(f'{Kubios_result['analysis']['pns_index']}', 5, 20, 1)
                    display.text(f'PNS value:', 0, 30, 1)
                    display.text(f'{Kubios_result['analysis']['sns_index']}', 5, 40, 1)
                    display.show()
                    ppi_lst.clear()
    time.sleep(.5)
    switch = False
    

def menu(pointr_size):
    menu_lst = ['Heart Rate', 'HR analysis', 'Kubios HRV ']
    for i in range(len(menu_lst)):
        display.text(menu_lst[i], pointr_size, (pointr_size+5)*i, 1)
    display.show()


def display_pointr(pointr):
    display.fill_rect(0, 0, pointr_size, 64, 0)
    y_decrement = pointr_size
    for i in range(pointr_size):
        arrow_increment = (pointr_size+2) * pointr 
        y_axisincrement = arrow_increment + i
        for n in range(y_decrement):
            display.pixel(i, y_axisincrement, 1)
            y_axisincrement += 1
        y_decrement -= 2
    display.show()

def rot_button(tid):
    global switch
    switch = True

def rotary_change():
    global rota_state
    global rotb_state
    global rota_laststate
    global value
    rota_state = rot_a.value()
    rotb_state = rot_b.value()
    if rota_state != rota_laststate:
        if rotb_state != rota_state:
            value = (value+1)%pointr_num
        else:
            value = (value-1)%pointr_num
    rota_laststate = rota_state

rot_a = Pin(10, Pin.IN, Pin.PULL_DOWN)
rot_b = Pin(11, Pin.IN, Pin.PULL_DOWN)
rot_sw = Pin(12, Pin.IN, Pin.PULL_UP)
rot_sw.irq(handler = rot_button, trigger=Pin.IRQ_FALLING)
rota_state = rot_a.value()
value = 0
rota_laststate = rot_a.value()
switch = 0
pointr_size = 14
pointr_num = 3

### Enter wifi details ###
ssid = ""
password = ""

value = 0
samples = isr_fifo(750, 26)# create the improved fifo : size = 750, adc pin = pin_nr
tmr = Piotimer(mode= Piotimer.PERIODIC, period = 4, callback = samples.handler)
i2c = I2C(id = 1, sda = Pin(14), scl = Pin(15))
display = ssd1306.SSD1306_I2C(128, 64 , i2c)



### Main program ###

# wifi_try_connect(ssid, password, 10) #<<< Uncomment when wifi details are entered
display.fill(0)
while True:    
    menu(pointr_size)
    rotary_change()
    display_pointr(value)
    if switch:
        if value == 0:
            HR()
            display.fill(0)
        if value == 1:
            basic_analysis()
            display.fill(0)
        if value == 2:
            Kubios_HRV()
            display.fill(0)
