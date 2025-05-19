import logging
import time
import random

from constants import CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm, Module2Message as mm2
from utility import bytetobinary, binaryToDecimal, DTH
from config_reader import ConfigManager
from power_120kw.persistent_communication import SetInterval
from caninterface import CanInterface


global_data = ConstantManager120KW()
#================================================================================
#=================== MQTT =======================================================
#================================================================================
import paho.mqtt.client as mqtt
# import signal
total_power = ConfigManager().get_total_power()
ConfigManager().set_power(total_power)

current = None
voltage = None
isStartButton1Pressed = False
isStartButton2Pressed = False
readCurrent = None
readVolatge = None
power1 = 0
power2 = 0
# This part of the static values has to be captured from config.ini file.
# TODO
hostIp = "192.168.3.120"
hostPort = 1883

# The callback function to be called when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("MAN_COMMAND_1")
    client.subscribe("MAN_COMMAND_2")

# The callback function to be called when a message is received.
def on_message(client, userdata, msg):
    global isStartButton1Pressed
    global isStartButton2Pressed
    global current
    global voltage
    data = msg.payload.decode()
    data = data.split(":")
    print(data[0])

    # payload = data[0]
    #current = int(data[1])
    #voltage = int(data[2])
    # START1:450:20
    #STOP1::
    if msg.topic == "MAN_COMMAND_1":
        if data[0] == "START1":
            start(int(data[2]), int(data[1]))
            current = int(data[2])
            voltage = int(data[1])
            isStartButton1Pressed = True
            isStartButton2Pressed = False
        elif data[0] == "STOP1":
            isStartButton1Pressed = False
            isStartButton2Pressed = False
            stop()
    
    if msg.topic == "MAN_COMMAND_2":
        if data[0] == "START2":
            start2(int(data[2]), int(data[1]))
            current = int(data[2])
            voltage = int(data[1])
            isStartButton2Pressed = True
            isStartButton1Pressed = False
        elif data[0] == "STOP2":
            isStartButton2Pressed = False
            isStartButton1Pressed = False
            stop()
# Function to start sensor
def start(current, setVoltage):
    print("Charging started... GUN1")
    global isStartButton1Pressed
    global power1
    #When Start button is pressed, below code and while loop should run.
    Running_current = int(current)
    power1 = int(current * setVoltage)
    mm.digital_output_close_AC()
    if 0 < power1 <= 30000:
        mm1.digital_output_close_Gun11()
    elif 30000 < power1 <= 60000:
        mm1.digital_output_close_Gun12()
    elif 60000 < power1 <= 90000:
        mm1.digital_output_close_Gun13()
    elif power1 > 90000:
        mm1.digital_output_close_Gun14()
    
    # print(f"Charging started for current = {Running_current}A and voltage = {setVoltage}")
    return Running_current, setVoltage

def start2(current, setVoltage):
    print("Charging started... GUN2")
    global isStartButton2Pressed
    global power2
    Running_current = int(current)
    power2 = int(current * setVoltage)
    mm.digital_output_close_AC()
    if 0 < power2 <= 30000:
        mm2.digital_output_close_Gun21()
    elif 30000 < power2 <= 60000:
        mm2.digital_output_close_Gun22()
    elif 60000 < power2 <= 90000:
        mm2.digital_output_close_Gun23()
    elif power2 > 90000:
        mm2.digital_output_close_Gun24()
        
    # print(f"Charging started for current = {Running_current}A and voltage = {setVoltage}")
    return Running_current, setVoltage

# Function to stop sensor
def stop():
    print("Charging Stopped1...")
        # When Stop button is pressed, below code should run.
    mm1.digital_output_led_red1()
    mm2.digital_output_led_red2()
    mm.stopModule(CanId.CAN_ID_1)
    mm.stopModule(CanId.CAN_ID_2)
    mm.stopModule(CanId.CAN_ID_3)
    mm.stopModule(CanId.CAN_ID_4)
    mm.readModule_Voltage(CanId.CAN_ID_1)
    mm.readModule_Voltage(CanId.CAN_ID_2)
    mm.readModule_Voltage(CanId.CAN_ID_3)
    mm.readModule_Voltage(CanId.CAN_ID_4)
    mm.readModule_Current(CanId.CAN_ID_1)
    mm.readModule_Current(CanId.CAN_ID_2)
    mm.readModule_Current(CanId.CAN_ID_3)
    mm.readModule_Current(CanId.CAN_ID_4)
    mm.digital_output_open_stop()
    time.sleep(5)
    mm.digital_output_open_fan()
    mm.digital_output_open_AC()
