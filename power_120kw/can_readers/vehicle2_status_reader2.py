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

    def getRealTimeVIP(self):
        s2g2d = bytetobinary(PECC.STATUS2_GUN2_DATA)
        voltage_pre = binaryToDecimal(int(s2g2d[1] + s2g2d[0]))
        self._voltage = (voltage_pre / 10)
        current_pre = binaryToDecimal(int(s2g2d[3] + s2g2d[2]))
        self._current = (current_pre / 10)

        self._readPower = int(self._voltage * self._current)
        #print(f"Real-time G2: Voltage: {self._voltage}V, Current: {self._current}A, Power: {self._readPower}W  || Target Power: {self._global_data.get_data_targetpower_ev2()}W")
        #print(f"p2= {self._readPower}, v2= {self._voltage}, c2={self._current}")
        return self._readPower, self._voltage, self._current

    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        vs2 = self._binary_data
        self._global_data.set_data_status_vehicle2(binaryToDecimal(int(vs2[0])))
        vehicle_status2 = binaryToDecimal(int(vs2[0]))
        #print("s2=",vehicle_status2)
        # logger.info(f'Vehicle-2 status {vehicle_status2}')
        vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        #logger.info(f'Vehicle-1 status {vehicle_status1_g}')

        tag_vol2 = binaryToDecimal(int(vs2[2] + vs2[1]))
        target_volatge_from_car2 = (tag_vol2 / 10)

        tag_curr2 = binaryToDecimal(int(vs2[4] + vs2[3]))
        tag_curr22 = (tag_curr2 / 10)
        target_current_from_car2 = (tag_curr22)
        target_power2 = int(target_volatge_from_car2 * tag_curr22)
        self._global_data.set_data_targetpower_ev2(target_power2)

        maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
        maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
        self.getRealTimeVIP()
        def funct_30_cc2():
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

            if cable_check_voltage2 <= 500:
                mm.lowMode(CanId.CAN_ID_2)
            if cable_check_voltage2 > 500:
                mm.highMode(CanId.CAN_ID_2)

            mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
            mm.startModule(CanId.CAN_ID_2)
            mm.readModule_Voltage(CanId.CAN_ID_2)
            digitl_input = self._global_data.get_data()
            

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN2_DATA[0] = 3
        def funct_30_2():      

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
          

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN2_DATA[0] = 3

        def funct_60_2():  
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
           

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                PECC.STATUS1_GUN2_DATA[0] = 3

        def funct_90_2():
            
            
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
            mm.readModule_Current(CanId.CAN_ID_4)
            mm.readModule_Current(CanId.CAN_ID_3)
            digitl_input = self._global_data.get_data()
 

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                PECC.STATUS1_GUN2_DATA[0] = 3


        if vehicle_status2 == 0 and vehicle_status1_g == 0 or vehicle_status2 == 6 and vehicle_status1_g == 6 or vehicle_status2 == 6 and vehicle_status1_g == 0:
            mm.digital_output_open_AC()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1'  :
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 2
                else:
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 0
            else:
                mm2.digital_output_led_red2()
                PECC.STATUS1_GUN2_DATA[0] = 0   

        if vehicle_status2 == 0 and vehicle_status1_g == 6 or vehicle_status2 == 0 and vehicle_status1_g == 2 or vehicle_status2 == 0 and vehicle_status1_g == 29:
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1'  :
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 2
                else:
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 0
            else:
                mm2.digital_output_led_red2()
                PECC.STATUS1_GUN2_DATA[0] = 0              

        if vehicle_status2 == 2 and vehicle_status1_g == 0 or vehicle_status2 == 2 and vehicle_status1_g == 6 :
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9      
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)    
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                PECC.STATUS1_GUN2_DATA[0] = 2
            
            else:
                mm2.digital_output_led_red2()
                mm.digital_output_close_AC()
                PECC.STATUS1_GUN2_DATA[0] = 0 

        if vehicle_status2 == 2 and vehicle_status1_g != 0 or vehicle_status2 == 2 and vehicle_status1_g != 6:
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()        
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9      
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)    
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                PECC.STATUS1_GUN2_DATA[0] = 2
            
            else:
                mm2.digital_output_led_red2()
        
                PECC.STATUS1_GUN2_DATA[0] = 0

        if vehicle_status2 == 13 and vehicle_status1_g == 0 or vehicle_status2 == 13 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            mm2.digital_output_led_red2()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            mm2.digital_output_close_Gun21()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

            if cable_check_voltage2 <= 500:
                mm.lowMode(CanId.CAN_ID_2)
            if cable_check_voltage2 > 500:
                mm.highMode(CanId.CAN_ID_2)

            mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
            mm.startModule(CanId.CAN_ID_2)
            mm.readModule_Voltage(CanId.CAN_ID_2)
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (cable_check_voltage2-10):
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
                mm.stopModule(CanId.CAN_ID_2)

            
        if vehicle_status2 == 13 and vehicle_status1_g == 2 or vehicle_status2 == 13 and vehicle_status1_g == 35 or vehicle_status2 == 13 and vehicle_status1_g == 37:
            mm2.digital_output_led_red2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            mm2.digital_output_Gun2_load11()
            funct_30_cc2()
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (cable_check_voltage2-10):
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()
                    

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5
                mm.stopModule(CanId.CAN_ID_2)


        if vehicle_status2 == 13 and vehicle_status1_g == 13 or vehicle_status2 == 13 and vehicle_status1_g == 21 or vehicle_status2 == 13 and vehicle_status1_g == 29:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            PECC.STATUS1_GUN2_DATA[0] = 1
            mm2.digital_output_led_red2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            mm2.digital_output_load21()
            funct_30_cc2()
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (cable_check_voltage2-10):
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5
                mm.stopModule(CanId.CAN_ID_2)

        if vehicle_status2 == 21 and vehicle_status1_g == 0 or vehicle_status2 == 21 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.startModule(CanId.CAN_ID_2)
            mm2.digital_output_led_red2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
            mm2.digital_output_close_Gun21()
            funct_30_2()

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

                
                

        if vehicle_status2 == 21 and vehicle_status1_g == 2 or vehicle_status2 == 21 and vehicle_status1_g == 35 or vehicle_status2 == 21 and vehicle_status1_g == 37:
            mm2.digital_output_led_red2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.startModule(CanId.CAN_ID_2)
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()

            
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            mm2.digital_output_Gun2_load11()
            funct_30_2()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5
                
            
                
        if vehicle_status2 == 21 and vehicle_status1_g == 13 or vehicle_status2 == 21 and vehicle_status1_g == 21 or vehicle_status2 == 21 and vehicle_status1_g == 29:
            mm2.digital_output_led_red2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.startModule(CanId.CAN_ID_2)
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
            mm2.digital_output_load21()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            funct_30_2()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5

        if vehicle_status2 == 29 and vehicle_status1_g == 0 or vehicle_status2 == 29 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.readModule_Voltage(CanId.CAN_ID_2)
            mm2.digital_output_led_green2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            #self._global_data.set_data_maxpower2(maxpowerev2_g)
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (target_volatge_from_car2-150):

                if target_power_from_car2 <= 28000:
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                    mm2.digital_output_close_Gun21()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    pm2=1
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_30_2()

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
                    
                if target_power_from_car2 > 28000 and target_power_from_car2 < 32000:
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                    if (pm_assign2 == 1):
                        mm2.digital_output_close_Gun21()
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)
                        funct_30_2()
                    elif (pm_assign2 == 2):
                        mm2.digital_output_close_Gun22()
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        funct_60_2()
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
                    
                if target_power_from_car2 >= 32000 and target_power_from_car2 <= 58000:
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                    mm2.digital_output_close_Gun22()    # Closing contactors for 2 modules for Gun2
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    pm2=2
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_60_2()
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

                if target_power_from_car2 > 58000 and target_power_from_car2 < 62000:
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 2):
                        mm2.digital_output_close_Gun22()
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        funct_60_2()
                    elif (pm_assign2 == 3):
                        mm2.digital_output_close_Gun23()
                        mm.stopModule(CanId.CAN_ID_1)
                        funct_90_2()
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
                    
                if target_power_from_car2 >= 62000 and target_power_from_car2 <= 88000:
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    pm2=3
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_90_2()
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
                    
                if target_power_from_car2 > 88000 and target_power_from_car2 < 92000:
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 3):
                        mm2.digital_output_close_Gun23()
                        mm.stopModule(CanId.CAN_ID_1)
                        funct_90_2()
                    elif (pm_assign2 == 4):
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
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm.digital_output_open_stop()
                        time.sleep(5)
                        mm.digital_output_open_fan()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                    if digitl_input[1] == '0' or digitl_input[2] == '1' :
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3

                if target_power_from_car2 >= 92000:  
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9      
                    mm2.digital_output_close_Gun24()
                    pm2=4
                    self._global_data.set_data_pm_assign2(pm2)
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

                    if digitl_input[1] == '0' or digitl_input[2] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_2)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)
                        PECC.STATUS1_GUN2_DATA[0] = 3
                    

        if vehicle_status2 == 29 and vehicle_status1_g == 2 or vehicle_status2 == 29 and vehicle_status1_g == 35 or vehicle_status2 == 29 and vehicle_status1_g == 37:
        
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.readModule_Voltage(CanId.CAN_ID_2)
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (target_volatge_from_car2-150):
                if (target_power_from_car2 <= 28000):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                    pm2=1
                    self._global_data.set_data_pm_assign2(pm2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm2.digital_output_Gun2_load11()
                    funct_30_2()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load21()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5
                    
                if 28000 < target_power_from_car2 < 32000 :
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 1):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm.stopModule(CanId.CAN_ID_4)
                        mm2.digital_output_Gun2_load11()
                        funct_30_2()
                        digitl_input = self._global_data.get_data()
                        if digitl_input[4] == '1':
                            mm2.digital_output_led_red2()
                            mm.stopcharging(CanId.STOP_GUN2)
                            mm.stopModule(CanId.CAN_ID_2)              
                            PECC.STATUS1_GUN2_DATA[0] = 9
                            mm2.digital_output_open_load21()

                        if digitl_input[4] == '0':
                            PECC.STATUS1_GUN2_DATA[0] = 5
                    elif(pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm2.digital_output_Gun2_load12()
                        funct_60_2()
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
                if (32000 <= target_power_from_car2 <= 58000):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                    pm2=2
                    self._global_data.set_data_pm_assign2(pm2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    funct_60_2()
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

                if (58000 < target_power_from_car2 < 62000 and pm_assign1 == 1) or (58000 < target_power_from_car2 < 62000 and pm_assign1 == 0):
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm2.digital_output_Gun2_load12()
                        funct_60_2()  
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
                    elif (pm_assign2 == 3):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                        
                        mm.stopModule(CanId.CAN_ID_1)
                        mm2.digital_output_Gun2_load13()
                        funct_90_2()
                        digitl_input = self._global_data.get_data()
                        if digitl_input[4] == '1':
                            mm2.digital_output_led_red2()
                            mm.stopcharging(CanId.STOP_GUN2)
                            mm.stopModule(CanId.CAN_ID_2)  
                            mm.stopModule(CanId.CAN_ID_4)  
                            mm.stopModule(CanId.CAN_ID_3)             
                            PECC.STATUS1_GUN2_DATA[0] = 9
                            mm2.digital_output_open_load23()

                        if digitl_input[4] == '0':
                            PECC.STATUS1_GUN2_DATA[0] = 5 

                if (58000 < target_power_from_car2 < 62000 and pm_assign1 == 2) or (58000 < target_power_from_car2 < 62000 and pm_assign1 == 3):
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm2.digital_output_Gun2_load12()
                        funct_60_2() 
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
                    elif(pm_assign2 == 3):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm.stopModule(CanId.CAN_ID_1)
                        mm.stopModule(CanId.CAN_ID_3)
                        mm2.digital_output_Gun2_load12()
                        funct_60_2()
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

                if (target_power_from_car2 >= 62000 and pm_assign1 == 0) or (target_power_from_car2 >= 62000 and pm_assign1 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    pm2=3
                    self._global_data.set_data_pm_assign2(pm2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm2.digital_output_Gun2_load13()
                    funct_90_2()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)  
                        mm.stopModule(CanId.CAN_ID_4)  
                        mm.stopModule(CanId.CAN_ID_3)             
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load23()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                if (target_power_from_car2 >= 62000 and pm_assign1 == 2) or (target_power_from_car2 >= 62000 and pm_assign1 == 3):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                
                    pm2=2
                    self._global_data.set_data_pm_assign2(pm2)
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    funct_60_2()
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
                

        if vehicle_status2 == 29 and vehicle_status1_g == 13 or vehicle_status2 == 29 and vehicle_status1_g == 21 or vehicle_status2 == 29 and vehicle_status1_g == 29:
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm.readModule_Voltage(CanId.CAN_ID_2)
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            realtime_data2 = self.getRealTimeVIP()
            #print(f"V2: {realtime_data2[1]}, CCV2: {cable_check_voltage2}")
            if realtime_data2[1] >= (target_volatge_from_car2-150):
                if (target_power_from_car2 <= 28000 and pm_assign1 == 1) or (target_power_from_car2 <= 28000 and pm_assign1 == 2) :
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                    mm2.digital_output_load21()
                    mm.stopModule(CanId.CAN_ID_4)
                    pm2=1
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_30_2()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load21()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5
                if (target_power_from_car2 <= 28000 and pm_assign1 == 3) :
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 184
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 11
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 232
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 3
                    mm2.digital_output_load21()
                    pm2=1
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_30_2()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load21()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                if 28000 < target_power_from_car2 < 32000 :
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 1):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm2.digital_output_load21()
                        funct_30_2()
                        digitl_input = self._global_data.get_data()
                        if digitl_input[4] == '1':
                            mm2.digital_output_led_red2()
                            mm.stopcharging(CanId.STOP_GUN2)
                            mm.stopModule(CanId.CAN_ID_2)                
                            PECC.STATUS1_GUN2_DATA[0] = 9
                            mm2.digital_output_open_load21()

                        if digitl_input[4] == '0':
                            PECC.STATUS1_GUN2_DATA[0] = 5
                    elif(pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm2.digital_output_load22()
                        funct_60_2()
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

                if (32000 <= target_power_from_car2 <= 58000 and pm_assign1 ==1) or (32000 <= target_power_from_car2 <= 58000 and pm_assign1 ==2) or (32000 <= target_power_from_car2 <= 58000 and pm_assign1 ==3):
                    pm2=2
                    self._global_data.set_data_pm_assign2(pm2)
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                    mm2.digital_output_load22()
                    funct_60_2()
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

                if (58000 < target_power_from_car2 < 62000 and pm_assign1 == 1) or (58000 < target_power_from_car2 < 62000 and target_power_from_car1 <= 28000) :
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                        mm2.digital_output_load22()
                        funct_60_2()
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
                    elif(pm_assign2 == 3):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                        mm2.digital_output_load23()
                        funct_90_2()

                        digitl_input = self._global_data.get_data()
                        if digitl_input[4] == '1':
                            mm2.digital_output_led_red2()
                            mm.stopcharging(CanId.STOP_GUN2)
                            mm.stopModule(CanId.CAN_ID_2) 
                            mm.stopModule(CanId.CAN_ID_4)
                            mm.stopModule(CanId.CAN_ID_3)               
                            PECC.STATUS1_GUN2_DATA[0] = 9
                            mm2.digital_output_open_load23()

                        if digitl_input[4] == '0':
                            PECC.STATUS1_GUN2_DATA[0] = 5

                if (58000 < target_power_from_car2 < 62000 and pm_assign1== 2) or (58000 < target_power_from_car2 < 62000 and pm_assign1 == 3):
                    pm_assign2 = self._global_data.get_data_pm_assign2()
                    if (pm_assign2 == 2):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm2.digital_output_load22()
                        funct_60_2()
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
                    elif(pm_assign2 == 3):
                        PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                        PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                        PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                        PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                        mm2.digital_output_load22()
                        funct_60_2()
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
                        
            
                if (target_power_from_car2 >= 62000 and target_power_from_car1 <= 28000) or (target_power_from_car2 >= 62000 and pm_assign1 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 40
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 35
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    pm2=3
                    self._global_data.set_data_pm_assign2(pm2)
                    mm2.digital_output_load23()
                    funct_90_2()
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2) 
                        mm.stopModule(CanId.CAN_ID_4)
                        mm.stopModule(CanId.CAN_ID_3)               
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load23()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                if (target_power_from_car2 >= 62000 and pm_assign1 == 2) or (target_power_from_car2 >= 62000 and pm_assign1 == 3) or (target_power_from_car2 >= 62000 and target_power_from_car1 > 32000) :
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 112
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 23
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 208
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 7
                    mm2.digital_output_load22()
                    pm2=2
                    self._global_data.set_data_pm_assign2(pm2)
                    funct_60_2()
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
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (pm_assign2 == 1):
                mm.stopModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
            elif (pm_assign2 == 2):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
            
            elif (pm_assign2 == 3):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                mm.readModule_Current(CanId.CAN_ID_3)
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
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if (pm_assign2 == 1):
                mm.stopModule(CanId.CAN_ID_2)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
            elif (pm_assign2 == 2):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
            
            elif (pm_assign2 == 3):
                mm.stopModule(CanId.CAN_ID_2)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
                mm.readModule_Current(CanId.CAN_ID_3)
            PECC.STATUS1_GUN2_DATA[0] = 1
          
