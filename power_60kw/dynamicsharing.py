# import the library
import configparser
import time

from power_60kw.factory_reader import FactoryReader
from caninterface import CanInterface
from power_60kw.persistent_communication import set_status_update


def readAllCanData(d):
    reader = FactoryReader.create_reader(d.arbitration_id,d.data)
    if reader:
        reader.read_input_data()


def readFromCan():
    bus = CanInterface.bus_instance
    for m in bus:
        readAllCanData(m)


def perform_action():
    #time.sleep(40)
    set_status_update()
    readFromCan()