# # Function to set current
# def setCurrent(current):
#     # Code to set current
#     pass

# Create an MQTT client instance
client = mqtt.Client("UFC_1234")
# Set the callback functions
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("UFC","ufc123")
# Connect to the MQTT broker
client.connect(hostIp, hostPort,60)
print("Device connected")
# To be added if some sensor operations required. Do not forget to call this method on your required places.
# def sensor_work():
#     print("Sensor work Started.")

# Start a new thread to handle network traffic
client.loop_start()

#=================================================================================
#==========================  CAN FUNCTIONS =======================================
#=================================================================================

#SetVoltage = 400  # Variable to enter voltage value
#Setcurrent=50    # Variable to enter the current value
#Running_current= 0

def start_Modules(icurrent, isetVoltage):
    #print("SetCurrent1 -> ", icurrent1)
    #print("SetVoltage1 -> ", isetVoltage1)
    power1 = int(icurrent * isetVoltage)
    mm1.digital_output_led_red1()
    mm2.digital_output_led_red2()
    time.sleep(2)
    if 0 < power1 <= 30000:
        mm.stopModule(CanId.CAN_ID_2)
        mm.stopModule(CanId.CAN_ID_3)
        mm.stopModule(CanId.CAN_ID_4)
        #mm1.digital_output_close_Gun11()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_1)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_1)

        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_1)
        global_data.set_data_running_current(int(icurrent))
        mm.setCurrent(CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_1)
        mm.readModule_Voltage(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
        
    elif 30000 < power1 <= 60000:
        mm.stopModule(CanId.CAN_ID_2)
        mm.stopModule(CanId.CAN_ID_4)
        #mm1.digital_output_close_Gun12()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_1)
            mm.lowMode(CanId.CAN_ID_3)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_1)
            mm.highMode(CanId.CAN_ID_3)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_1)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_3)
        global_data.set_data_running_current(int(icurrent/2))
        mm.setCurrent(CanId.CAN_ID_1)
        mm.setCurrent(CanId.CAN_ID_3)
        mm.startModule(CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_3)
        mm.readModule_Voltage(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
    
    elif 60000 < power1 <= 90000:
        
        mm.stopModule(CanId.CAN_ID_2)
        #mm1.digital_output_close_Gun13()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_1)
            mm.lowMode(CanId.CAN_ID_3)
            mm.lowMode(CanId.CAN_ID_4)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_1)
            mm.highMode(CanId.CAN_ID_3)
            mm.highMode(CanId.CAN_ID_4)
    
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_1)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_3)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_4)
        global_data.set_data_running_current(int(icurrent/3))
        mm.setCurrent(CanId.CAN_ID_1)
        mm.setCurrent(CanId.CAN_ID_3)
        mm.setCurrent(CanId.CAN_ID_4)
        mm.startModule(CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_3)
        mm.startModule(CanId.CAN_ID_4)
        mm.readModule_Voltage(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
    
    elif power1 > 90000:
        #mm1.digital_output_close_Gun14()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_1)
            mm.lowMode(CanId.CAN_ID_2)
            mm.lowMode(CanId.CAN_ID_3)
            mm.lowMode(CanId.CAN_ID_4)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_1)
            mm.highMode(CanId.CAN_ID_2)
            mm.highMode(CanId.CAN_ID_3)
            mm.highMode(CanId.CAN_ID_4)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_1)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_2)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_3)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_4)
        global_data.set_data_running_current(int(icurrent/4))
        mm.setCurrent(CanId.CAN_ID_1)
        mm.setCurrent(CanId.CAN_ID_2)
        mm.setCurrent(CanId.CAN_ID_3)
        mm.setCurrent(CanId.CAN_ID_4)
        mm.startModule(CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_2)
        mm.startModule(CanId.CAN_ID_3)
        mm.startModule(CanId.CAN_ID_4)
        mm.readModule_Voltage(CanId.CAN_ID_1)
        mm.readModule_Voltage(CanId.CAN_ID_2)
        mm.readModule_Voltage(CanId.CAN_ID_3)
        mm.readModule_Voltage(CanId.CAN_ID_4)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)

# def stop_charge():
#     pass

