import can
import logging
import threading
import time

from constants import PECC, CanId, CONTACTOR
from caninterface import CanInterface

#logger = logging.getLogger(__name__)


class SetInterval:
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        try:
            thread=threading.Thread(target=self.__setInterval)
            thread.start()
            #logger.info(f"Started thread for constant status update from following method: {action.__name__}")
        except threading.ThreadException as err:
            pass
            #logger.error(f"Failed to start the thread for following method: {action.__name__}, error: {err}")

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()
        #logger.info(f"Stopped status update from following method: {self.action.__name__}")


class PECCStatusManager:
    # Bus interface
    bus = CanInterface.bus_instance

    @staticmethod
    def pecc_powers_voltage_limits_1():
        message = can.Message(arbitration_id=CanId.PECC_POWER_VOLTAGE_L1,
                              is_extended_id=False, data=PECC.LIMITS1_DATA_120kw_Gun1)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_current_limits_1():
        message = can.Message(arbitration_id=CanId.PECC_CURRENT_L1,
                              is_extended_id=False, data=PECC.LIMITS2_DATA_120kw_Gun1)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_status_1_Gun1():
        message = can.Message(arbitration_id=CanId.PECC_STATUS1_GUN1,
                              is_extended_id=False, data=PECC.STATUS1_GUN1_DATA)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_status_2_Gun1():
        message = can.Message(arbitration_id=CanId.PECC_STATUS2_GUN1,
                              is_extended_id=False, data=PECC.STATUS2_GUN1_DATA)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_powers_voltage_limits_2():
        message = can.Message(arbitration_id=CanId.PECC_POWER_VOLTAGE_L2,
                              is_extended_id=False, data=PECC.LIMITS1_DATA_120kw_Gun2)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_current_limits_2():
        message = can.Message(arbitration_id=CanId.PECC_CURRENT_L2,
                              is_extended_id=False, data=PECC.LIMITS2_DATA_120kw_Gun2)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_status_1_Gun2():
        message = can.Message(arbitration_id=CanId.PECC_STATUS1_Gun2,
                              is_extended_id=False, data=PECC.STATUS1_GUN2_DATA)
        PECCStatusManager.bus.send(message)

    @staticmethod
    def pecc_status_2_Gun2():
        message = can.Message(arbitration_id=CanId.PECC_STATUS2_Gun2,
                              is_extended_id=False, data=PECC.STATUS2_GUN2_DATA)
        PECCStatusManager.bus.send(message)

    
    @staticmethod
    def contactor_action():
        # Updated Contactor Status is being sent to the CAN bus to Vector
        print("Inside Contactor Action")
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=CONTACTOR.CONTACTOR_STATUS_DATA)
        PECCStatusManager.bus.send(message)

def set_status_update():
    # Get all the attributes of the class
    attributes = dir(PECCStatusManager)
    print("Inside set Status Update.")

    # Filter for methods
    send_status_methods = [attr for attr in attributes if callable(getattr(PECCStatusManager, attr)) and not attr.startswith('__')]

    # Invoke all the methods
    for send_status in send_status_methods:
        send_status_method = getattr(PECCStatusManager, send_status)
        SetInterval(0.25, send_status_method)
