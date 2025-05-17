
import time
import logging

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm, Module2Message as mm2
from utility import bytetobinary
#logger = logging.getLogger(__name__)



class ResetGunModule1(BaseReader):
    arbitration_id = 774

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Reset Gun-1')
        vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        if vehicle_status2_g == 13 or vehicle_status2_g == 21 or vehicle_status2_g == 29:
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            mm1.digital_output_led_red1()
            if (target_power_from_car1 <= 30000 and target_power_from_car2 <= 30000) or (target_power_from_car1 <= 30000 and 30000 < target_power_from_car2 <= 60000) or (target_power_from_car1 <= 30000 and 60000 < target_power_from_car2 <= 90000) or (target_power_from_car1 <= 30000 and target_power_from_car2 > 90000):
                mm.stopModule(CanId.CAN_ID_1)
                mm1.digital_output_open_load11()
            if (30000 < target_power_from_car1 <= 60000 and target_power_from_car2 <= 30000) or (30000 < target_power_from_car1 <= 60000 and 30000 < target_power_from_car2 <= 60000) or (30000 < target_power_from_car1 <= 60000 and 60000 < target_power_from_car2 <= 90000) or (30000 < target_power_from_car1 <= 60000 and target_power_from_car2 > 90000) or (60000 < target_power_from_car1 <= 90000 and 30000 < target_power_from_car2 <= 60000) or (60000 < target_power_from_car1 <= 90000 and 60000 < target_power_from_car2 <= 90000) or (60000 < target_power_from_car1 <= 90000 and target_power_from_car2 > 90000) or (target_power_from_car1 > 90000 and 30000 < target_power_from_car2 <= 60000) or (target_power_from_car1 > 90000 and 60000 < target_power_from_car2 <= 90000) or (target_power_from_car1 > 90000 and target_power_from_car2 > 90000):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm1.digital_output_open_load12()
            if (60000 < target_power_from_car1 <= 90000 and target_power_from_car2 <= 30000) or (target_power_from_car1 > 90000 and target_power_from_car2 <= 30000):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm1.digital_output_open_load13()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1':
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
        else:
            mm1.digital_output_led_red1()
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            mm.digital_output_open_stop()
            time.sleep(10)
            mm.digital_output_open_fan()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
            


class ResetGunModule2(BaseReader):
    arbitration_id = 1542

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Reset Gun-2')
        vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        if vehicle_status1_g == 13 or vehicle_status1_g == 21 or vehicle_status1_g == 29:
            mm2.digital_output_led_red2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            if (target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000):
                mm.stopModule(CanId.CAN_ID_2)
                mm2.digital_output_open_load21()
            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm2.digital_output_open_load22()
            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_open_load23()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1':
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                PECC.STATUS1_GUN2_DATA[0] = 0
            
        else:
            mm2.digital_output_led_red2()
            #maxpowerev2_g = self._global_data.get_data_maxpower2()
            #print("max22=", maxpower2)
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            mm.digital_output_open_stop()
            time.sleep(10)
            mm.digital_output_open_fan()
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1':
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                PECC.STATUS1_GUN2_DATA[0] = 0

#end
