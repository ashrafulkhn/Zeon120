import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module2Message as mm2, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH
from pecc_frame_setter import PECCFrameSetter as setter

#logger = logging.getLogger(__name__)

class Vehicle2StatusReader(BaseReader):
    arbitration_id = 1537

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self.limitChangeRequested = False

     #  Return the real-time voltage, current and power
    def getRealTimeVIP(self):
        s2g2d = bytetobinary(PECC.STATUS2_GUN2_DATA)

        voltage_pre = binaryToDecimal(int(s2g2d[1] + s2g2d[0]))
        self._voltage = (voltage_pre / 10)

        current_pre = binaryToDecimal(int(s2g2d[3] + s2g2d[2]))
        self._current = (current_pre / 10)

        self._readPower = int(self._voltage * self._current)
        # print(f"Real-time G2: Voltage: {self._voltage}V, Current: {self._current}A, Power: {self._readPower}W  || Target Power: {self._global_data.get_data_targetpower_ev2()}W")
        return self._readPower, self._voltage, self._current

    def limitChangeRequest(self, limitPower):
        """
        Case 1: Demand = 34kW -> Limit = 35kW -> readPower = 20kW -> Difference = 15kW
        Case 2: Demand = 38kW -> Limit = 35kW -> readPower = 33kW -> Difference = 2kW
        Case 3: Demand = 38kW -> Limit = 35kW -> readPower = 55kW -> Difference = abs(-20kW) = 20kW
        This means switch power only when the difference is more than 2kW both positive and negative way. If there is a drastic change in power, then we will not switch the power.
        """
        print("INFO:: Indside Limit Change Function Gun1")
        realTimeVIP = self.getRealTimeVIP()
        # print(f"Limit Power: {limitPower}")
        val = abs(limitPower - realTimeVIP[0])    # 35 - 34 = 1; 35 - 36 = -1
        # print(f"Comparision value: Limit Power: {limitPower}, Read Power: {self._readPower}, Difference Value: {val}")
        if val <= 2000:  # 2kW
            self.limitChangeRequested = True
        else:
            self.limitChangeRequested = False

        print(f"Gun2 :: LP: {limitPower}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev2()}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")

    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        vs2 = self._binary_data
        self._global_data.set_data_status_vehicle2(binaryToDecimal(int(vs2[0])))
        vehicle_status2 = binaryToDecimal(int(vs2[0]))
        #print("s2=",vehicle_status2)
        # logger.info(f'Vehicle-2 status {vehicle_status2}')
        vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        #logger.info(f'Vehicle-1 status {vehicle_status1_g}')

        self.getRealTimeVIP()

        tag_vol2 = binaryToDecimal(int(vs2[2] + vs2[1]))
        target_volatge_from_car2 = (tag_vol2 / 10)

        tag_curr2 = binaryToDecimal(int(vs2[4] + vs2[3]))
        tag_curr22 = (tag_curr2 / 10)
        target_current_from_car2 = (tag_curr22)

        target_power2 = int(target_volatge_from_car2 * tag_curr22)
        self._global_data.set_data_targetpower_ev2(target_power2)

        def cableCheck():
            print("GUN2: Cable Check")
            cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

            if cable_check_voltage2 <= 500:
                mm.lowMode(CanId.CAN_ID_2)
            if cable_check_voltage2 > 500:
                mm.highMode(CanId.CAN_ID_2)

            mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
            mm.startModule(CanId.CAN_ID_2)
            mm.readModule_Voltage(CanId.CAN_ID_2)
            digitl_input = self._global_data.get_data()
            
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN2_DATA[0] = 3

        def handleError(module_ids):
            """"
            Check the digital input from the VSECC.
            Digital input 1: Emergency Button Status, 0 is Active
            Digital input 2: SPD Status/ELR Status, 1 is active
            Digital input 7: 3 Phase Monitoring Device Status, 0 is active
            If any of the above digital input is Active, then stop the charging and turn on the red LED.
            """
            # Handle error conditions here

            # Check the digital input from the VSECC.
            # mm2.digital_output_led_red1()
            mm2.digital_output_led_red2()
            mm.stopcharging(CanId.STOP_GUN2)
            for module_id in module_ids:
                mm.stopModule(module_id)

            PECC.STATUS1_GUN2_DATA[0] = 3

        def standByled():
            """
            
            """
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' or  digitl_input[7] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 2
                    mm2.digital_output_led_red2()
                else:
                    PECC.STATUS1_GUN2_DATA[0] = 0
                    mm2.digital_output_led_green2()
            else:
                PECC.STATUS1_GUN2_DATA[0] = 0
                mm2.digital_output_led_green2()

        def updateVI_status(vs2):
            """
            Update the VI status of the vehicle
            vs2: Vehicle status
            """
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            
        def startCharging(module_ids):
            """
            Call the startCharging function to start the charging process
            modue_ids: List of module IDs to be started
            Example:
            module_ids = [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
            """
            # for module_id in module_ids:
            #     mm.startModule(module_id)
            #     mm.readModule_Voltage(module_id)
            #     mm.readModule_Current(module_id)

            if target_volatge_from_car2 <= 500:
                for module_id in module_ids:
                    mm.lowMode(module_id)

            elif target_volatge_from_car2 > 500:
                for module_id in module_ids:
                    mm.highMode(module_id)

            RUNNING_CURRENT = (target_current_from_car2/len(module_ids))
            self._global_data.set_data_running_current(RUNNING_CURRENT)
            for module_id in module_ids:
                mm.setVoltage(DTH.convertohex(target_volatge_from_car2), module_id)
                mm.setCurrent(module_id)
                mm.startModule(module_id)
                mm.readModule_Current(module_id)

            mm.readModule_Voltage(module_ids[0])  # Read and update the voltage of the first module

            # Handle error conditions here
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0' :
                handleError(module_ids)

        def stopActiveModules(module_ids):
            for module_id in module_ids:
                mm.stopModule(module_id)

        # GUN2:: Condition 1
        if  vehicle_status2 == 0 and vehicle_status1_g == 0 or \
            vehicle_status2 == 6 and vehicle_status1_g == 6 or \
            vehicle_status2 == 6 and vehicle_status1_g == 0:
            print("GUN2:: Condition 1")
            mm.digital_output_open_AC()
            setter.setModulesLimit(120000, 250, 2)

            pm2=[]
            self._global_data.set_data_pm_assign2(len(pm2))
            digitl_input = self._global_data.get_data()
            standByled()
        
        # GUN2:: Condition 2
        if  vehicle_status2 == 0 and vehicle_status1_g == 6 or \
            vehicle_status2 == 0 and vehicle_status1_g == 2 or \
            vehicle_status2 == 0 and vehicle_status1_g == 29:
            print("GUN2:: Condition 2")
            setter.setModulesLimit(120000, 250, gun_number=2)

            pm2=[]
            self._global_data.set_data_pm_assign2(len(pm2))
            digitl_input = self._global_data.get_data()             
            standByled()
        
        # GUN2:: Condition 3
        if  vehicle_status2 == 2 and vehicle_status1_g == 0 or \
            vehicle_status2 == 2 and vehicle_status1_g == 6 :
            print("GUN2:: Condition 3")
            setter.setModulesLimit(120000, 250, gun_number=2) 

            pm2=[]
            self._global_data.set_data_pm_assign2(len(pm2))   
            digitl_input = self._global_data.get_data()
            try:
                if len(digitl_input) != 0 :
                    if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        PECC.STATUS1_GUN2_DATA[0] = 2
                
                    else:
                        mm2.digital_output_led_green2()
                        mm.digital_output_close_AC()
                        PECC.STATUS1_GUN2_DATA[0] = 0 
                else:
                    mm2.digital_output_led_green2()
                    mm.digital_output_close_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 0 
            except IndexError:
                print("GUN2: IndexError: List index out of range. Please check the input data.")
        
        # GUN2:: Condition 4
        if  vehicle_status2 == 2 and vehicle_status1_g == 13 or \
            vehicle_status2 == 2 and vehicle_status1_g == 21 or \
            vehicle_status2 == 2 and vehicle_status1_g == 29:
            print("GUN2:: Condition 4")

            setter.setModulesLimit(120000, 250, gun_number=2)
            mm2.digital_output_led_green2()
            PECC.STATUS1_GUN2_DATA[0] = 0   
            pm2=[]
            self._global_data.set_data_pm_assign2(len(pm2))    
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                PECC.STATUS1_GUN2_DATA[0] = 2
        
        # GUN2:: Condition 5
        if  vehicle_status2 == 13 and vehicle_status1_g == 0 or \
            vehicle_status2 == 13 and vehicle_status1_g == 6:
            print("GUN2:: Condition 5")
            setter.setModulesLimit(120000, 250, gun_number=2)
            updateVI_status(vs2=vs2)
            PECC.STATUS1_GUN2_DATA[0] = 1

            mm2.digital_output_led_green2()
            
            mm2.digital_output_close_Gun21()

            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            
            cableCheck()

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
        
        # GUN2:: Condition 6
        if  vehicle_status2 == 13 and vehicle_status1_g == 2 or \
            vehicle_status2 == 13 and vehicle_status1_g == 35 or \
            vehicle_status2 == 13 and vehicle_status1_g == 37:
            print("GUN2:: Condition 6")

            updateVI_status(vs2)
            PECC.STATUS1_GUN2_DATA[0] = 1
            
            mm2.digital_output_led_green2()
            mm2.digital_output_Gun2_load11()

            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            stopActiveModules([CanId.CAN_ID_1,
                               CanId.CAN_ID_3,
                               CanId.CAN_ID_4])
            
            cableCheck()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()
            
            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5
            
        # GUN2:: Condition 7
        if  vehicle_status2 == 13 and vehicle_status1_g == 13 or \
            vehicle_status2 == 13 and vehicle_status1_g == 21 or \
            vehicle_status2 == 13 and vehicle_status1_g == 29:
            print("GUN2:: Condition 7")
            updateVI_status(vs2)
            PECC.STATUS1_GUN2_DATA[0] = 1
            mm2.digital_output_led_green2()
            mm2.digital_output_load21()
            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            
            cableCheck()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5

        # Condition 8
        if  vehicle_status2 == 21 and vehicle_status1_g == 0 or \
            vehicle_status2 == 21 and vehicle_status1_g == 6:
            print("GUN2:: Condition 8")
            updateVI_status(vs2)
            setter.setModulesLimit(30000, 100, gun_number=2)
            mm2.digital_output_led_green2()
            mm2.digital_output_close_Gun21()
            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            startCharging(pm2)

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

        # GUN2:: Condition 9
        if  vehicle_status2 == 21 and vehicle_status1_g == 2 or \
            vehicle_status2 == 21 and vehicle_status1_g == 35 or \
            vehicle_status2 == 21 and vehicle_status1_g == 37:
            print("GUN2:: Condition 9")
            updateVI_status(vs2)
            
            mm2.digital_output_led_green2()
                       
            setter.setModulesLimit(30000, 100, 2)
            mm2.digital_output_Gun2_load11()
            stopActiveModules([CanId.CAN_ID_1,
                                CanId.CAN_ID_3,
                                CanId.CAN_ID_4])

            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            startCharging(pm2)

            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5
                    # GUN2:: Condition 1   
        
        # GUN2:: Condition 10
        if  vehicle_status2 == 21 and vehicle_status1_g == 13 or \
            vehicle_status2 == 21 and vehicle_status1_g == 21 or \
            vehicle_status2 == 21 and vehicle_status1_g == 29:
            print("GUN2:: Condition 10")
            updateVI_status(vs2)
            mm2.digital_output_led_green2()
            setter.setModulesLimit(30000, 100, 2)
            mm2.digital_output_load21()

            pm2=[CanId.CAN_ID_2]
            self._global_data.set_data_pm_assign2(len(pm2))
            startCharging(pm2)

            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5

