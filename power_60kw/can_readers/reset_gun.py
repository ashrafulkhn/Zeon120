
import time
import logging

from base_reader import BaseReader
from constants import PECC, CanId
from power_60kw.constant_manager_60kw import ConstantManager60KW
from power_60kw.message_helper import Module1Message as mm1, ModuleMessage as mm, Module2Message as mm2
from utility import bytetobinary
#logger = logging.getLogger(__name__)



class ResetGunModule1(BaseReader):
    arbitration_id = 774

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager60KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Reset Gun-1')
        vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        if vehicle_status2_g == 13 or vehicle_status2_g == 21 or vehicle_status2_g == 29:
            mm.stopModule(CanId.CAN_ID_1)
            mm1.digital_output_open_load1()
            mm1.digital_output_led_green1()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1' :
                mm1.digital_output_led_red1()
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
        else:
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm1.digital_output_led_red1()
            mm.digital_output_open_stop()
            time.sleep(10)
            mm.digital_output_open_fan()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
        


class ResetGunModule2(BaseReader):
    arbitration_id = 1542

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager60KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Reset Gun-2')
        vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        if vehicle_status1_g == 13 or vehicle_status1_g == 21 or vehicle_status1_g == 29:
            mm2.digital_output_open_load2()
            mm.stopModule(CanId.CAN_ID_2)
            mm2.digital_output_led_green2()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm2.digital_output_led_red2()
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                PECC.STATUS1_GUN2_DATA[0] = 0
        else:
            mm.stopModule(CanId.CAN_ID_1)
            mm2.digital_output_led_red2()
            mm.stopModule(CanId.CAN_ID_2)
            mm.digital_output_open_stop()
            time.sleep(10)
            mm.digital_output_open_fan()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                PECC.STATUS1_GUN2_DATA[0] = 0     