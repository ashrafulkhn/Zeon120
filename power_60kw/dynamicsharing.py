#import configparser
import time

from power_60kw.factory_reader import FactoryReader
#from caninterface import CanInterface
from power_60kw.persistent_communication import set_status_update

"""
  can1  60B   [6]  00 00 00 00 00 00
  can1  500   [4]  00 00 20 00
  can1  60D   [7]  00 00 00 00 00 00 00
  can1  60E   [8]  00 00 00 00 00 00 00 00
  can1  30A   [4]  00 00 00 00
  can1  500   [4]  00 02 00 02
  can1  500   [4]  00 00 10 00
  can1  305   [4]  00 00 FA 00
  can1  605   [4]  00 00 FA 00
  can1  304   [8]  DC 05 10 27 D0 07 00 00
  can1  604   [8]  DC 05 10 27 D0 07 00 00
  can1  302   [7]  00 00 00 00 00 00 00
  can1  602   [7]  00 00 00 00 00 00 00
  can1  303   [7]  00 00 00 00 00 00 00
  can1  603   [7]  00 00 00 00 00 00 00
  can1  502   [1]  C1

  [00, 00, 00, 00, 00, 00, 00]
"""

class MaxEVvalues2Input:
    def __init__(self):
        self.arbitration_id = 1547
        self.data = [239, 1, 240, 0, 118, 0]

class MaxEVvalues1Input:
    def __init__(self):
        self.arbitration_id = 779
        self.data = [239, 1, 240, 0, 118, 0]

# class ResetGunModule2Input:
#     def __init__(self):
#         self.arbitration_id = 1542
#         self.data = []

# class ResetGunModule1Input:
#     def __init__(self):
#         self.arbitration_id = 774
#         self.data = []

class Vehicle2StatusReaderInput:
    def __init__(self):
        self.arbitration_id = 1537
        self.data = [0, 224, 16, 64, 5, 0, 0, 0]

class Vehicle1StatusReaderInput:
    def __init__(self):
        self.arbitration_id = 769
        self.data = [29, 224, 16, 64, 5, 0, 0, 0]



class PMSetDataCurrentPeccStatus2Input:
    def __init__(self):
        self.arbitration_id = 35693618
        self.data = [0, 48, 0, 0, 0, 160, 9, 1]


class PMSetDataCurrentPeccStatus1Input:
    def __init__(self):
        self.arbitration_id = 35677237
        self.data = [0, 48, 0, 0, 0, 160, 9, 1]


class DigitalInputReaderInput:
    def __init__(self):
        self.arbitration_id = 1282
        self.data = [44]

input_values = [DigitalInputReaderInput(), PMSetDataCurrentPeccStatus1Input(), PMSetDataCurrentPeccStatus2Input(),
                 Vehicle1StatusReaderInput(),
                Vehicle2StatusReaderInput(), MaxEVvalues2Input(), MaxEVvalues1Input()]   
  
def readAllCanData(d):
    reader = FactoryReader.create_reader(d.arbitration_id,d.data)
    if reader:
        reader.read_input_data()


def readFromCan():
    end_time = time.time() + 30
    start = 0
    end_idx = len(input_values)
    while time.time()<end_time:
    # bus = CanInterface.bus_instance
    # for m in bus:
        m = input_values[start]
        print(m)
        readAllCanData(m)
        start+=1
        if start==end_idx:
            start=0


def perform_action():
    set_status_update()
    readFromCan()