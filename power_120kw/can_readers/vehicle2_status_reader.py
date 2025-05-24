import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module2Message as mm2, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH

#logger = logging.getLogger(__name__)


class Vehicle2StatusReader(BaseReader):
    arbitration_id = 1537

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        vs2 = self._binary_data
        self._global_data.set_data_status_vehicle2(binaryToDecimal(int(vs2[0])))
        vehicle_status2 = binaryToDecimal(int(vs2[0]))
        #logger.info(f'Vehicle-2 status {vehicle_status2}')
        vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        #logger.info(f'Vehicle-1 status {vehicle_status1_g}')

        tag_vol2 = binaryToDecimal(int(vs2[2] + vs2[1]))
        target_volatge_from_car2 = (tag_vol2 / 10)

        tag_curr2 = binaryToDecimal(int(vs2[4] + vs2[3]))
        tag_curr22 = (tag_curr2 / 10)
        target_current_from_car2 = (tag_curr22)
        target_power2 = (target_volatge_from_car2 * tag_curr22)
        self._global_data.set_data_targetpower_ev2(target_power2)

        maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
        maxpowerev2_g = self._global_data.get_data_maxpower_ev2()

        if vehicle_status2 == 0 and vehicle_status1_g == 0 or vehicle_status2 == 6 and vehicle_status1_g == 6 or vehicle_status2 == 6 and vehicle_status1_g == 0:
            mm.digital_output_open_AC()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[6] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 2
                else:
                    mm2.digital_output_led_green2()
                    PECC.STATUS1_GUN2_DATA[0] = 0
            else:
                mm2.digital_output_led_green2()
                PECC.STATUS1_GUN2_DATA[0] = 0   

        if vehicle_status2 == 0 and vehicle_status1_g == 6 or vehicle_status2 == 0 and vehicle_status1_g == 2 or vehicle_status2 == 0 and vehicle_status1_g == 29:
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[6] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 2
                else:
                    mm2.digital_output_led_green2()
                    PECC.STATUS1_GUN2_DATA[0] = 0
            else:
                mm2.digital_output_led_green2()
                PECC.STATUS1_GUN2_DATA[0] = 0              

        if vehicle_status2 == 2 and vehicle_status1_g == 0 or vehicle_status2 == 2 and vehicle_status1_g == 6 :
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9            
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                PECC.STATUS1_GUN2_DATA[0] = 2
            elif digitl_input[6] == '1':
                mm2.digital_output_led_red2()
                mm.digital_output_open_AC()
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                mm2.digital_output_led_green2()
                mm.digital_output_close_AC()
                PECC.STATUS1_GUN2_DATA[0] = 0 

        if vehicle_status2 == 2 and vehicle_status1_g != 0 or vehicle_status2 == 2 and vehicle_status1_g != 6:
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()        
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9            
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                PECC.STATUS1_GUN2_DATA[0] = 2
            elif digitl_input[6] == '1':
                mm2.digital_output_led_red2()
                mm.digital_output_open_AC()
                PECC.STATUS1_GUN2_DATA[0] = 2
            else:
                mm2.digital_output_led_green2()
        
                PECC.STATUS1_GUN2_DATA[0] = 0

        if vehicle_status2 == 13 and vehicle_status1_g == 0 or vehicle_status2 == 13 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            mm2.digital_output_led_green2()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            if 0 < maxpowerev2_g <= 30000:
                mm2.digital_output_close_Gun21()
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 30000 and maxpowerev2_g <=60000:
                mm2.digital_output_close_Gun22()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 60000 and maxpowerev2_g <=90000:

                mm2.digital_output_close_Gun23()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                    mm.lowMode(CanId.CAN_ID_3)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)
                    mm.highMode(CanId.CAN_ID_3)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_3)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 90000:

                mm2.digital_output_close_Gun24()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 13 and vehicle_status1_g == 2 or vehicle_status2 == 13 and vehicle_status1_g == 35 or vehicle_status2 == 13 and vehicle_status1_g == 37:
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            if (target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm2.digital_output_Gun2_load11()
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_Gun2_load12()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                mm.stopModule(CanId.CAN_ID_1)
                mm2.digital_output_Gun2_load13()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 13 and vehicle_status1_g == 13 or vehicle_status2 == 13 and vehicle_status1_g == 21 or vehicle_status2 == 13 and vehicle_status1_g == 29:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            mm2.digital_output_led_green2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            if target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load21()
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)

                mm.readModule_Voltage(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load22()
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)

                mm.readModule_Voltage(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load23()
                
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)

                mm.readModule_Voltage(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (30000 < target_power_from_car2 <= 60000  and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load24()
            
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000  and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load25()
            
                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()
                
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                mm2.digital_output_load26()

                cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

                if cable_check_voltage2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)
                if cable_check_voltage2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()
                    

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 21 and vehicle_status1_g == 0 or vehicle_status2 == 21 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm2.digital_output_led_green2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            if 0 < maxpowerev2_g <= 30000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3

                mm2.digital_output_close_Gun21()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm2.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 30000 and maxpowerev2_g <=60000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7

                mm2.digital_output_close_Gun22()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 60000 and maxpowerev2_g <=90000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                mm2.digital_output_close_Gun23()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)
                    mm.lowMode(CanId.CAN_ID_3)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)
                    mm.highMode(CanId.CAN_ID_3)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                RUNNING_CURRENT = (target_current_from_car2/3)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_3)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                mm.readModule_Current(CanId.CAN_ID_3)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 90000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                mm2.digital_output_close_Gun24()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)
                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/4)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_1)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 21 and vehicle_status1_g == 2 or vehicle_status2 == 21 and vehicle_status1_g == 35 or vehicle_status2 == 21 and vehicle_status1_g == 37:
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))

            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()

            if (target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3

                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm2.digital_output_Gun2_load11()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
        
            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_Gun2_load12()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()
                    
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                mm.stopModule(CanId.CAN_ID_1)
                mm2.digital_output_Gun2_load13()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/3)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
        if vehicle_status2 == 21 and vehicle_status1_g == 13 or vehicle_status2 == 21 and vehicle_status1_g == 21 or vehicle_status2 == 21 and vehicle_status1_g == 29:
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            if target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load21()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load22()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load23()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load24()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000  and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load25()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000): 
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                mm2.digital_output_load26()

                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/3)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 29 and vehicle_status1_g == 0 or vehicle_status2 == 29 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm2.digital_output_led_blue2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            #self._global_data.set_data_maxpower2(maxpowerev2_g)
            if 0 < maxpowerev2_g <= 30000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3

                mm2.digital_output_close_Gun21()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm2.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 30000 and maxpowerev2_g <=60000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                if target_power_from_car2 <= 30000:
                    mm2.digital_output_close_Gun21()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                    RUNNING_CURRENT = (target_current_from_car2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)

                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm2.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 30000 and target_power_from_car2 <= 60000:
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_4)

                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_4)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    RUNNING_CURRENT = (target_current_from_car2/2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 60000 and maxpowerev2_g <=90000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                
                if target_power_from_car2 <= 30000:
                    mm2.digital_output_close_Gun21()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                    RUNNING_CURRENT = (target_current_from_car2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)

                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm2.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 30000 and target_power_from_car2 <= 60000:
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_4)

                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_4)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    RUNNING_CURRENT = (target_current_from_car2/2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 60000 and target_power_from_car2 <= 90000:
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_4)
                        mm.lowMode(CanId.CAN_ID_3)

                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_4)
                        mm.highMode(CanId.CAN_ID_3)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                    RUNNING_CURRENT = (target_current_from_car2/3)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.setCurrent(CanId.CAN_ID_3)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_3)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    mm.readModule_Current(CanId.CAN_ID_3)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        mm.stopModule(CanId.CAN_ID_3)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        mm.stopModule(CanId.CAN_ID_3)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2

            elif maxpowerev2_g > 90000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                if target_power_from_car2 <= 30000:
                    mm2.digital_output_close_Gun21()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                    RUNNING_CURRENT = (target_current_from_car2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)

                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm2.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 30000 and target_power_from_car2 <= 60000:
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_4)

                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_4)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    RUNNING_CURRENT = (target_current_from_car2/2)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 60000 and target_power_from_car2 <= 90000:
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_4)
                        mm.lowMode(CanId.CAN_ID_3)

                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_4)
                        mm.highMode(CanId.CAN_ID_3)

                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                    RUNNING_CURRENT = (target_current_from_car2/3)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.setCurrent(CanId.CAN_ID_3)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_3)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    mm.readModule_Current(CanId.CAN_ID_3)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        mm.stopModule(CanId.CAN_ID_3)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        mm.stopModule(CanId.CAN_ID_3)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2
                if target_power_from_car2 > 90000:        
                    mm2.digital_output_close_Gun24()
                    if target_volatge_from_car2 <= 500:
                        mm.lowMode(CanId.CAN_ID_1)
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_3)
                        mm.lowMode(CanId.CAN_ID_4)
                    if target_volatge_from_car2 > 500:
                        mm.highMode(CanId.CAN_ID_1)
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_3)
                        mm.highMode(CanId.CAN_ID_4)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_1)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                    RUNNING_CURRENT = (target_current_from_car2/4)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_1)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_3)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_1)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_3)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.readModule_Voltage(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_3)
                    mm.readModule_Current(CanId.CAN_ID_4)
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    if digitl_input[6] == '1':
                        mm2.digital_output_led_red2()
                        mm.digital_output_open_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 29 and vehicle_status1_g == 2 or vehicle_status2 == 29 and vehicle_status1_g == 35 or vehicle_status2 == 29 and vehicle_status1_g == 37:
        
            mm2.digital_output_led_blue2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))

            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            if (target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3

                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm2.digital_output_Gun2_load11()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
        
            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_Gun2_load12()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                mm.stopModule(CanId.CAN_ID_1)
                mm2.digital_output_Gun2_load13()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/3)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 29 and vehicle_status1_g == 13 or vehicle_status2 == 29 and vehicle_status1_g == 21 or vehicle_status2 == 29 and vehicle_status1_g == 29:
            mm2.digital_output_led_blue2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            if target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load21()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000:
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load22()
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

            if (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                mm2.digital_output_load23()
            
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), CanId.CAN_ID_2)

                RUNNING_CURRENT = (target_current_from_car2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load24()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            if (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000  and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                mm2.digital_output_load25()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/2)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()
                    
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2
            
            if (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                
                mm2.digital_output_load26()
                
                if target_volatge_from_car2 <= 500:
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)

                if target_volatge_from_car2 > 500:
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)

                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car2)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car2/3)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN2_DATA[0] = 3
                if digitl_input[6] == '1':
                    mm2.digital_output_led_red2()
                    mm.digital_output_open_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 2

        if vehicle_status2 == 37 and vehicle_status1_g == 0 or vehicle_status2 == 35 and vehicle_status1_g == 0 or vehicle_status2 == 37 and vehicle_status1_g == 6 or vehicle_status2 == 35 and vehicle_status1_g == 6:
            mm2.digital_output_led_red2()
            #maxpower2 = self._global_data.get_data_maxpower2()
            #print("max2=", maxpower2)
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)                                                                                          
            mm.stopModule(CanId.CAN_ID_4)
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.readModule_Voltage(CanId.CAN_ID_2)
            mm.readModule_Current(CanId.CAN_ID_2)
            PECC.STATUS1_GUN2_DATA[0] = 1
            

        if vehicle_status2 == 37 and vehicle_status1_g == 37 or vehicle_status2 == 35 and vehicle_status1_g == 35 or vehicle_status2 == 37 and vehicle_status1_g == 35 or vehicle_status2 == 35 and vehicle_status1_g == 37:
            mm2.digital_output_led_red2()
           
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.readModule_Voltage(CanId.CAN_ID_2)
            mm.readModule_Current(CanId.CAN_ID_2)
            PECC.STATUS1_GUN2_DATA[0] = 1

        if vehicle_status2 == 37 and vehicle_status1_g == 2 or vehicle_status2 == 37 and vehicle_status1_g == 13 or vehicle_status2 == 37 and vehicle_status1_g == 21 or vehicle_status2 == 37 and vehicle_status1_g == 29:
            mm2.digital_output_led_red2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            if (target_power_from_car2 <= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2 <= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 <= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 <= 30000 and target_power_from_car1 > 90000) :
                mm.stopModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
            elif (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2 <= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2 <= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2 <= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2 <= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2 <= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2 > 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2 > 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2 > 90000 and target_power_from_car1 > 90000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
            
            elif (60000 < target_power_from_car2 <= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2 > 90000 and target_power_from_car1 <= 30000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
            PECC.STATUS1_GUN2_DATA[0] = 1

        if vehicle_status2 == 35 and vehicle_status1_g == 2 or vehicle_status2 == 35 and vehicle_status1_g == 13 or vehicle_status2 == 35 and vehicle_status1_g == 21 or vehicle_status2 == 35 and vehicle_status1_g == 29:
            mm2.digital_output_led_red2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            if (target_power_from_car2<= 30000 and target_power_from_car1 <= 30000) or (target_power_from_car2<= 30000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2<= 30000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2<= 30000 and target_power_from_car1 > 90000) :
                mm.stopModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
            elif (30000 < target_power_from_car2<= 60000 and target_power_from_car1 <= 30000) or (30000 < target_power_from_car2<= 60000 and 30000 < target_power_from_car1 <= 60000) or (30000 < target_power_from_car2<= 60000 and 60000 < target_power_from_car1 <= 90000) or (30000 < target_power_from_car2<= 60000 and target_power_from_car1 > 90000) or (60000 < target_power_from_car2<= 90000 and 30000 < target_power_from_car1 <= 60000) or (60000 < target_power_from_car2<= 90000 and 60000 < target_power_from_car1 <= 90000) or (60000 < target_power_from_car2<= 90000 and target_power_from_car1 > 90000) or (target_power_from_car2> 90000 and 30000 < target_power_from_car1 <= 60000) or (target_power_from_car2> 90000 and 60000 < target_power_from_car1 <= 90000) or (target_power_from_car2> 90000 and target_power_from_car1 > 90000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
            
            elif (60000 < target_power_from_car2<= 90000 and target_power_from_car1 <= 30000) or (target_power_from_car2> 90000 and target_power_from_car1 <= 30000):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
            PECC.STATUS1_GUN2_DATA[0] = 1
          
