import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_60kw.constant_manager_60kw import ConstantManager60KW
from power_60kw.message_helper import Module1Message as mm1, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH

#logger = logging.getLogger(__name__)


class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager60KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        vs1 = self._binary_data
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))
        vehicle_status1 = binaryToDecimal(int(vs1[0]))
        #logger.info(f'Vehicle-1 status {vehicle_status1}')
        vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        

        #logger.info(f'Vehicle-2 status {vehicle_status2_g}')
        tag_vol1 = binaryToDecimal(int(vs1[2] + vs1[1]))
        target_volatge_from_car1 = (tag_vol1 / 10)

        tag_curr1 = binaryToDecimal(int(vs1[4] + vs1[3]))
        tag_curr11 = (tag_curr1 / 10)
        target_current_from_car1 = (tag_curr11 / 2)

        target_power1 = int(target_volatge_from_car1 * tag_curr11)
        self._global_data.set_data_targetpower_ev1(target_power1)

        if vehicle_status1 == 0 and vehicle_status2_g == 0 or vehicle_status1 == 6 and vehicle_status2_g == 6 or vehicle_status1 == 6 and vehicle_status2_g == 0:
            mm.digital_output_open_AC()
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    PECC.STATUS1_GUN1_DATA[0] = 2
                    mm1.digital_output_led_red1()
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm1.digital_output_led_green1()
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
                mm1.digital_output_led_green1()
                    
        if vehicle_status1 == 0 and vehicle_status2_g == 6:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    PECC.STATUS1_GUN1_DATA[0] = 2
                    mm1.digital_output_led_red1()
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm1.digital_output_led_green1()
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
                mm1.digital_output_led_green1()

        if vehicle_status1 == 2 and vehicle_status2_g == 0 or vehicle_status1 == 2 and vehicle_status2_g == 6 :
            
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                mm1.digital_output_led_green1()
                mm.digital_output_close_AC()
                PECC.STATUS1_GUN1_DATA[0] = 0
        if vehicle_status1 == 2 and vehicle_status2_g != 0 or vehicle_status1 == 2 and vehicle_status2_g != 6 :
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                PECC.STATUS1_GUN1_DATA[0] = 2
            else:
                mm1.digital_output_led_green1()
                
                PECC.STATUS1_GUN1_DATA[0] = 0

        if vehicle_status1 == 13 and vehicle_status2_g == 0 or vehicle_status1 == 13 and vehicle_status2_g == 6:

            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
            mm1.digital_output_led_green1()

            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            if maxpowerev1_g > 30000:

                mm1.digital_output_close_Gun1()

                cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))

                if cable_check_voltage1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                    mm.lowMode(CanId.CAN_ID_2)
                if cable_check_voltage1 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(10)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 3

            if maxpowerev1_g <= 30000:
                     
                mm1.digital_output_Gun1_load2()
                mm.stopModule(CanId.CAN_ID_2)
                cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))

                if cable_check_voltage1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                if cable_check_voltage1 > 500:
                    mm.highMode(CanId.CAN_ID_1)

                mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_1)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(10)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 13 and vehicle_status2_g == 2 or vehicle_status1 == 13 and vehicle_status2_g == 37 or vehicle_status1 == 13 and vehicle_status2_g == 35:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm.stopModule(CanId.CAN_ID_2)
            mm1.digital_output_Gun1_load2()
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1

            cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))

            if cable_check_voltage1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)

            if cable_check_voltage1 > 500:
                mm.highMode(CanId.CAN_ID_1)

            mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 13 and vehicle_status2_g == 13 or vehicle_status1 == 13 and vehicle_status2_g == 21 or vehicle_status1 == 13 and vehicle_status2_g == 29:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm1.digital_output_load1()
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1

            cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))

            if cable_check_voltage1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)

            if cable_check_voltage1 > 500:
                mm.highMode(CanId.CAN_ID_1)

            mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)

            mm.readModule_Voltage(CanId.CAN_ID_1)

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_1)
                
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 21 and vehicle_status2_g == 0 or vehicle_status1 == 21 and vehicle_status2_g == 6:
            
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))

            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            if maxpowerev1_g > 30000:
                PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
                PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
                PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
                PECC.LIMITS2_DATA_60kw_Gun1[3] = 7

                mm1.digital_output_close_Gun1()
                if target_volatge_from_car1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car1 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_2)
                RUNNING_CURRENT = (target_current_from_car1)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_1)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(10)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 3

            elif maxpowerev1_g <= 30000:
                PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
                PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
                PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
                PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
                mm1.digital_output_Gun1_load2()
                if target_volatge_from_car1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)

                if target_volatge_from_car1 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

                RUNNING_CURRENT = (target_current_from_car1 * 2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_1)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(10)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 21 and vehicle_status2_g == 2 or vehicle_status1 == 21 and vehicle_status2_g == 35 or vehicle_status1 == 21 and vehicle_status2_g == 37:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm.stopModule(CanId.CAN_ID_2)
            mm1.digital_output_Gun1_load2()
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
        
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

            RUNNING_CURRENT = (target_current_from_car1 * 2)

            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 21 and vehicle_status2_g == 13 or vehicle_status1 == 21 and vehicle_status2_g == 21 or vehicle_status1 == 21 and vehicle_status2_g == 29:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm1.digital_output_load1()
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

            RUNNING_CURRENT = (target_current_from_car1 * 2)

            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 29 and vehicle_status2_g == 0 or vehicle_status1 == 29 and vehicle_status2_g == 6:
            
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            mm1.digital_output_led_blue1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()                                                               
            if maxpowerev1_g > 30000:
                PECC.LIMITS1_DATA_60kw_Gun1[4] = 112
                PECC.LIMITS1_DATA_60kw_Gun1[5] = 23
                PECC.LIMITS2_DATA_60kw_Gun1[2] = 208
                PECC.LIMITS2_DATA_60kw_Gun1[3] = 7
                if target_power_from_car1 <= 30000:
                    mm1.digital_output_Gun1_load2()
                    mm.stopModule(CanId.CAN_ID_2)
                    if target_volatge_from_car1 <= 500:
                        mm.lowMode(CanId.CAN_ID_1)

                    if target_volatge_from_car1 > 500:
                        mm.highMode(CanId.CAN_ID_1)
                    mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

                    RUNNING_CURRENT = (target_current_from_car1 * 2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_1)
                    mm.startModule(CanId.CAN_ID_1)
                    mm.readModule_Voltage(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_1)
            
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(10)
                        mm.digital_output_open_fan()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN1_DATA[0] = 3
                if target_power_from_car1 > 30000:
                    mm1.digital_output_close_Gun1()
                    if target_volatge_from_car1 <= 500:
                        mm.lowMode(CanId.CAN_ID_1)
                        mm.lowMode(CanId.CAN_ID_2)

                    if target_volatge_from_car1 > 500:
                        mm.highMode(CanId.CAN_ID_1)
                        mm.highMode(CanId.CAN_ID_2)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_2)
                    RUNNING_CURRENT = (target_current_from_car1)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_1)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_1)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.readModule_Voltage(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_2)
                
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(10)
                        mm.digital_output_open_fan()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN1_DATA[0] = 3
            elif maxpowerev1_g <= 30000:
                PECC.LIMITS1_DATA_60kw_Gun1[4] = 184                                                                                         
                PECC.LIMITS1_DATA_60kw_Gun1[5] = 11                                                                                    
                PECC.LIMITS2_DATA_60kw_Gun1[2] = 232                                                                                         
                PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
                mm1.digital_output_Gun1_load2()
                mm.stopModule(CanId.CAN_ID_2)
                if target_volatge_from_car1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)

                if target_volatge_from_car1 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

                RUNNING_CURRENT = (target_current_from_car1 * 2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_1)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
            
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(10)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN1_DATA[0] = 3

        if vehicle_status1 == 29 and vehicle_status2_g == 2 or vehicle_status1 == 29 and vehicle_status2_g == 35 or vehicle_status1 == 29 and vehicle_status2_g == 37:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm1.digital_output_Gun1_load2()
            mm.stopModule(CanId.CAN_ID_2)
            mm1.digital_output_led_blue1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

            RUNNING_CURRENT = (target_current_from_car1 * 2)

            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3


        if vehicle_status1 == 29 and vehicle_status2_g == 13 or vehicle_status1 == 29 and vehicle_status2_g == 21 or vehicle_status1 == 29 and vehicle_status2_g == 29:
            PECC.LIMITS1_DATA_60kw_Gun1[4] = 184
            PECC.LIMITS1_DATA_60kw_Gun1[5] = 11
            PECC.LIMITS2_DATA_60kw_Gun1[2] = 232
            PECC.LIMITS2_DATA_60kw_Gun1[3] = 3
            mm1.digital_output_load1()
            mm1.digital_output_led_blue1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

            RUNNING_CURRENT = (target_current_from_car1 * 2)

            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load1()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] =='1' or digitl_input[6] =='1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN1_DATA[0] = 3
        if vehicle_status1 == 37 and vehicle_status2_g == 0 or vehicle_status1 == 35 and vehicle_status2_g == 0 or vehicle_status1 == 35 and vehicle_status2_g == 6 or vehicle_status1 == 37 and vehicle_status2_g == 6:
            mm1.digital_output_led_green1()
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_2)
            PECC.STATUS1_GUN1_DATA[0] = 1
            
        if vehicle_status1 == 37 and vehicle_status2_g == 35 or vehicle_status1 == 35 and vehicle_status2_g == 37 or vehicle_status1 == 35 and vehicle_status2_g == 35 or vehicle_status1 == 37 and vehicle_status2_g == 35:
            mm1.digital_output_led_green1()
            mm.stopModule(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
           

        if vehicle_status1 == 37 and vehicle_status2_g == 2 or vehicle_status1 == 37 and vehicle_status2_g == 13 or vehicle_status1 == 37 and vehicle_status2_g == 21 or vehicle_status1 == 37 and vehicle_status2_g == 29:
            mm1.digital_output_led_green1()
            mm.stopModule(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1

        if vehicle_status1 == 35 and vehicle_status2_g == 2 or vehicle_status1 == 35 and vehicle_status2_g == 13 or vehicle_status1 == 35 and vehicle_status2_g == 21 or vehicle_status1 == 35 and vehicle_status2_g == 29:
            mm1.digital_output_led_green1()
            mm.stopModule(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
           
          