# ============================================================================================
# ============================================================================================
# ============================================================================================

        # GUN2:: Conditions 11
        if  vehicle_status2 == 29 and vehicle_status1_g == 0 or \
            vehicle_status2 == 29 and vehicle_status1_g == 6:
            print("GUN2:: Condition 11")
            updateVI_status(vs2)
            
            mm2.digital_output_led_blue2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()

            # Demand Condition 1
            # if target_power_from_car1 <= 38000:
            if target_power_from_car2 <= 28000:
                setter.setModulesLimit(25000, 100, gun_number=2)
                # Assign modules for Gun1
                pm2=[CanId.CAN_ID_2]
                self._global_data.set_data_pm_assign2(len(pm2))

                mm2.digital_output_close_Gun21()
                stopActiveModules([CanId.CAN_ID_1,
                                CanId.CAN_ID_4,
                                CanId.CAN_ID_3])

                # Check the realtime votage and current
                
                self.limitChangeRequest(25000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    # print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    startCharging(pm2)

                else:
                    if self._global_data.get_data_targetpower_ev2() == 0:
                        stopActiveModules([CanId.CAN_ID_2])
                    else:
                        setter.setModulesLimit(55000, 200, gun_number=2)
                        self.limitChangeRequested = False
                        # print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()

                # IMD Status Check
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)
                    # mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm2.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 2
            if  target_power_from_car2 > 28000 and \
                target_power_from_car2 < 32000:
                
                pm_assign2 = self._global_data.get_data_pm_assign2()
                #Setting limit to 55kW
                setter.setModulesLimit(55000, 200, gun_number=2)
                if (pm_assign2 == 1):
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    mm2.digital_output_close_Gun21()
                    startCharging([CanId.CAN_ID_2])
                elif (pm_assign2 == 2):
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

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

            # Demand Condition 3
            if  target_power_from_car2 >= 32000 and \
                target_power_from_car2 <= 58000:
                setter.setModulesLimit(55000, 200, gun_number=2)
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                stopActiveModules([CanId.CAN_ID_1,CanId.CAN_ID_3])
                self.limitChangeRequest(55000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    mm2.digital_output_close_Gun22()
                    startCharging(pm2)
                else:
                    setter.setModulesLimit(85000, 250, gun_number=2)
                    self.limitChangeRequested = False
                    # print(f"INFO: Limit changed to 75kW.")

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
            
            # Demand Condition 4
            if  target_power_from_car2 > 58000 and \
                target_power_from_car2 < 62000:
            # if target_power_from_car1 > 78000 and target_power_from_car1 < 82000:
                pm_assign2 = self._global_data.get_data_pm_assign2()
                setter.setModulesLimit(85000, 250, gun_number=2)
                
                if ((pm_assign2) == 2):
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_close_Gun22()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                elif ((pm_assign2) == 3):
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm2.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5
            
            # Demand Condition 5
            if  target_power_from_car2 >= 62000 and \
                target_power_from_car2 <= 88000:
                setter.setModulesLimit(85000, 250, gun_number=2)

                mm.stopModule(CanId.CAN_ID_1)
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))

                self.limitChangeRequest(85000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    mm2.digital_output_close_Gun23()
                    startCharging(pm2)
                else:
                    setter.setModulesLimit(120000, 250, gun_number=2)
                    self.limitChangeRequested = False
                    # print(f"INFO: Limit changed to 120kW.")

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()
                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 6
            if  target_power_from_car2 > 88000 and \
                target_power_from_car2 < 92000:

                pm_assign2 = self._global_data.get_data_pm_assign2()
                setter.setModulesLimit(120000, 250, gun_number=2)
                if (pm_assign2 == 3):
                    mm.stopModule(CanId.CAN_ID_1)
                    mm2.digital_output_close_Gun23()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                elif ((pm_assign2) == 4):
                    mm2.digital_output_close_Gun24()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm2.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
            
            # Demand Condition 7
            if target_power_from_car2 >= 92000:
                mm2.digital_output_close_Gun24()
                setter.setModulesLimit(120000, 250, gun_number=2)
                pm2=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                
                self._global_data.set_data_pm_assign2(len(pm2))
                
                startCharging(pm2)

                val = 120000 - self._global_data.get_data_targetpower_ev2()   # This val is not used anywhere. It is just for printing. Comment this line if you are not printing anything.

                print(f"Gun2 :: LP: {120000}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev2()}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")
                
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

        # GUN2:: Condition 12
        if  vehicle_status2 == 29 and vehicle_status1_g == 2 or   \
            vehicle_status2 == 29 and vehicle_status1_g == 35 or \
            vehicle_status2 == 29 and vehicle_status1_g == 37:
            print("GUN2:: Condition 12")
            updateVI_status(vs2)
            mm2.digital_output_led_blue2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1() # Number of modules assigned to Gun 2

            # Demand Condition 1
            if (target_power_from_car2 <= 28000) :
                setter.setModulesLimit(30000, 100, gun_number=2)
                
                pm2=[CanId.CAN_ID_2]
                self._global_data.set_data_pm_assign2(len(pm2))
                mm2.digital_output_Gun2_load11()

                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_4, CanId.CAN_ID_3])
                startCharging(pm2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 

            # Demand Condtition 2
            if (28000 < target_power_from_car2 <= 32000) :
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 1):

                    # Setting demand to 30kW
                    # Power in decimal -> 80000/10 -> 8000 -> Convert to Hex -> Update Lower byte to [4], Upper byte to [5]
                    # Current conversion -> Current Value in decimal -> 250*10 -> Convert to Hex -> Update Lower byte to [2], Upper byte to [3]

                    setter.setModulesLimit(60000, 200, gun_number=2)
                    mm2.digital_output_Gun2_load11()
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_4, CanId.CAN_ID_3])
                    startCharging([CanId.CAN_ID_2])
                    
                    # IMD Check conditions
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load21()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                elif((pm_assign2) == 2):
                    # Setting limit to 60kW
                    setter.setModulesLimit(60000, 200, gun_number=2)

                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    mm2.digital_output_Gun2_load12()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            #Demand Condition 3
            if (32000 < target_power_from_car2 <= 58000):
                setter.setModulesLimit(60000, 200, gun_number=2)
                # pm1=2
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))

                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                mm2.digital_output_Gun2_load12()
                # funct_80_1() 
                startCharging(pm2)
                digitl_input = self._global_data.get_data()

                # IMD Check
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)

                    stopActiveModules(pm2)            
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 

            # Demand Condition 4
            if  (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 1) or \
                (58000 < target_power_from_car2 <= 62000 and target_power_from_car1 <= 28000):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    setter.setModulesLimit(90000, 250, gun_number=2)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    mm2.digital_output_Gun2_load12()
                    # funct_80_1()  
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

                if ((pm_assign2) == 3):
                    setter.setModulesLimit(90000, 250, gun_number=2)
                    
                    mm.stopModule(CanId.CAN_ID_1)
                    mm2.digital_output_Gun2_load13()
                    # funct_120_1()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

                    #Imd check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])             
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load23()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 5
            if  (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 2) or \
                (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 3):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if ((pm_assign2) == 2):
                    setter.setModulesLimit(60000, 200, gun_number=2)

                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    mm2.digital_output_Gun2_load12()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])            
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5 
                elif((pm_assign2) == 3):
                    setter.setModulesLimit(60000, 200, gun_number=2)

                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    mm2.digital_output_Gun2_load12()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 6
            if  (target_power_from_car2 > 62000 and pm_assign1 == 1) or \
                (target_power_from_car2 > 62000 and target_power_from_car1 <= 28000):
                setter.setModulesLimit(90000, 250, gun_number=2)
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                mm.stopModule(CanId.CAN_ID_1)
                mm2.digital_output_Gun2_load13()
                startCharging(pm2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)              
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 7
            if  (target_power_from_car2 > 62000 and pm_assign1 == 2) or \
                (target_power_from_car2 > 62000 and pm_assign1 == 3):
                setter.setModulesLimit(60000, 200, gun_number=2)

                # pm1=2
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                mm2.digital_output_Gun2_load12()
                # funct_80_1()
                startCharging(pm2)

                #IMD check
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)       
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 
        
        # GUN2:: Condition 13
        if  vehicle_status2 == 29 and vehicle_status1_g == 13 or \
            vehicle_status2 == 29 and vehicle_status1_g == 21 or \
            vehicle_status2 == 29 and vehicle_status1_g == 29:
            print("GUN2:: Condition 13")
            updateVI_status(vs2)
            mm2.digital_output_led_blue2()

            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            
            # Demand Condition 1
            if  (target_power_from_car2 <= 28000 and pm_assign1 == 1) or \
                (target_power_from_car2 <= 28000 and pm_assign1 == 2) :
                setter.setModulesLimit(30000, 100, gun_number=2)
                mm2.digital_output_load21()
                mm.stopModule(CanId.CAN_ID_4)
                # pm1=1
                pm2=[CanId.CAN_ID_2]
                self._global_data.set_data_pm_assign2(len(pm2))
                # funct_40_1()
                startCharging(pm2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)               
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 
            
            # Demand Condition 2
            if (target_power_from_car2 <= 28000 and pm_assign1 == 3):
                setter.setModulesLimit(30000, 100, gun_number=2)
                mm2.digital_output_load21()
                # pm1=1
                pm2=[CanId.CAN_ID_2]
                self._global_data.set_data_pm_assign2(len(pm2))
                # funct_40_1()
                startCharging(pm2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand Condition 3
            if 28000 < target_power_from_car2 <= 32000 :
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if ((pm_assign2) == 1):
                    setter.setModulesLimit(60000, 200, gun_number=2)
                    mm2.digital_output_load21()
                    startCharging([CanId.CAN_ID_2])
                    digitl_input = self._global_data.get_data()

                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        mm.stopModule(CanId.CAN_ID_2)                
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load21()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5 

                elif((pm_assign2) == 2):
                    setter.setModulesLimit(60000, 200, gun_number=2)
                    mm2.digital_output_load22()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])             
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5 

            # Demand Condition 4
            if 32000 < target_power_from_car2 <= 58000 :
                # pm1=2
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                setter.setModulesLimit(60000, 200, gun_number=2)
                mm2.digital_output_load22()
                startCharging(pm2)

                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)             
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 

            # Demand Condition 5
            if  (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 1) or \
                (58000 < target_power_from_car2 <= 62000 and target_power_from_car1 <= 28000):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if ((pm_assign2) == 2):
                    setter.setModulesLimit(60000, 200, gun_number=2)
                    mm2.digital_output_load22()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5
                elif((pm_assign2) == 3):
                    setter.setModulesLimit(90000, 250, gun_number=2)
                    mm2.digital_output_load23()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load23()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5

            # Demand COndition 6
            if  (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 2) or \
                (58000 < target_power_from_car2 <= 62000 and pm_assign1 == 3):

                pm_assign2 = self._global_data.get_data_pm_assign2()
                if ((pm_assign2) == 2):
                    setter.setModulesLimit(60000, 200, gun_number=2)
                    mm2.digital_output_load22()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                
                    digitl_input = self._global_data.get_data()
                    if digitl_input[4] == '1':
                        mm2.digital_output_led_red2()
                        mm.stopcharging(CanId.STOP_GUN2)
                        stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN2_DATA[0] = 9
                        mm2.digital_output_open_load22()

                    if digitl_input[4] == '0':
                        PECC.STATUS1_GUN2_DATA[0] = 5 
                    
            # Demand Condition 7
            if  (target_power_from_car2 > 62000 and pm_assign1 == 1) or \
                target_power_from_car2 > 62000 and target_power_from_car1 <= 28000:
                setter.setModulesLimit(90000, 250, gun_number=2)
                pm2 = [CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                mm2.digital_output_load23()
                startCharging(pm2)

                # IMD Check
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)       
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load23()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 

            # Demand Condition 8
            if  (target_power_from_car2 > 62000 and pm_assign1 == 2) or \
                (target_power_from_car2 > 62000 and pm_assign1 == 3) or \
                (target_power_from_car2 > 62000 and target_power_from_car1 > 32000):
                
                setter.setModulesLimit(90000, 250, gun_number=2)

                # pm1=2
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(len(pm2))
                # stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                mm2.digital_output_load22()
                # funct_80_1()
                startCharging(pm2)

                #IMD check
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    stopActiveModules(pm2)       
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load22()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5 
        
        # GUN2:: Condition 14
        if  vehicle_status2 == 37 and vehicle_status1_g == 0 or \
            vehicle_status2 == 35 and vehicle_status1_g == 0 or \
            vehicle_status2 == 35 and vehicle_status1_g == 6 or \
            vehicle_status2 == 37 and vehicle_status1_g == 6:
            
            print("GUN2:: Condition 14")
            mm2.digital_output_led_red2()

            updateVI_status(vs2)
            stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

            mm.readModule_Voltage(CanId.CAN_ID_2)
            mm.readModule_Current(CanId.CAN_ID_2)
            PECC.STATUS1_GUN2_DATA[0] = 1
            # mm.digital_output_close_AC()

        
        # GUN2:: Condition 15
        if  vehicle_status2 == 37 and vehicle_status1_g == 35 or \
            vehicle_status2 == 35 and vehicle_status1_g == 37 or \
            vehicle_status2 == 35 and vehicle_status1_g == 35 or \
            vehicle_status2 == 37 and vehicle_status1_g == 35:
            print("GUN2:: Condition 15")
            mm2.digital_output_led_red2()

            updateVI_status(vs2)
            stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

            mm.readModule_Voltage(CanId.CAN_ID_2)
            mm.readModule_Current(CanId.CAN_ID_2)
            PECC.STATUS1_GUN2_DATA[0] = 1
        
        # GUN2:: Condition 16
        if  vehicle_status2 == 37 and vehicle_status1_g == 2 or \
            vehicle_status2 == 37 and vehicle_status1_g == 13 or \
            vehicle_status2 == 37 and vehicle_status1_g == 21 or \
            vehicle_status2 == 37 and vehicle_status1_g == 29:
            print("GUN2:: Condition 16")
            mm2.digital_output_led_red2()
            
            updateVI_status(vs2)
            
            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if ((pm_assign2) == 1):
                stopActiveModules([CanId.CAN_ID_2])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

            elif ((pm_assign2) == 2):
                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)
            
            elif ((pm_assign2) == 3):
                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)

            PECC.STATUS1_GUN2_DATA[0] = 1

        # GUN2:: Condition 17
        if  vehicle_status2 == 35 and vehicle_status1_g == 2 or \
            vehicle_status2 == 35 and vehicle_status1_g == 13 or \
            vehicle_status2 == 35 and vehicle_status1_g == 21 or \
            vehicle_status2 == 35 and vehicle_status1_g == 29:

            print("GUN2:: Condition 17")
            mm2.digital_output_led_red2()
            updateVI_status(vs2)

            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if ((pm_assign2) == 1):
                stopActiveModules([CanId.CAN_ID_2])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)

            elif ((pm_assign2) == 2):
                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_4)

            elif ((pm_assign2) == 3): 
                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_2)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)

            PECC.STATUS1_GUN2_DATA[0] = 1