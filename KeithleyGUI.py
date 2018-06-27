


import usbtmc
import argparse
import time
from time import sleep
import numpy as np


import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button

parser = argparse.ArgumentParser(description='Program a Keithley 2220-30-1 DC power supply')
parser.add_argument('-u', '--usb', help="USB vendor and product IDs", nargs=2, default=['05e6','2220'], required=False, metavar=("VENDOR_ID", "PRODUCT_ID"))


args = parser.parse_args()

#open connection to device
try:
    inst = usbtmc.Instrument(int(args.usb[0], 16), int(args.usb[1], 16))
except usbtmc.usbtmc.UsbtmcException:
    print("Unable to connect to device.")
    exit()
    

#querty device's identity
print(inst.ask("*IDN?"))

#start remote control
inst.write("SYSTEM:REMOTE")   

measureing=False

def getSettings():
    vSetting = []
    cSetting=[]
    
    for i in range(0,2):
        inst.write("INST:SEL CH"+str(i+1))
        vSetting.append(inst.ask("VOLT?"))   #voltage setting
        cSetting.append(inst.ask("CURR?"))   #current setting

    return vSetting, cSetting


def getMeasurements():
    measureing=True
    voltStatus =    inst.ask("MEAS:VOLT:DC? ALL")     #voltage on all channels
    currentStatus = inst.ask("MEAS:CURRENT:DC? ALL")  #current on all channels
    
    v = voltStatus.split(",")
    c = currentStatus.split(",")
    measuring=False
    
    return v,c

def isOutput():
    outputStatus = inst.ask("OUTPUT?") 
    if outputStatus == "1":
        return True
    else:
        return False

#check if a string is a number below 30V (device max voltage)
def checkV(s):
    try:
        float(s)
        if float(s) > 30:
            print("Voltage must be less than 30V")
            return False
        return True
    except ValueError:
        return False  

initialSettings = getSettings()


def updateMeasurements(event=0):
    inst.write("*OPC")
    measurements = getMeasurements()
    V1.set_text(measurements[0][0].ljust(5, '0')+"\n"+measurements[1][0].ljust(5, '0'))
    V2.set_text(measurements[0][1].ljust(5, '0')+"\n"+measurements[1][1].ljust(5, '0'))

    plt.draw()


def submitChannel1V(text):
    if checkV(text):
        #inst.write("OUTPut 1")
        inst.write("INST:NSEL 1")
        inst.write("VOLT "+text)
        updateMeasurements()
        

def submitChannel2V(text):
    if checkV(text):
        #inst.write("OUTPut 1")
        inst.write("INST:NSEL 2")
        inst.write("VOLT "+text)
        updateMeasurements()

def submitChannel1C(text):
    if checkV(text):
        #inst.write("OUTPut 1")
        inst.write("INST:NSEL 1")
        inst.write("CURRENT "+text)
        updateMeasurements()


def submitChannel2C(text):
    if checkV(text):
        #inst.write("OUTPut 1")
        inst.write("INST:NSEL 2")
        inst.write("CURRENT "+text)
        updateMeasurements()
        

def enableToggle(event):
    outputOn=isOutput()
    buttonString=""
    if outputOn:
        inst.write("OUTPut 0")
        buttonString="Output disabled"
    else:
        inst.write("OUTPut 1")
        buttonString="Output enabled"
    bEnable.label.set_text(buttonString)
    updateMeasurements()



fig = plt.figure(figsize=(4,2))
fig.canvas.set_window_title('Keithley 2220-30-1 Control')
        
axboxCH1V = plt.axes([0.2, 0.23, 0.38, 0.1])
text_boxCH1V = TextBox(axboxCH1V, 'Voltage', initial=initialSettings[0][0])
text_boxCH1V.on_submit(submitChannel1V)

axboxCH2V = plt.axes([0.6, 0.23, 0.38, 0.1])
text_boxCH2V = TextBox(axboxCH2V, '', initial=initialSettings[0][1])
text_boxCH2V.on_submit(submitChannel2V)

axboxCH1C = plt.axes([0.2, 0.12, 0.38, 0.1])
text_boxCH1C = TextBox(axboxCH1C, 'Current', initial=initialSettings[1][0])
text_boxCH1C.on_submit(submitChannel1C)

axboxCH2C = plt.axes([0.6, 0.12, 0.38, 0.1])
text_boxCH2C = TextBox(axboxCH2C, '', initial=initialSettings[1][1])
text_boxCH2C.on_submit(submitChannel2C)

initialState = isOutput()
initialString = "Output disabled"
if initialState:
    initialString="Output enabled"



axboxEnable = plt.axes([0.31, 0.01, 0.38, 0.1])
bEnable=Button(axboxEnable, initialString)
bEnable.on_clicked(enableToggle)


axboxMeasure = plt.axes([0.31, 0.9, 0.38, 0.1])
bMeasure=Button(axboxMeasure, "Measure")
bMeasure.on_clicked(updateMeasurements)


initialMeasures = getMeasurements()

V1 = plt.text(0.1, -3.5, initialMeasures[0][0].ljust(5, '0')+"\n"+initialMeasures[1][0].ljust(5, '0'), ha="center", size=12,
              bbox=dict(boxstyle="round",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))
V2 = plt.text( 0.9, -3.5, initialMeasures[0][1].ljust(5, '0')+"\n"+initialMeasures[1][1].ljust(5, '0'), ha="center", size=12,
              bbox=dict(boxstyle="round",
                   ec=(1., 0.5, 0.5),
                   fc=(1., 0.8, 0.8),
                   ))
plt.text( -0.55, -3.5, "Voltage\nCurrent", ha="center", size=12)

plt.text(0.1,-1.5, "Channel 1", ha="center", size=12)
plt.text(0.9,-1.5, "Channel 2", ha="center", size=12)


plt.text(0,-5.6, "Channel 1", ha="center", size=12)
plt.text(1.05,-5.6, "Channel 2", ha="center", size=12)

plt.show()
    
inst.write("SYSTem:LOCal")
inst.close()
    