def start_Modules2(icurrent, isetVoltage):
    #print("SetCurrent1 -> ", icurrent1)
    #print("SetVoltage1 -> ", isetVoltage1)
    power2 = int(icurrent * isetVoltage)
    mm1.digital_output_led_red1()
    mm2.digital_output_led_red2()
    time.sleep(2)
    if 0 < power2 <= 30000:
        mm.stopModule(CanId.CAN_ID_1)
        mm.stopModule(CanId.CAN_ID_3)
        mm.stopModule(CanId.CAN_ID_4)
        #mm2.digital_output_close_Gun21()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_2)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_2)

        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_2)
        global_data.set_data_running_current(int(icurrent))
        mm.setCurrent(CanId.CAN_ID_2)
        mm.startModule(CanId.CAN_ID_2)
        mm.readModule_Voltage(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
        
    elif 30000 < power2 <= 60000:
        mm.stopModule(CanId.CAN_ID_1)
        mm.stopModule(CanId.CAN_ID_3)
        #mm2.digital_output_close_Gun22()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_2)
            mm.lowMode(CanId.CAN_ID_4)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_2)
            mm.highMode(CanId.CAN_ID_4)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_2)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_4)
        global_data.set_data_running_current(int(icurrent/2))
        mm.setCurrent(CanId.CAN_ID_2)
        mm.setCurrent(CanId.CAN_ID_4)
        mm.startModule(CanId.CAN_ID_2)
        mm.startModule(CanId.CAN_ID_4)
        mm.readModule_Voltage(CanId.CAN_ID_2)
        mm.readModule_Voltage(CanId.CAN_ID_4)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
    
    elif 60000 < power2 <= 90000:
        
        mm.stopModule(CanId.CAN_ID_1)
        #mm2.digital_output_close_Gun23()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_2)
            mm.lowMode(CanId.CAN_ID_3)
            mm.lowMode(CanId.CAN_ID_4)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_2)
            mm.highMode(CanId.CAN_ID_3)
            mm.highMode(CanId.CAN_ID_4)
    
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_2)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_3)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_4)
        global_data.set_data_running_current(int(icurrent/3))
        mm.setCurrent(CanId.CAN_ID_2)
        mm.setCurrent(CanId.CAN_ID_3)
        mm.setCurrent(CanId.CAN_ID_4)
        mm.startModule(CanId.CAN_ID_2)
        mm.startModule(CanId.CAN_ID_3)
        mm.startModule(CanId.CAN_ID_4)
        mm.readModule_Voltage(CanId.CAN_ID_2)
        mm.readModule_Voltage(CanId.CAN_ID_3)
        mm.readModule_Voltage(CanId.CAN_ID_4)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)
    
    elif power2 > 90000:
        #mm2.digital_output_close_Gun24()
        if isetVoltage <= 500 :
            mm.lowMode(CanId.CAN_ID_1)
            mm.lowMode(CanId.CAN_ID_2)
            mm.lowMode(CanId.CAN_ID_3)
            mm.lowMode(CanId.CAN_ID_4)

        elif isetVoltage >500 :
            mm.highMode(CanId.CAN_ID_1)
            mm.highMode(CanId.CAN_ID_2)
            mm.highMode(CanId.CAN_ID_3)
            mm.highMode(CanId.CAN_ID_4)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_1)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_2)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_3)
        mm.setVoltage(DTH.convertohex(int(isetVoltage)), CanId.CAN_ID_4)
        global_data.set_data_running_current(int(icurrent/4))
        mm.setCurrent(CanId.CAN_ID_1)
        mm.setCurrent(CanId.CAN_ID_2)
        mm.setCurrent(CanId.CAN_ID_3)
        mm.setCurrent(CanId.CAN_ID_4)
        mm.startModule(CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_2)
        mm.startModule(CanId.CAN_ID_3)
        mm.startModule(CanId.CAN_ID_4)
        mm.readModule_Voltage(CanId.CAN_ID_1)
        mm.readModule_Voltage(CanId.CAN_ID_2)
        mm.readModule_Voltage(CanId.CAN_ID_3)
        mm.readModule_Voltage(CanId.CAN_ID_4)
        mm.readModule_Current(CanId.CAN_ID_1)
        mm.readModule_Current(CanId.CAN_ID_2)
        mm.readModule_Current(CanId.CAN_ID_3)
        mm.readModule_Current(CanId.CAN_ID_4)

