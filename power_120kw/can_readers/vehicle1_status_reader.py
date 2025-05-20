import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH
import math

from power_120kw.can_readers.power_module_reader import PowerModuleReader

logger = logging.getLogger(__name__)


class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self.limitChangeRequested = False

    #  Return the real-time voltage, current and power
    def getRealTimeVIP(self):
        s2gd = bytetobinary(PECC.STATUS2_GUN1_DATA)

        voltage_pre = binaryToDecimal(int(s2gd[1] + s2gd[0]))
        self._voltage = (voltage_pre / 10)

        current_pre = binaryToDecimal(int(s2gd[3] + s2gd[2]))
        self._current = (current_pre / 10)

        self._readPower = int(self._voltage * self._current)
        print(f"Real-time Voltage: {self._voltage}V, Current: {self._current}A, Power: {self._readPower}W  || Target Power: {self._global_data.get_data_targetpower_ev1()}W")
        return self._readPower, self._voltage, self._current
    
    def limitChangeRequest(self, limitPower):
        print(f"Limit Power: {limitPower}")
        val = abs(limitPower - self._readPower)    # 35 - 34 = 1; 35 - 36 = -1
        print(f"Comparision value: Limit Power: {limitPower}, Read Power: {self._readPower}, Difference Value: {val}")
        if val <= 2000:  # 2kW
            self.limitChangeRequested = True
        else:
            self.limitChangeRequested = False
        
        print(f"Limit Change Requested status: {self.limitChangeRequested}")
        
    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        vs1 = self._binary_data
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))
        vehicle_status1 = binaryToDecimal(int(vs1[0]))
        #logger.info(f'Vehicle-1 status {vehicle_status1}')
        vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        
        self.getRealTimeVIP()   # To update the real-time voltage, current and power
        print(f"Real-time Power: {self._readPower}W")

        #logger.info(f'Vehicle-2 status {vehicle_status2_g}')
        tag_vol1 = binaryToDecimal(int(vs1[2] + vs1[1]))
        target_volatge_from_car1 = (tag_vol1 / 10)

        tag_curr1 = binaryToDecimal(int(vs1[4] + vs1[3]))
        tag_curr11 = (tag_curr1 / 10)
        target_current_from_car1 = (tag_curr11 )

        target_power1 = int(target_volatge_from_car1 * tag_curr11)
        self._global_data.set_data_targetpower_ev1(target_power1)

        maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
        maxpowerev2_g = self._global_data.get_data_maxpower_ev2()

        def funct_40_cc():
            cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))
            if cable_check_voltage1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if cable_check_voltage1 > 500:
                mm.highMode(CanId.CAN_ID_1)

            mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 3

        def funct_40_1():
            
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)

            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex(target_volatge_from_car1), CanId.CAN_ID_1)

            RUNNING_CURRENT = (target_current_from_car1)
            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()
            

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 3

        def funct_80_1():
            
            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
                mm.lowMode(CanId.CAN_ID_3)

            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
                mm.highMode(CanId.CAN_ID_3)

            mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_3)
            RUNNING_CURRENT = (target_current_from_car1/2)
            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.setCurrent(CanId.CAN_ID_3)
            mm.startModule(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_3)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_3)
            digitl_input = self._global_data.get_data()
            

            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                PECC.STATUS1_GUN1_DATA[0] = 3

        def funct_120_1():

            if target_volatge_from_car1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
                mm.lowMode(CanId.CAN_ID_3)
                mm.lowMode(CanId.CAN_ID_4)

            if target_volatge_from_car1 > 500:
                mm.highMode(CanId.CAN_ID_1)
                mm.highMode(CanId.CAN_ID_3)
                mm.highMode(CanId.CAN_ID_4)

            mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
            mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_3)
            mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_4)
            RUNNING_CURRENT = (target_current_from_car1/3)
            self._global_data.set_data_running_current(RUNNING_CURRENT)
            mm.setCurrent(CanId.CAN_ID_1)
            mm.setCurrent(CanId.CAN_ID_3)
            mm.setCurrent(CanId.CAN_ID_4)
            mm.startModule(CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_3)
            mm.startModule(CanId.CAN_ID_4)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_3)
            mm.readModule_Current(CanId.CAN_ID_4)
            digitl_input = self._global_data.get_data()
            
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                PECC.STATUS1_GUN1_DATA[0] = 3
        
        if vehicle_status1 == 0 and vehicle_status2_g == 0 or vehicle_status1 == 6 and vehicle_status2_g == 6 or vehicle_status1 == 6 and vehicle_status2_g == 0:
            mm.digital_output_open_AC()
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 128                                                                                   
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 62                                                                              
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 134                                                                                    
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
            pm1=0
            self._global_data.set_data_pm_assign1(pm1)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 2
                    mm1.digital_output_led_red1()
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm1.digital_output_led_green1()
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
                mm1.digital_output_led_green1()

        if vehicle_status1 == 0 and vehicle_status2_g == 6 or vehicle_status1 == 0 and vehicle_status2_g == 2 or vehicle_status1 == 0 and vehicle_status2_g == 29 :
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 128                                                                                    
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 62                                                                              
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 134                                                                                    
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
            pm1=0
            self._global_data.set_data_pm_assign1(pm1)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or  digitl_input[7] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 2
                    mm1.digital_output_led_red1()
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm1.digital_output_led_green1()
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
                mm1.digital_output_led_green1()

        if vehicle_status1 == 2 and vehicle_status2_g == 0 or vehicle_status1 == 2 and vehicle_status2_g == 6 :
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 128                                                                                    
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 62                                                                              
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 134                                                                                    
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
            pm1=0
            self._global_data.set_data_pm_assign1(pm1)
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0'  :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                PECC.STATUS1_GUN1_DATA[0] = 2
            
            else:
                mm1.digital_output_led_green1()
                mm.digital_output_close_AC()
                PECC.STATUS1_GUN1_DATA[0] = 0

        if vehicle_status1 == 2 and vehicle_status2_g == 13 or vehicle_status1 == 2 and vehicle_status2_g == 21 or vehicle_status1 == 2 and vehicle_status2_g == 29:
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 128                                                                                    
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 62                                                                              
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 134                                                                                    
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[0] = 0
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm1=0
            self._global_data.set_data_pm_assign1(pm1)
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (target_power_from_car2 <= 38000) or (pm_assign2 == 1):
                mm1.digital_output_load14()

            if (42000 < target_power_from_car2 <= 78000) or (pm_assign2 == 2):
                mm1.digital_output_load15()

            if (target_power_from_car2 > 82000):
                mm1.digital_output_load16()

            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0'  :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                PECC.STATUS1_GUN1_DATA[0] = 2
            

        if (vehicle_status1 == 13 and vehicle_status2_g == 0) or (vehicle_status1 == 13 and vehicle_status2_g == 6):

            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1
            mm1.digital_output_led_green1()
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 128                                                                                    
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 62                                                                              
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 134                                                                                    
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            
            mm1.digital_output_close_Gun11()
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            funct_40_cc()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm.digital_output_open_stop()
                time.sleep(5)
                mm.digital_output_open_fan()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

               
        if vehicle_status1 == 13 and vehicle_status2_g == 2 or vehicle_status1 == 13 and vehicle_status2_g == 37 or vehicle_status1 == 13 and vehicle_status2_g == 35:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1
            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
                
            mm1.digital_output_Gun1_load21()
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            mm.stopModule(CanId.CAN_ID_2) 
            mm.stopModule(CanId.CAN_ID_4)
            mm.stopModule(CanId.CAN_ID_3) 
            funct_40_cc()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()
                
            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

                
        if vehicle_status1 == 13 and vehicle_status2_g == 13 or vehicle_status1 == 13 and vehicle_status2_g == 21 or vehicle_status1 == 13 and vehicle_status2_g == 29:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.STATUS1_GUN1_DATA[0] = 1
            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
            mm1.digital_output_load11()
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            funct_40_cc()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)                
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5
           

                #precharge



                

        if vehicle_status1 == 21 and vehicle_status2_g == 0 or vehicle_status1 == 21 and vehicle_status2_g == 6:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            
            mm1.digital_output_close_Gun11()
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            funct_40_1()

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm.digital_output_open_stop()
                time.sleep(5)
                mm1.digital_output_open_fan()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

            
                
                

        if vehicle_status1 == 21 and vehicle_status2_g == 2 or vehicle_status1 == 21 and vehicle_status2_g == 35 or vehicle_status1 == 21 and vehicle_status2_g == 37:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            
            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
            mm1.digital_output_Gun1_load21()
            mm.stopModule(CanId.CAN_ID_2) 
            mm.stopModule(CanId.CAN_ID_4)
            mm.stopModule(CanId.CAN_ID_3) 
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            funct_40_1()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()
                
            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        if vehicle_status1 == 21 and vehicle_status2_g == 13 or vehicle_status1 == 21 and vehicle_status2_g == 21 or vehicle_status1 == 21 and vehicle_status2_g == 29:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm1.digital_output_led_green1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
            mm1.digital_output_load11()
            pm1=1
            self._global_data.set_data_pm_assign1(pm1)
            funct_40_1()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)                
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5
                
        if vehicle_status1 == 29 and vehicle_status2_g == 0 or vehicle_status1 == 29 and vehicle_status2_g == 6:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            
            mm1.digital_output_led_blue1()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()

            """
            We are removing the check for maxpowerev1_g as we are doing the check based onj the target power power from car
            """

            # if maxpowerev1_g > 120000 :
                
            if target_power_from_car1 <= 38000:
                # set limit 35kW
                # _limit = 35000
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 172
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 13
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9

                # Assign modules for Gun1
                pm1=1
                pm_assign1 = self._global_data.set_data_pm_assign1(pm1)

                mm1.digital_output_close_Gun11()
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.stopModule(CanId.CAN_ID_3)

                # Check the realtime votage and current
                
                self.limitChangeRequest(35000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm1.digital_output_close_Gun11()
                    funct_40_1()

                else:
                    # set limit to 75kW
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 76
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 29
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5


            if target_power_from_car1 > 38000 and target_power_from_car1 < 42000:
                # PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                # PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                # PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                # PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 1):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm1.digital_output_close_Gun11()
                    funct_40_1()
                elif (pm_assign1 == 2):
                    mm1.digital_output_close_Gun12()
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    funct_80_1()

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            if target_power_from_car1 >= 42000 and target_power_from_car1 <= 78000:
                pm1=2
                pm_assign1 = self._global_data.set_data_pm_assign1(pm1)
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)

                self.limitChangeRequest(75000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm1.digital_output_close_Gun12()
                    funct_80_1()
                else:
                    # set limit to 115kW
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 236
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 44
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()
                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
            

            if target_power_from_car1 > 78000 and target_power_from_car1 < 82000:
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 2):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_close_Gun12()
                    funct_80_1()
                elif (pm_assign1 == 3):
                    mm1.digital_output_close_Gun13()
                    mm.stopModule(CanId.CAN_ID_2)
                    funct_120_1()

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
                
            if target_power_from_car1 >= 82000 and target_power_from_car1 <= 118000:

                mm.stopModule(CanId.CAN_ID_2)
                pm1=3
                pm_assign1 = self._global_data.set_data_pm_assign1(pm1)

                self.limitChangeRequest(115000)  # Updates the limitChangeRequested variable to true if the limit is reached
                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm1.digital_output_close_Gun13()
                    funct_120_1()
                else:
                    # set limit to 160kW
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 128
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 62
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 134
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 11
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()
                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            if target_power_from_car1 > 118000 and target_power_from_car1 < 122000:
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 3):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm1.digital_output_close_Gun13()
                    funct_120_1()
                elif (pm_assign1 == 4):
                    mm1.digital_output_close_Gun14()
                    if target_volatge_from_car1 <= 500:
                        mm.lowMode(CanId.CAN_ID_1)
                        mm.lowMode(CanId.CAN_ID_2)
                        mm.lowMode(CanId.CAN_ID_3)
                        mm.lowMode(CanId.CAN_ID_4)
                    if target_volatge_from_car1 > 500:
                        mm.highMode(CanId.CAN_ID_1)
                        mm.highMode(CanId.CAN_ID_2)
                        mm.highMode(CanId.CAN_ID_3)
                        mm.highMode(CanId.CAN_ID_4)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_2)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_3)
                    mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_4)
                    RUNNING_CURRENT = (target_current_from_car1/4)
                    self._global_data.set_data_running_current(RUNNING_CURRENT)
                    mm.setCurrent(CanId.CAN_ID_1)
                    mm.setCurrent(CanId.CAN_ID_2)
                    mm.setCurrent(CanId.CAN_ID_3)
                    mm.setCurrent(CanId.CAN_ID_4)
                    mm.startModule(CanId.CAN_ID_1)
                    mm.startModule(CanId.CAN_ID_2)
                    mm.startModule(CanId.CAN_ID_3)
                    mm.startModule(CanId.CAN_ID_4)
                    mm.readModule_Voltage(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_1)
                    mm.readModule_Current(CanId.CAN_ID_2)
                    mm.readModule_Current(CanId.CAN_ID_3)
                    mm.readModule_Current(CanId.CAN_ID_4)

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 3
                

            if target_power_from_car1 >= 122000:
                mm1.digital_output_close_Gun14()
                pm1=4
                pm_assign1 = self._global_data.set_data_pm_assign1(pm1)
                if target_volatge_from_car1 <= 500:
                    mm.lowMode(CanId.CAN_ID_1)
                    mm.lowMode(CanId.CAN_ID_2)
                    mm.lowMode(CanId.CAN_ID_3)
                    mm.lowMode(CanId.CAN_ID_4)
                if target_volatge_from_car1 > 500:
                    mm.highMode(CanId.CAN_ID_1)
                    mm.highMode(CanId.CAN_ID_2)
                    mm.highMode(CanId.CAN_ID_3)
                    mm.highMode(CanId.CAN_ID_4)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_1)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_2)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_3)
                mm.setVoltage(DTH.convertohex((target_volatge_from_car1)), CanId.CAN_ID_4)
                RUNNING_CURRENT = (target_current_from_car1/4)
                self._global_data.set_data_running_current(RUNNING_CURRENT)
                mm.setCurrent(CanId.CAN_ID_1)
                mm.setCurrent(CanId.CAN_ID_2)
                mm.setCurrent(CanId.CAN_ID_3)
                mm.setCurrent(CanId.CAN_ID_4)
                mm.startModule(CanId.CAN_ID_1)
                mm.startModule(CanId.CAN_ID_2)
                mm.startModule(CanId.CAN_ID_3)
                mm.startModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    PECC.STATUS1_GUN1_DATA[0] = 3
                
        if vehicle_status1 == 29 and vehicle_status2_g == 2 or vehicle_status1 == 29 and vehicle_status2_g == 35 or vehicle_status1 == 29 and vehicle_status2_g == 37:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm1.digital_output_led_blue1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (target_power_from_car1 <= 38000) :
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
                pm1=1
                self._global_data.set_data_pm_assign1(pm1)
                mm1.digital_output_Gun1_load21()
                mm.stopModule(CanId.CAN_ID_2) 
                mm.stopModule(CanId.CAN_ID_4)
                mm.stopModule(CanId.CAN_ID_3)
                funct_40_1() 
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)                
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 
            if (38000 < target_power_from_car1 <= 42000) :
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_Gun1_load21()
                    mm.stopModule(CanId.CAN_ID_2) 
                    mm.stopModule(CanId.CAN_ID_4)
                    mm.stopModule(CanId.CAN_ID_3)
                    funct_40_1() 
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load11()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5
                elif(pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_Gun1_load22()
                    funct_80_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)  
                        mm.stopModule(CanId.CAN_ID_3)              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
            
            if (42000 < target_power_from_car1 <= 78000):
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                pm1=2
                self._global_data.set_data_pm_assign1(pm1)
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm1.digital_output_Gun1_load22()
                funct_80_1() 
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1) 
                    mm.stopModule(CanId.CAN_ID_3)               
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            if (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 1) or (78000 < target_power_from_car1 <= 82000 and target_power_from_car2 <= 38000):
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_Gun1_load22()
                    funct_80_1()  
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1) 
                        mm.stopModule(CanId.CAN_ID_3)               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                if (pm_assign1 == 3):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    
                    mm.stopModule(CanId.CAN_ID_2)
                    mm1.digital_output_Gun1_load23()
                    funct_120_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)  
                        mm.stopModule(CanId.CAN_ID_4)              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load13()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            if (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 2) or (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 3):
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_Gun1_load22()
                    funct_80_1() 
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1) 
                        mm.stopModule(CanId.CAN_ID_3)               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif(pm_assign1 == 3):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_Gun1_load22()
                    funct_80_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            if (target_power_from_car1 > 82000 and pm_assign2 == 1) or (target_power_from_car1 > 82000 and target_power_from_car1 <= 38000):
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                pm1=3
                self._global_data.set_data_pm_assign1(pm1)
                mm.stopModule(CanId.CAN_ID_2)
                mm1.digital_output_Gun1_load23()
                funct_120_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)  
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)              
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load13()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            if (target_power_from_car1 > 82000 and pm_assign2 == 2) or (target_power_from_car1 > 82000 and pm_assign2 == 3):
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                mm1.digital_output_load12()
                pm1=2
                self._global_data.set_data_pm_assign1(pm1)
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm1.digital_output_Gun1_load22()
                funct_80_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)   
                    mm.stopModule(CanId.CAN_ID_3)             
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 
               
        if vehicle_status1 == 29 and vehicle_status2_g == 13 or vehicle_status1 == 29 and vehicle_status2_g == 21 or vehicle_status1 == 29 and vehicle_status2_g == 29:
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm1.digital_output_led_blue1()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (target_power_from_car1 <= 38000 and pm_assign2 == 1) or (target_power_from_car1 <= 38000 and pm_assign2 == 2) :
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
                mm1.digital_output_load11()
                mm.stopModule(CanId.CAN_ID_3)
                pm1=1
                self._global_data.set_data_pm_assign1(pm1)
                funct_40_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)                
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            if (target_power_from_car1 <= 38000 and pm_assign2 == 3) :
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 5
                mm1.digital_output_load11()
                pm1=1
                self._global_data.set_data_pm_assign1(pm1)
                funct_40_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)                
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            if 38000 < target_power_from_car1 <= 42000 :
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load11()
                    funct_40_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load11()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif(pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load12()
                    funct_80_1()

                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)  
                        mm.stopModule(CanId.CAN_ID_3)              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            if 42000 < target_power_from_car1 <= 78000 :
                pm1=2
                self._global_data.set_data_pm_assign1(pm1)
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                mm1.digital_output_load12()
                funct_80_1()

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1) 
                    mm.stopModule(CanId.CAN_ID_3)               
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            if (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 1) or (78000 < target_power_from_car1 <= 82000 and target_power_from_car2 <= 38000):
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load12()
                    funct_80_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif(pm_assign1 == 3):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load13()
                    funct_120_1()

                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1) 
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load13()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            if (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 2) or (78000 < target_power_from_car1 <= 82000 and pm_assign2 == 3):
                pm_assign1 = self._global_data.get_data_pm_assign1()
                if (pm_assign1 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load12()
                    funct_80_1()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1) 
                        mm.stopModule(CanId.CAN_ID_3)               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif(pm_assign1 == 3):
                    PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    mm1.digital_output_load12()
                    funct_80_1()
                
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1) 
                        mm.stopModule(CanId.CAN_ID_3)               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                    
         
            if (target_power_from_car1 > 82000 and pm_assign2 == 1) or (target_power_from_car1 > 82000 and target_power_from_car2 <= 38000):
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                pm1=3
                self._global_data.set_data_pm_assign1(pm1)
                mm1.digital_output_load13()
                funct_120_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1) 
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)               
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load13()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            if (target_power_from_car1 > 82000 and pm_assign2 == 2) or (target_power_from_car1 > 82000 and pm_assign2 == 3) or (target_power_from_car1 > 82000 and target_power_from_car2 > 42000):
                PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                mm1.digital_output_load12()
                pm1=2
                self._global_data.set_data_pm_assign1(pm1)
                funct_80_1()
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)   
                    mm.stopModule(CanId.CAN_ID_3)             
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5    
                
        if vehicle_status1 == 37 and vehicle_status2_g == 0 or vehicle_status1 == 35 and vehicle_status2_g == 0 or vehicle_status1 == 35 and vehicle_status2_g == 6 or vehicle_status1 == 37 and vehicle_status2_g == 6:
            mm1.digital_output_led_red1()
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
            
        if vehicle_status1 == 37 and vehicle_status2_g == 35 or vehicle_status1 == 35 and vehicle_status2_g == 37 or vehicle_status1 == 35 and vehicle_status2_g == 35 or vehicle_status1 == 37 and vehicle_status2_g == 35:
            mm1.digital_output_led_red1()
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_2)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)

            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
           

        if vehicle_status1 == 37 and vehicle_status2_g == 2 or vehicle_status1 == 37 and vehicle_status2_g == 13 or vehicle_status1 == 37 and vehicle_status2_g == 21 or vehicle_status1 == 37 and vehicle_status2_g == 29:
            mm1.digital_output_led_red1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (pm_assign1 == 1):
                mm.stopModule(CanId.CAN_ID_1)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)

            elif (pm_assign1 == 2):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
            
            elif (pm_assign1 == 3):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
            PECC.STATUS1_GUN1_DATA[0] = 1

        if vehicle_status1 == 35 and vehicle_status2_g == 2 or vehicle_status1 == 35 and vehicle_status2_g == 13 or vehicle_status1 == 35 and vehicle_status2_g == 21 or vehicle_status1 == 35 and vehicle_status2_g == 29:
            mm1.digital_output_led_red1()
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (pm_assign1 == 1):
                mm.stopModule(CanId.CAN_ID_1)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)

            elif (pm_assign1 == 2):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
            
            elif (pm_assign1 == 3):
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
            PECC.STATUS1_GUN1_DATA[0] = 1
           
          