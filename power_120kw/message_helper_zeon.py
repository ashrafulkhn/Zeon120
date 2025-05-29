import can
from caninterface import CanInterface
from power_120kw.constant_manager_120kw import ConstantManager120KW
from constants import CanId
from utility import DTH

class ModuleMessage:
    bus = CanInterface.bus_instance

    @classmethod
    def digital_output_open_fan(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 128, 0])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_AC(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[64, 0, 64,0])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_AC(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 255, 48])
        cls.bus.send(message)
    
    @classmethod
    def digital_output_open_stop(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 63, 48])
        cls.bus.send(message)

    @classmethod
    def stopcharging(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=False, data=[])
        cls.bus.send(message)

    @classmethod
    def lowMode(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            16, 95, 0, 0, 0, 0, 0, 2])
        cls.bus.send(message)

    @classmethod
    def highMode(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            16, 95, 0, 0, 0, 0, 0, 1])
        cls.bus.send(message)

    @classmethod
    def readModule_Voltage(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            18, 98, 0, 0, 0, 0, 0, 0])
        cls.bus.send(message)

    @classmethod
    def readModule_Current(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            18, 48, 0, 0, 0, 0, 0, 0])
        cls.bus.send(message)

    @classmethod
    def readModule_Current1(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            18, 1, 0, 0, 0, 0, 0, 0])
        cls.bus.send(message)

    @classmethod
    def stopcharging(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=False, data=[])
        cls.bus.send(message)

    @classmethod
    def stopModule(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            16, 4, 0, 0, 0, 0, 0, 1])
        cls.bus.send(message)

    @classmethod
    def setVoltage(cls, voltageValue, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[16, 2, 0, 0, 0] + voltageValue)
        cls.bus.send(message)

    @classmethod
    def setCurrent(cls, can_id):
        global_data = ConstantManager120KW()
        tmp_current1 = DTH.convertohex(global_data.get_data_running_current())
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[16, 3, 0, 0, 0] + tmp_current1)

        cls.bus.send(message)

    @classmethod
    def startModule(cls, can_id):
        message = can.Message(arbitration_id=can_id, is_extended_id=True, data=[
            16, 4, 0, 0, 0, 0, 0, 0])
        cls.bus.send(message)
 


class Module1Message(ModuleMessage):

    @classmethod
    def digital_output_close_Gun11(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[193, 0, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun12(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[197, 16, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun13(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[245, 16, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun14(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[253, 48, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load11(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[193, 0, 197, 16])
        cls.bus.send(message)
    @classmethod

    def digital_output_load12(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[197, 16, 245, 16])
        cls.bus.send(message)

    @classmethod
    def digital_output_load13(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[245, 16, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load14(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[194, 0, 222, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load15(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[202, 32, 222, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load16(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[218, 32, 222, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun1_load21(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[193, 0, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun1_load22(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[197, 16, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun1_load23(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[245, 16, 253, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load11(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 193, 0])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load12(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 197, 16])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load13(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 245, 16])
        cls.bus.send(message)
    
    @classmethod
    def digital_output_led_red1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 1, 0, 3])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_green1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 2, 0, 3])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_blue1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[32, 0, 32, 3])       # data changed for 120kW
        cls.bus.send(message)

class Module2Message(ModuleMessage):

    @classmethod
    def digital_output_close_Gun21(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[194, 0, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun22(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[202, 32, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun23(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[250, 32, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_close_Gun24(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[254, 48, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load21(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[194, 0, 202, 32])
        cls.bus.send(message)

    @classmethod
    def digital_output_load22(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[202, 32, 250, 32])
        cls.bus.send(message)

    @classmethod
    def digital_output_load23(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[250, 32, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load24(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[203, 32, 223, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load25(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[207, 48, 223, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load26(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[219, 32, 223, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun2_load11(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[194, 0, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun2_load12(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[202, 32, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun2_load13(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[250, 32, 254, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load21(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 194, 0])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load22(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 202, 32])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load23(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[192, 0, 250, 32])
        cls.bus.send(message)

    @classmethod
    def digital_output_led_red2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 4, 0, 12])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_green2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 8, 0, 12])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_blue2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 64, 0, 76])       # data changed for 120kW
        cls.bus.send(message)


    