def readAllCanData(d):
    global readCurrent
    global readVolatge
    global divide_vol
    global tot_current

    # print("Inside readAllCanData")
    try:
        #print("Trying to read data from Can IDs")
     
        if d.arbitration_id == int(ConfigManager().get_power_config('PS1_id')):
            #print("reading PS1")
            b1 = bytetobinary(d.data)
            diff_vol_current = binaryToDecimal(int(b1[1]))
    
            if diff_vol_current == 98:
                volatge_pe1 = binaryToDecimal(int(b1[4] + b1[5] + b1[6] + b1[7]))
                divide_vol = int(volatge_pe1)/1000
                readVolatge = int(divide_vol)

            if diff_vol_current == 48:
                global_data.set_data_current_pe1(binaryToDecimal(int(b1[4] + b1[5] + b1[6] + b1[7])))
                    
        
        if d.arbitration_id == int(ConfigManager().get_power_config('PS2_id')):
        # arbitration id for PS2
            b2 = bytetobinary(d.data)
            diff_vol_current = binaryToDecimal(int(b2[1]))
            if diff_vol_current == 98:
                volatge_pe2 = binaryToDecimal(int(b2[4] + b2[5] + b2[6] + b2[7]))
                divide_vol = int(volatge_pe2)/1000
                readVolatge = int(divide_vol)
            if diff_vol_current == 48:
                global_data.set_data_current_pe2(binaryToDecimal(int(b2[4] + b2[5] + b2[6] + b2[7])))
            
       
        if d.arbitration_id == int(ConfigManager().get_power_config('PS3_id')):
            
            b3 = bytetobinary(d.data)
            diff_vol_current = binaryToDecimal(int(b3[1]))
            if diff_vol_current == 98:
                volatge_pe3 = binaryToDecimal(int(b3[4] + b3[5] + b3[6] + b3[7]))
                divide_vol = int(volatge_pe3)/1000
                readVolatge = int(divide_vol)
            if diff_vol_current == 48:
                global_data.set_data_current_pe3(binaryToDecimal(int(b3[4] + b3[5] + b3[6] + b3[7]))) 

        
        if d.arbitration_id == int(ConfigManager().get_power_config('PS4_id')) :
           # print("reading PS4",d.arbitration_id)
            b4 = bytetobinary(d.data)
            diff_vol_current = binaryToDecimal(int(b4[1]))
 
            if diff_vol_current == 98:
                volatge_pe4 = binaryToDecimal(int(b4[4] + b4[5] + b4[6] + b4[7]))
                divide_vol = int(volatge_pe4)/1000
                
                readVolatge = int(divide_vol)
            if diff_vol_current == 48:
                c_pe4 = binaryToDecimal(int(b4[4] + b4[5] + b4[6] + b4[7]))
                current_pe4 = int(int(c_pe4)/1000)
                tc1 = int(global_data.get_data_current_pe1())/1000
                tc2 = int(global_data.get_data_current_pe2())/1000
                tc3 = int(global_data.get_data_current_pe3())/1000
                tot_current = int(current_pe4+tc3+tc2+tc1)
                readCurrent = tot_current
        
                
                # print(f"TOTAL CUERRNET = ' {tot_current1}A ,  Volatge = {divide_vol}V") #Current Values

        # # return tot_current1, int(divide_vol)
        readCurrent = readCurrent
        readVolatge = readVolatge
        

        # readCurrent = tot_current1
        # readVolatge = int(divide_vol)
    except:
        print("There was some error in reading the voltage and current values.")
       # print("Sending random values to MQTT topics.")

def readFromCan():
    global readCurrent
    global readVolatge

    
    print("Thread Started.")
    # while True:
   # readModule_Voltage_1()
   # readModule_Current_1()
   # readModule_Current_2()
    bus = CanInterface.bus_instance
    for m in bus:
        readAllCanData(m)

readdata = SetInterval(0.25,readFromCan)

# Run the main loop
while True:
    # Do other stuff here
    if isStartButton1Pressed == True:
        #print("Current1 : ", readCurrent1)
        #print("voltage1: ", readVolatge1 )

        client.publish("VOLTAGE_2ND_1", str(readVolatge))
        client.publish("CURRENT_2ND_1", str(readCurrent))
        # current, setVoltage = start()
        start_Modules(current, voltage)
    if isStartButton2Pressed == True:
        #print("Current 2: ", readCurrent2)
        #print("voltage 2: ", readVolatge2 )

        client.publish("VOLTAGE_2ND_2", str(readVolatge))
        client.publish("CURRENT_2ND_2", str(readCurrent))
        # current, setVoltage = start()
        start_Modules2(current, voltage)


# Stop the network thread and disconnect
client.loop_stop()
client.disconnect()
