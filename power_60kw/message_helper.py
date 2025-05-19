import can
from caninterface import CanInterface
from power_60kw.constant_manager_60kw import ConstantManager60KW
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
                              is_extended_id=False, data=[0, 0, 223, 48])
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
    def digital_output_open_stop(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 31, 48])
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
        global_data = ConstantManager60KW()
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
    def digital_output_close_Gun1(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[221, 48, 221, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load1(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[195, 0, 223, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun1_load2(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[193, 0, 221, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load1(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 29, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_led_red1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 1, 32, 3])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_blue1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 2, 32, 3])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_green1(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[32, 0, 32, 3])       # data changed for 120kW
        cls.bus.send(message)


class Module2Message(ModuleMessage):

    @classmethod
    def digital_output_close_Gun2(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[222, 48, 222, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_load2(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[195, 0, 223, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_Gun2_load1(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[194, 0, 222, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_open_load2(cls):
        message = can.Message(arbitration_id=CanId.DIGITAL_OUT,
                              is_extended_id=False, data=[0, 0, 30, 48])
        cls.bus.send(message)

    @classmethod
    def digital_output_led_red2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 4, 0, 76])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_blue2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 8, 0, 76])       # data changed for 120kW
        cls.bus.send(message)

    @classmethod
    def digital_output_led_green2(cls):
        message=can.Message(arbitration_id=CanId.DIGITAL_OUT,
                          is_extended_id=False, data=[0, 64, 0, 76])       # data changed for 120kW
        cls.bus.send(message)

    