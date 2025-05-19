# import the library
import configparser
import time

from power_120kw.factory_reader import FactoryReader
from caninterface import CanInterface
from power_120kw.persistent_communication import set_status_update


def readAllCanData(messgage):
    """
    This function reads all the CAN data and calls the appropriate reader based on the arbitration ID.
    """
    reader = FactoryReader.create_reader(messgage.arbitration_id, messgage.data)
    if reader:
        reader.read_input_data()


def readFromCan():
    bus = CanInterface.bus_instance
    for message in bus:
        readAllCanData(message)


def perform_action():
    set_status_update()
    readFromCan()
