#!/usr/bin/env python

import usbtmc
import argparse
from time import sleep

#command line arguments
parser = argparse.ArgumentParser(description='Program a Keithley 2220-30-1 DC power supply')
parser.add_argument('-v1','--voltage1',help='Voltage setting for channel 1 in volts',default="none", required=False)
parser.add_argument('-v2','--voltage2',help='Voltage setting for channel 2 in volts',default="none", required=False)
parser.add_argument('-c1','--current1',help='Current setting for channel 1 in mA',default="none", required=False)
parser.add_argument('-c2','--current2',help='Current setting for channel 2 in mA',default="none", required=False)
parser.add_argument('-s','--status',help='Display voltage and current settings',action='store_true', required=False)
parser.add_argument('-o','--output',help='Enable/disable output',default="keep", required=False, choices=['off', 'on', 'keep'])
parser.add_argument('-m', '--macro',help='A SCPI macro file', default="none", required=False)
parser.add_argument('-l', '--line', help="A single command to send to the device", default="", required=False)
parser.add_argument('-u', '--usb', help="USB vendor and product IDs", nargs=2, default=['05e6','2220'], required=False, metavar=("VENDOR_ID", "PRODUCT_ID"))

args = parser.parse_args()

#open connection to device                       
inst = usbtmc.Instrument(int(args.usb[0], 16), int(args.usb[1], 16))

#querty device's identity
print(inst.ask("*IDN?"))

#status check
def Status():
    voltStatus =    inst.ask("MEAS:VOLT:DC? ALL")     #voltage on all channels
    currentStatus = inst.ask("MEAS:CURRENT:DC? ALL")  #current on all channels
    powerStatus = inst.ask("MEAS:POW? ALL")           #power on all channels
    outputStatus = inst.ask("OUTPUT?")                #is output enabled
    
    inst.close()
    
    v = voltStatus.split(",")
    c = currentStatus.split(",")
    p = powerStatus.split(",")

    #print status message
    print("Device status:")
    for i in range(0,2):
        print("Channel "+str(i+1)+":")
        print("    Voltage = "+v[i]+"V")
        print("    Current = "+c[i]+"A")
        print("    Power   = "+p[i]+"W")
        print("")

    if outputStatus == "1":
        print("Output is on")
    else:
        print("Output is off")

    print("")
    
        

if args.status:
    Status()
    exit()


#start remote control
inst.write("SYSTEM:REMOTE")

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

#check if a string is a number below 1500mA (device max current)
def checkA(s):
    try:
        float(s)
        if float(s) > 1500:
            print("Current must be less than 1.5A")
            return False
        return True
    except ValueError:
        return False



#read in a macro then quit
if not args.macro == "none":
    print("Macro specified")
    for line in open(args.macro):
        sleep(0.1)
        #ignore commented lines
        if line[0] == '#':
            continue;
        writeString = line.split("#")[0].strip()
        print(writeString)

        #if the command has a '?' get the response
        if "?" in writeString:
            sleep(0.5)
            print("   "+inst.ask(writeString))
        else:
            inst.write(writeString)

    inst.write("SYSTem:LOCal")
    inst.close()
    exit()

#send a single SCPI command
if args.line !="":
    inst.write(args.line)
    print(args.line)
    
    
#set voltage on channel 1
if checkV(args.voltage1):
    inst.write("OUTPut 1")
    inst.write("INST:NSEL 1")
    inst.write("VOLT "+args.voltage1)

#set voltage on channel 2
if checkV(args.voltage2):
    inst.write("OUTPut 1")
    inst.write("INST:NSEL 2")
    inst.write("VOLT "+args.voltage2)

#set current on channel 1
if checkA(args.current1):
    inst.write("OUTPut 1")
    inst.write("INST:NSEL 1")
    inst.write("CURRENT "+args.current1+"mA")

#set current on channel 2
if checkA(args.current2):
    inst.write("OUTPut 1")
    inst.write("INST:NSEL 2")
    inst.write("CURRENT "+args.current1+"mA")

#toggle output
if args.output.lower() == "on":
    inst.write("OUTPut 1")
elif args.output.lower() == "off":
    inst.write("OUTPut 0")

#display status
Status()

#return to local control, then disconnect from device
inst.write("SYSTem:LOCal")
inst.close()
