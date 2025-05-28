import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH
import math

from power_120kw.can_readers.power_module_reader import PowerModuleReader
from pecc_frame_setter import PECCFrameSetter as setter

# logger = logging.getLogger(__name__)

class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self.limitChangeRequested = False
    
    def getRealTimeVIP(self):
        print("INFO:: Indside getRealtimeVIP")
        # Return the real-time voltage, current and power
        s2g1d = bytetobinary(PECC.STATUS2_GUN1_DATA)
        voltage_pre = binaryToDecimal(int(s2g1d[1] + s2g1d[0]))
        self._voltage = (voltage_pre / 10)
        current_pre = binaryToDecimal(int(s2g1d[3] + s2g1d[2]))
        self._current = (current_pre / 10)
        self._readPower = int(self._voltage * self._current)
        return self._readPower, self._voltage, self._current
    
    def limitChangeRequest(self, limitPower):
        print("INFO:: Indside Limit Change Function Gun1")
        realTimeVIP = self.getRealTimeVIP()
        # val = abs(limitPower - self._readPower)    # 35 - 34 = 1; 35 - 36 = -1
        val = abs(limitPower - realTimeVIP[0])    # 35 - 34 = 1; 35 - 36 = -1
        if self._global_data.get_data_targetpower_ev1() != 0:
            if val <= 2000:  # 2kW
                self.limitChangeRequested = True
            else:
                self.limitChangeRequested = False
        else:
            self.limitChangeRequested = False
        print(f"Gun1 :: LP: {limitPower}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev1()}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")
    
    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        # print("Reading input status of Vehicle 1")
        vs1 = self._binary_data
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))
        vehicle_status1 = binaryToDecimal(int(vs1[0]))
        #logger.info(f'Vehicle-1 status {vehicle_status1}')
        vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        
        self.getRealTimeVIP()   # To update the real-time voltage, current and power
        # print(f"Real-time Power: {self._readPower}W")

        #logger.info(f'Vehicle-2 status {vehicle_status2_g}')
        tag_vol1 = binaryToDecimal(int(vs1[2] + vs1[1]))
        target_volatge_from_car1 = (tag_vol1 / 10)

        tag_curr1 = binaryToDecimal(int(vs1[4] + vs1[3]))
        tag_curr11 = (tag_curr1 / 10)
        target_current_from_car1 = (tag_curr11)

        target_power1 = int(target_volatge_from_car1 * tag_curr11)
        self._global_data.set_data_targetpower_ev1(target_power1)

        def cableCheck():
            print("GUN1:: Cable Check")
            cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))
            if cable_check_voltage1 <= 500:
                mm.lowMode(CanId.CAN_ID_1)
            if cable_check_voltage1 > 500:
                mm.highMode(CanId.CAN_ID_1)

            mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
            mm.startModule(CanId.CAN_ID_1)
            mm.readModule_Voltage(CanId.CAN_ID_1)
            digitl_input = self._global_data.get_data()

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 3

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
            mm1.digital_output_led_red1()
            mm.stopcharging(CanId.STOP_GUN1)
            print("Error Occured.")
            for module_id in module_ids:
                mm.stopModule(module_id)

            PECC.STATUS1_GUN1_DATA[0] = 3

        def standByled():
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1' :
                    PECC.STATUS1_GUN1_DATA[0] = 2
                    mm1.digital_output_led_red1()
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm1.digital_output_led_red1()
            else:
                PECC.STATUS1_GUN1_DATA[0] = 0
                mm1.digital_output_led_red1()
            
        def updateVI_status(vs1):
            """
            Update the VI status of the vehicle
            vs1: Vehicle status
            """
            # print("GUN1: UPDATE REQESTED for voltage and Current.")
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))

        def startCharging(module_ids):
            """
            Call the startCharging function to start the charging process
            modue_ids: List of module IDs to be started
            Example:
            module_ids = [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
            """
            # print(f"INFO:: Indside Start Charging Function, Module List: {module_ids}")

            if target_volatge_from_car1 <= 500:
                for module_id in module_ids:
                    mm.lowMode(module_id)
            elif target_volatge_from_car1 > 500:
                for module_id in module_ids:
                    mm.highMode(module_id)

            RUNNING_CURRENT = (target_current_from_car1/len(module_ids))
            self._global_data.set_data_running_current(RUNNING_CURRENT)

            for module_id in module_ids:
                voltage_value = DTH.convertohex(target_volatge_from_car1)
                mm.setVoltage(voltage_value, module_id)
                mm.setCurrent(module_id)
                mm.startModule(module_id)
                mm.readModule_Current(module_id)
            mm.readModule_Voltage(module_ids[0])
            
            # Handle error conditions here
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1'  :
                handleError(module_ids)

        def stopActiveModules(module_ids):
            # print(f"Stopping Modules {module_ids}")
            for module_id in module_ids:
                mm.stopModule(module_id)
        
        # Conditions 1
        if  vehicle_status1 == 0 and vehicle_status2_g == 0 or \
            vehicle_status1 == 6 and vehicle_status2_g == 6 or \
            vehicle_status1 == 6 and vehicle_status2_g == 0:

            """
            When both the guns are not connected to the vehicle, then the status of the gun is 0 or 6.
            """
            print("GUN1:: Condition 1")
            mm.digital_output_open_AC()
            setter.setModulesLimit(120000, 250, 1)

            pm1=[]
            self._global_data.set_data_pm_assign1(len(pm1))
            digitl_input = self._global_data.get_data()
            standByled()
        
        # conditions 2
        if  vehicle_status1 == 0 and vehicle_status2_g == 6 or \
            vehicle_status1 == 0 and vehicle_status2_g == 2 or \
            vehicle_status1 == 0 and vehicle_status2_g == 29 :
            print("GUN1:: Condition 2")
            setter.setModulesLimit(120000, 250, gun_number=1)

            pm1=[]
            self._global_data.set_data_pm_assign1(len(pm1))
            digitl_input = self._global_data.get_data()
            standByled()
        
        # Conditions 3
        if  vehicle_status1 == 2 and vehicle_status2_g == 0 or \
            vehicle_status1 == 2 and vehicle_status2_g == 6 :
            print("GUN1:: Condition 3")
            
            setter.setModulesLimit(120000, 250, gun_number=1)

            pm1=[]
            self._global_data.set_data_pm_assign1(len(pm1))
            digitl_input = self._global_data.get_data()

            try:
                if len(digitl_input) != 0 :
                    if digitl_input[1] == '0' or digitl_input[2] == '1'  :
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        PECC.STATUS1_GUN1_DATA[0] = 2
                    
                    else:
                        mm1.digital_output_led_red1()
                        mm.digital_output_close_AC()
                        PECC.STATUS1_GUN1_DATA[0] = 0
                else:
                    PECC.STATUS1_GUN1_DATA[0] = 0
                    mm.digital_output_close_AC()
                    mm1.digital_output_led_red1()
            except IndexError:
                print("GUN1: IndexError: List index out of range. Please check the input data.")

        # Conditions 4
        if  vehicle_status1 == 2 and vehicle_status2_g == 13 or \
            vehicle_status1 == 2 and vehicle_status2_g == 21 or\
            vehicle_status1 == 2 and vehicle_status2_g == 2 or\
            vehicle_status1 == 2 and vehicle_status2_g == 29:
            print("GUN1:: Condition 4")
            setter.setModulesLimit(120000, 250, gun_number=1)

            # Set LED to red
            mm1.digital_output_led_red1()
            PECC.STATUS1_GUN1_DATA[0] = 0
            
            # Taking data from Gun 2.
            # target_power_from_car2 = self._global_data.get_data_targetpower_ev2()

            pm1=[]
            self._global_data.set_data_pm_assign1(len(pm1))

            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                PECC.STATUS1_GUN1_DATA[0] = 2

        # Conditions 5
        if  (vehicle_status1 == 13 and vehicle_status2_g == 0) or \
            (vehicle_status1 == 13 and vehicle_status2_g == 6):
            print("GUN1:: Condition 5")
            setter.setModulesLimit(120000, 250, gun_number=1)
            PECC.STATUS1_GUN1_DATA[0] = 1
            updateVI_status(vs1)

            mm1.digital_output_led_red1()
            mm1.digital_output_close_Gun11()   # Close Gun 1

            pm1=[CanId.CAN_ID_1]
            self._global_data.set_data_pm_assign1(len(pm1))

            cableCheck()

            # check IMD status
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

        # GUN1:: Conditions 6
        if  vehicle_status1 == 13 and vehicle_status2_g == 2 or \
            vehicle_status1 == 13 and vehicle_status2_g == 35 or \
            vehicle_status1 == 13 and vehicle_status2_g == 37:
            print("GUN1:: Condition 6: Gun1 - Cable Check, Gun2 - Disconnected or Error State")
            updateVI_status(vs1)
        
            PECC.STATUS1_GUN1_DATA[0] = 1

            mm1.digital_output_led_red1()
            mm1.digital_output_Gun1_load21()

            pm1=[CanId.CAN_ID_1]
            self._global_data.set_data_pm_assign1(len(pm1))
            stopActiveModules([CanId.CAN_ID_2,
                                CanId.CAN_ID_4,
                                CanId.CAN_ID_3])
            
            cableCheck()
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()
                
            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        # GUN1:: Conditions 7
        if  vehicle_status1 == 13 and vehicle_status2_g == 13 or \
            vehicle_status1 == 13 and vehicle_status2_g == 21 or \
            vehicle_status1 == 13 and vehicle_status2_g == 29:
            print("GUN1:: Condition 7")
            updateVI_status(vs1)

            PECC.STATUS1_GUN1_DATA[0] = 1

            mm1.digital_output_led_red1()
            mm1.digital_output_load11()
            pm1= [CanId.CAN_ID_1]

            self._global_data.set_data_pm_assign1(len(pm1))
            cableCheck()

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        # GUN1:: Conditions 8
        if  vehicle_status1 == 21 and vehicle_status2_g == 0 or \
            vehicle_status1 == 21 and vehicle_status2_g == 6:
            print("GUN1:: GUN1:: Condition 8")
            updateVI_status(vs1)
            setter.setModulesLimit(20000, 100, gun_number=1)
            mm1.digital_output_led_red1()
            mm1.digital_output_close_Gun11()
            pm1=[CanId.CAN_ID_1]
            self._global_data.set_data_pm_assign1(len(pm1))
            startCharging(pm1)

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

        # GUN1:: Conditions 9
        if  vehicle_status1 == 21 and vehicle_status2_g == 2 or     \
            vehicle_status1 == 21 and vehicle_status2_g == 35 or    \
            vehicle_status1 == 21 and vehicle_status2_g == 37:
            print("GUN1:: Condition 9")
            updateVI_status(vs1)
            
            mm1.digital_output_led_red1()
            setter.setModulesLimit(20000, 100, gun_number=1)

            mm1.digital_output_Gun1_load21()
            stopActiveModules([CanId.CAN_ID_2,
                               CanId.CAN_ID_3,
                               CanId.CAN_ID_4])

            pm1=[CanId.CAN_ID_1]
            self._global_data.set_data_pm_assign1(len(pm1))
            startCharging(pm1)

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()
                
            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        # GUN1:: Condition 10
        if  vehicle_status1 == 21 and vehicle_status2_g == 13 or \
            vehicle_status1 == 21 and vehicle_status2_g == 21 or \
            vehicle_status1 == 21 and vehicle_status2_g == 29:
            print("GUN1:: Condition 10")
            updateVI_status(vs1)
            mm1.digital_output_led_red1()
            setter.setModulesLimit(20000, 100, gun_number=1)
            mm1.digital_output_load11()

            pm1=[CanId.CAN_ID_1]
            self._global_data.set_data_pm_assign1(len(pm1))
            startCharging(pm1)

            digitl_input = self._global_data.get_data()

            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)                
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm1.digital_output_open_load11()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5
        
        # GUN1:: Conditions 11
        if  vehicle_status1 == 29 and vehicle_status2_g == 0 or \
            vehicle_status1 == 29 and vehicle_status2_g == 6:
            print("GUN1:: Condition 11")
            updateVI_status(vs1)
            
            mm1.digital_output_led_green1()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
            # Demand GUN1:: Condition 1
            # if target_power_from_car1 <= 38000:
            if target_power_from_car1 <= 29000:
                print("GUN1:: Condition 11-1")

                setter.setModulesLimit(25000, 100, gun_number=1)

                # Assign modules for Gun1
                pm1=[CanId.CAN_ID_1]
                # pm_assign1 = self._global_data.set_data_pm_assign1(pm1)
                self._global_data.set_data_pm_assign1(len(pm1))

                mm1.digital_output_close_Gun11()
                stopActiveModules([CanId.CAN_ID_2,
                                CanId.CAN_ID_4,
                                CanId.CAN_ID_3])

                # Check the realtime votage and current
                
                self.limitChangeRequest(25000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    # print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    startCharging(pm1)

                else:
                    if self._global_data.get_data_targetpower_ev1() == 0:
                        stopActiveModules([CanId.CAN_ID_1])
                    else:
                        setter.setModulesLimit(55000, 200, gun_number=1)
                        self.limitChangeRequested = False
                        # print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()

                # IMD Status Check
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)
                    # mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 2
            if  target_power_from_car1 > 29000 and \
                target_power_from_car1 < 31000:
                print("GUN1:: Condition 11-2")
                
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(29000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(55000, 200, 1)
                    self.limitChangeRequested = False

                if (pm_assign1 == 1):
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    mm1.digital_output_close_Gun11()
                    startCharging([CanId.CAN_ID_1])
                elif (pm_assign1 == 2):
                    mm1.digital_output_close_Gun12()
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

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

            # Demand Condition 3
            if  target_power_from_car1 >= 31000 and \
                target_power_from_car1 <= 59000:
                print("GUN1:: Condition 11-3")
                setter.setModulesLimit(55000, 200, gun_number=1)
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3]
                # pm_assign1 = self._global_data.set_data_pm_assign1(pm1)
                self._global_data.set_data_pm_assign1(len(pm1))
                stopActiveModules([CanId.CAN_ID_2,CanId.CAN_ID_4])

                self.limitChangeRequest(55000)  # Updates the limitChangeRequested variable to true if the limit is reached
                if (self.limitChangeRequested == False):
                    mm1.digital_output_close_Gun12()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(85000, 250, gun_number=1)
                    self.limitChangeRequested = False
                    # print(f"INFO: Limit changed to 75kW.")

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
            
            # Demand Condition 4
            if  target_power_from_car1 > 59000 and \
                target_power_from_car1 < 61000:
                print("GUN1:: Condition 11-4")
            # if target_power_from_car1 > 78000 and target_power_from_car1 < 82000:
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(59000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(85000, 250, 1)
                    self.limitChangeRequested = False

                if ((pm_assign1) == 2):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm1.digital_output_close_Gun12()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])
                elif ((pm_assign1) == 3):
                    mm1.digital_output_close_Gun13()
                    mm.stopModule(CanId.CAN_ID_2)
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    # mm.stopModule(CanId.CAN_ID_1)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
            
            # Demand Condition 5
            if  target_power_from_car1 >= 61000 and \
                target_power_from_car1 <= 89000:
                print("GUN1:: Condition 11-5")
                setter.setModulesLimit(85000, 250, gun_number=1)

                mm.stopModule(CanId.CAN_ID_2)
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign1(len(pm1))

                self.limitChangeRequest(85000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    mm1.digital_output_close_Gun13()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(120000, 250, gun_number=1)
                    self.limitChangeRequested = False
                    # print(f"INFO: Limit changed to 120kW.")

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()
                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 6
            if  target_power_from_car1 > 89000 and \
                target_power_from_car1 < 91000:
                print("GUN1:: Condition 11-6")
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(89000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(120000, 250, 1)
                    self.limitChangeRequested = False

                if (pm_assign1 == 3):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm1.digital_output_close_Gun13()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
                elif ((pm_assign1) == 4):
                    mm1.digital_output_close_Gun14()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm1.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
            
            # Demand Condition 7
            if target_power_from_car1 >= 91000:
                print("GUN1:: Condition 11-7")
                mm1.digital_output_close_Gun14()

                setter.setModulesLimit(120000, 250, gun_number=1)

                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]

                self._global_data.set_data_pm_assign1(len(pm1))

                startCharging(pm1)

                val = 120000 - self._global_data.get_data_targetpower_ev1()   # This val is not used anywhere. It is just for printing. Comment this line if you are not printing anything.

                print(f"Gun1:: DC11-7 LP: {120000}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev1()}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")
                
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm.digital_output_open_stop()
                    time.sleep(5)
                    mm.digital_output_open_fan()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5
       
        # GUN1:: Condition 12
        if  vehicle_status1 == 29 and vehicle_status2_g == 2 or   \
            vehicle_status1 == 29 and vehicle_status2_g == 35 or \
            vehicle_status1 == 29 and vehicle_status2_g == 37:
            print("GUN1:: Condition 12")
            updateVI_status(vs1)
            mm1.digital_output_led_green1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            pm_assign2 = self._global_data.get_data_pm_assign2() # Number of modules assigned to Gun 2

            # Demand Condition 1
            if (target_power_from_car1 <= 29000) :
                print("GUN1:: Condition 12-1")
                setter.setModulesLimit(25000, 100, gun_number=1)
                pm1=[CanId.CAN_ID_1]
                self._global_data.set_data_pm_assign1(len(pm1))
                mm1.digital_output_Gun1_load21()

                self.limitChangeRequest(25000)

                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4, CanId.CAN_ID_3])
                
                if (self.limitChangeRequested == False):
                    startCharging(pm1)
                else:
                    if self._global_data.get_data_targetpower_ev1() == 0:
                        stopActiveModules(pm1)
                    else:
                        setter.setModulesLimit(55000, 200, gun_number=1)
                        self.limitChangeRequested = False

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    mm.stopModule(CanId.CAN_ID_1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            # Demand Condtition 2
            if (29000 < target_power_from_car1 <= 31000) :
                print("GUN1:: Condition 12-2")
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(29000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(55000, 200, 1)
                    self.limitChangeRequested = False

                if (pm_assign1 == 1):
                    mm1.digital_output_Gun1_load21()
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4, CanId.CAN_ID_3])
                    startCharging([CanId.CAN_ID_1])
                    
                    # IMD Check conditions
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load11()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

                elif((pm_assign1) == 2):
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    mm1.digital_output_Gun1_load22()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            #Demand Condition 3
            if (31000 < target_power_from_car1 <= 59000):
                print("GUN1:: Condition 12-3")
                setter.setModulesLimit(60000, 250, gun_number=1)
                # pm1=2
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3]
                self._global_data.set_data_pm_assign1(len(pm1))

                stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])

                self.limitChangeRequest(55000)

                if (self.limitChangeRequested == False):
                    # mm1.digital_output_close_Gun12()
                    mm1.digital_output_Gun1_load22()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(85000, 250, gun_number=1)
                    self.limitChangeRequested = False

                digitl_input = self._global_data.get_data()
                # IMD Check
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)

                    stopActiveModules(pm1)            
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            # Demand Condition 4
            if  (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 1) or \
                (59000 < target_power_from_car1 <= 61000 and target_power_from_car2 <= 29000):
                print("GUN1:: Condition 12-4")
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(59000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(90000, 250, 1)
                    self.limitChangeRequested = False

                if (pm_assign1 == 2):
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    mm1.digital_output_Gun1_load22()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

                if ((pm_assign1) == 3):
                    mm.stopModule(CanId.CAN_ID_2)
                    mm1.digital_output_Gun1_load23()
                    # funct_120_1()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])

                    #Imd check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])             
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load13()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 5
            if  (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 2) or \
                (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 3):
                print("GUN1:: Condition 12-5")
                pm_assign1 = self._global_data.get_data_pm_assign1()
                self.limitChangeRequest(59000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(90000, 250, 1)
                    self.limitChangeRequested = False

                if ((pm_assign1) == 2):
                    # PECC.LIMITS1_DATA_120kw_Gun1[4] = 64
                    # PECC.LIMITS1_DATA_120kw_Gun1[5] = 31
                    # PECC.LIMITS2_DATA_120kw_Gun1[2] = 196
                    # PECC.LIMITS2_DATA_120kw_Gun1[3] = 9
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    mm1.digital_output_Gun1_load22()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])            
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

                elif((pm_assign1) == 3):
                    stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
                    mm1.digital_output_Gun1_load22()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

                    #IMD Check
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 6
            if  (target_power_from_car1 > 61000 and pm_assign2 == 1) or \
                (target_power_from_car1 > 61000 and target_power_from_car2 <= 29000):
                print("GUN1:: Condition 12-6")
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign1(len(pm1))
                mm.stopModule(CanId.CAN_ID_2)
                
                self.limitChangeRequest(60000)
                # if self.limitChangeRequested == False:
                #     mm1.digital_output_Gun1_load23()
                #     startCharging(pm1)

                # else:
                #     setter.setModulesLimit(90000, 250, gun_number=1)
                #     self.limitChangeRequested = False
                self._global_data.get_data_targetpower_ev1()
                setter.setModulesLimit(90000, 250, gun_number=1)
                mm1.digital_output_Gun1_load23()
                startCharging(pm1)

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)              
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load13()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 7
            # if  (target_power_from_car1 > 62000 and pm_assign2 == 2) or \
            #     (target_power_from_car1 > 62000 and pm_assign2 == 3):
            #     print("GUN1:: Condition 12-7")
            #     setter.setModulesLimit(60000, 200, gun_number=1)

            #     # pm1=2
            #     pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3]
            #     self._global_data.set_data_pm_assign1(len(pm1))
            #     stopActiveModules([CanId.CAN_ID_2, CanId.CAN_ID_4])
            #     mm1.digital_output_Gun1_load22()
            #     startCharging(pm1)

            #     #IMD check
            #     digitl_input = self._global_data.get_data()
            #     if digitl_input[3] == '1':
            #         mm1.digital_output_led_red1()
            #         mm.stopcharging(CanId.STOP_GUN1)
            #         stopActiveModules(pm1)       
            #         PECC.STATUS1_GUN1_DATA[0] = 9
            #         mm1.digital_output_open_load12()

            #     if digitl_input[3] == '0':
            #         PECC.STATUS1_GUN1_DATA[0] = 5 
        
        # GUN1:: Condition 13
        if  vehicle_status1 == 29 and vehicle_status2_g == 13 or \
            vehicle_status1 == 29 and vehicle_status2_g == 21 or \
            vehicle_status1 == 29 and vehicle_status2_g == 29:
            print("GUN1:: Condition 13")
            updateVI_status(vs1=vs1)
            mm1.digital_output_led_green1()

            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            
            # Demand Condition 1
            if  (target_power_from_car1 <= 29000 and pm_assign2 == 1) or \
                (target_power_from_car1 <= 29000 and pm_assign2 == 2) :
                print("GUN1:: Condition 13-1")
                setter.setModulesLimit(25000, 100, gun_number=1)
                # mm1.digital_output_load11()
                mm.stopModule(CanId.CAN_ID_3)
                # pm1=1
                pm1=[CanId.CAN_ID_1]
                self._global_data.set_data_pm_assign1(len(pm1))
                # funct_40_1()
                self.limitChangeRequest(25000)

                if self.limitChangeRequested == False:
                    mm1.digital_output_load11()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(55000, 200, 1)
                    self.limitChangeRequested = False

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)               
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 
            
            # Demand Condition 2
            if (target_power_from_car1 <= 29000 and pm_assign2 == 3) :
                print("GUN1:: Condition 13-2")
                setter.setModulesLimit(25000, 100, gun_number=1)
                # mm1.digital_output_load11()
                # pm1=1
                pm1=[CanId.CAN_ID_1]
                self._global_data.set_data_pm_assign1(len(pm1))

                startCharging(pm1)

                self.limitChangeRequest(25000)

                if self.limitChangeRequested == False:
                    mm1.digital_output_load11()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(55000, 200, 1)
                    self.limitChangeRequested = False

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load11()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand Condition 3
            if 29000 < target_power_from_car1 <= 31000 :
                print("GUN1:: Condition 13-3")
                pm_assign1 = self._global_data.get_data_pm_assign1()
                self.limitChangeRequest(29000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(55000, 200, 1)
                    self.limitChangeRequested = False

                if ((pm_assign1) == 1):
                    mm1.digital_output_load11()
                    startCharging([CanId.CAN_ID_1])
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        mm.stopModule(CanId.CAN_ID_1)                
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load11()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

                elif((pm_assign1) == 2):
                    mm1.digital_output_load12()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])

                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])             
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 

            # Demand Condition 4
            if 31000 < target_power_from_car1 <= 59000 :   # Borrow from other Gun
                print("GUN1:: Condition 13-4")
                # pm1=2
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3]
                self._global_data.set_data_pm_assign1(len(pm1))
                setter.setModulesLimit(55000, 200, gun_number=1)
                # mm1.digital_output_load12()
                # startCharging(pm1)
                self.limitChangeRequest(55000)

                if self.limitChangeRequested == False:
                    mm1.digital_output_load12()
                    startCharging(pm1)
                else:
                    setter.setModulesLimit(85000, 250, 1)
                    self.limitChangeRequested = False

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 

            # Demand Condition 5
            if  (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 1) or \
                (59000 < target_power_from_car1 <= 61000 and target_power_from_car2 <= 29000):
                print("GUN1:: Condition 13-5")
                pm_assign1 = self._global_data.get_data_pm_assign1()

                self.limitChangeRequest(59000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(90000, 250, 1)
                    self.limitChangeRequested = False

                if ((pm_assign1) == 2):
                    # setter.setModulesLimit(55000, 200, gun_number=1)
                    mm1.digital_output_load12()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif((pm_assign1) == 3):
                    # setter.setModulesLimit(90000, 250, gun_number=1)
                    mm1.digital_output_load13()
                    # funct_120_1()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])

                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load13()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5

            # Demand COndition 6
            if  (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 2) or \
                (59000 < target_power_from_car1 <= 61000 and pm_assign2 == 3):
                print("GUN1:: Condition 13-6")
                pm_assign1 = self._global_data.get_data_pm_assign1()
                setter.setModulesLimit(60000, 200, gun_number=1)
                # self.limitChangeRequest(59000)
                # if self.limitChangeRequested == True:
                #     setter.setModulesLimit(60000, 200, 1)
                #     self.limitChangeRequested = False

                if ((pm_assign1) == 2):
                    mm1.digital_output_load12()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_3])
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])               
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
                elif((pm_assign1) == 3):
                    mm1.digital_output_load12()
                    # funct_80_1()
                    startCharging(CanId.CAN_ID_1, CanId.CAN_ID_3)
                
                    digitl_input = self._global_data.get_data()
                    if digitl_input[3] == '1':
                        mm1.digital_output_led_red1()
                        mm.stopcharging(CanId.STOP_GUN1)
                        stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])              
                        PECC.STATUS1_GUN1_DATA[0] = 9
                        mm1.digital_output_open_load12()

                    if digitl_input[3] == '0':
                        PECC.STATUS1_GUN1_DATA[0] = 5 
            
            # Demand Condition 7
            if  (target_power_from_car1 > 61000 and pm_assign2 == 1) or \
                (target_power_from_car1 > 61000 and target_power_from_car2 <= 29000):
                print("GUN1:: Condition 13-7")
                self.limitChangeRequest(59000)
                if self.limitChangeRequested == True:
                    setter.setModulesLimit(90000, 250, 1)
                    self.limitChangeRequested = False
                # setter.setModulesLimit(90000, 250, gun_number=1)
                # pm1=3
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign1(len(pm1))
                mm1.digital_output_load13()
                # funct_120_1()
                startCharging(pm1)

                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)              
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load13()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5 
            
            # Demand Condition 8
            if  (target_power_from_car1 > 62000 and pm_assign2 == 2) or \
                (target_power_from_car1 > 62000 and pm_assign2 == 3) or\
                (target_power_from_car1 > 62000 and target_power_from_car2 > 32000):
                print("GUN1:: Condition 13-8")
                setter.setModulesLimit(60000, 200, gun_number=1)
                mm1.digital_output_load12()
                # pm1=2
                pm1=[CanId.CAN_ID_1, CanId.CAN_ID_3]
                self._global_data.set_data_pm_assign1(len(pm1))
                startCharging(pm1)
                digitl_input = self._global_data.get_data()
                if digitl_input[3] == '1':
                    mm1.digital_output_led_red1()
                    mm.stopcharging(CanId.STOP_GUN1)
                    stopActiveModules(pm1)           
                    PECC.STATUS1_GUN1_DATA[0] = 9
                    mm1.digital_output_open_load12()

                if digitl_input[3] == '0':
                    PECC.STATUS1_GUN1_DATA[0] = 5    
        
        # GUN1:: Condition 14
        if  vehicle_status1 == 37 and vehicle_status2_g == 0 or \
            vehicle_status1 == 35 and vehicle_status2_g == 0 or \
            vehicle_status1 == 35 and vehicle_status2_g == 6 or \
            vehicle_status1 == 37 and vehicle_status2_g == 6:
            
            print("GUN1:: Condition 14")
            mm1.digital_output_led_red1()

            updateVI_status(vs1)
            stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
            # mm.digital_output_close_AC()

        # GUN1:: Condition 15
        if  vehicle_status1 == 37 and vehicle_status2_g == 35 or \
            vehicle_status1 == 35 and vehicle_status2_g == 37 or \
            vehicle_status1 == 35 and vehicle_status2_g == 35 or \
            vehicle_status1 == 37 and vehicle_status2_g == 35:
            print("GUN1:: Condition 15")
            mm1.digital_output_led_red1()

            updateVI_status(vs1)
            stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

            mm.readModule_Voltage(CanId.CAN_ID_1)
            mm.readModule_Current(CanId.CAN_ID_1)
            PECC.STATUS1_GUN1_DATA[0] = 1
        
        # GUN1:: Condition 16
        if  vehicle_status1 == 37 and vehicle_status2_g == 2 or \
            vehicle_status1 == 37 and vehicle_status2_g == 13 or \
            vehicle_status1 == 37 and vehicle_status2_g == 21 or \
            vehicle_status1 == 37 and vehicle_status2_g == 29:
            print("GUN1:: Condition 16")
            mm1.digital_output_led_red1()
            updateVI_status(vs1)
            
            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if ((pm_assign1) == 1):
                stopActiveModules([CanId.CAN_ID_1])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)

            elif ((pm_assign1) == 2):
                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
            
            elif ((pm_assign1) == 3):
                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)

            PECC.STATUS1_GUN1_DATA[0] = 1

        # GUN1:: Condition 17
        if  vehicle_status1 == 35 and vehicle_status2_g == 2 or  \
            vehicle_status1 == 35 and vehicle_status2_g == 13 or \
            vehicle_status1 == 35 and vehicle_status2_g == 21 or \
            vehicle_status1 == 35 and vehicle_status2_g == 29:

            print("GUN1:: Condition 17")
            mm1.digital_output_led_red1()
            updateVI_status(vs1)

            pm_assign1 = self._global_data.get_data_pm_assign1()
            pm_assign2 = self._global_data.get_data_pm_assign2()
            if ((pm_assign1) == 1):
                stopActiveModules([CanId.CAN_ID_1])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)

            elif ((pm_assign1) == 2):
                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)

            elif ((pm_assign1) == 3): 
                stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
                mm.readModule_Voltage(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_1)
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)

            PECC.STATUS1_GUN1_DATA[0] = 1