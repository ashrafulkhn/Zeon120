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
        status2_g1_data = bytetobinary(PECC.STATUS2_GUN1_DATA)
        voltage_pre = binaryToDecimal(int(status2_g1_data[1] + status2_g1_data[0]))
        self._voltage = (voltage_pre / 10)
        current_pre = binaryToDecimal(int(status2_g1_data[3] + status2_g1_data[2]))
        self._current = (current_pre / 10)
        self._readPower = int(self._voltage * self._current)
        return self._readPower, self._voltage, self._current
    
    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        # print("Reading input status of Vehicle 1")
        vs1 = self._binary_data
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))
        vehicle_status1 = binaryToDecimal(int(vs1[0]))
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))

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
        
        def cableCheck(self, moduel_ids):
            print("GUN1:: Cable Check")
            cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))
            if cable_check_voltage1 <= 500:
                for module_id in moduel_ids:
                    mm.lowMode(module_id)
            if cable_check_voltage1 > 500:
                for module_id in moduel_ids:
                    mm.highMode(module_id)
            
            for module_id in moduel_ids:
                mm.setVoltage(DTH.convertohex(cable_check_voltage1), module_id)
                mm.startModule(module_id)

            mm.readModule_Voltage(CanId.CAN_ID_1)

            digitl_input = self._global_data.get_data()

            if digitl_input[1] == '0' or digitl_input[2] == '1' :
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                mm.stopModule(CanId.CAN_ID_1)
                stopActiveModules(module_ids=module_id)
                PECC.STATUS1_GUN1_DATA[0] = 3

        def handleError(self, module_ids):
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

        def standByled(self, ):
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
        
        def updateVI_status(self, vs1):
            """
            Update the VI status of the vehicle
            vs1: Vehicle status
            """
            # print("GUN1: UPDATE REQESTED for voltage and Current.")
            PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
            PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
            PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
            PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))

        def startCharging(self, module_ids):
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

        def stopActiveModules(self, module_ids):
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
        
        # Conditions 3
        elif  vehicle_status1 == 2 and vehicle_status2_g == 0 or \
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

        # Conditions 5
        elif  (vehicle_status1 == 13 and vehicle_status2_g == 0) or \
            (vehicle_status1 == 13 and vehicle_status2_g == 6):
            print("GUN1:: Condition 5")
            setter.setModulesLimit(120000, 250, gun_number=1)
            PECC.STATUS1_GUN1_DATA[0] = 1
            updateVI_status(vs1)

            mm1.digital_output_led_red1()
            mm1.digital_output_close_Gun14()   # Close Gun 1, Closing all the contactors for Gun1

            pm1=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
            self._global_data.set_data_pm_assign1(len(pm1))

            cableCheck(pm1)

            # check IMD status
            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                stopActiveModules(pm1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm.digital_output_open_stop()
                # time.sleep(5)
                mm.digital_output_open_fan()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        # GUN1:: Conditions 8
        elif  vehicle_status1 == 21 and vehicle_status2_g == 0 or \
            vehicle_status1 == 21 and vehicle_status2_g == 6:
            print("GUN1:: GUN1:: Condition 8")
            updateVI_status(vs1)
            setter.setModulesLimit(120000, 250, gun_number=1)
            mm1.digital_output_led_red1()
            mm1.digital_output_close_Gun14()
            pm1=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
            self._global_data.set_data_pm_assign1(len(pm1))
            startCharging(pm1)

            digitl_input = self._global_data.get_data()
            if digitl_input[3] == '1':
                mm1.digital_output_led_red1()
                mm.stopcharging(CanId.STOP_GUN1)
                stopActiveModules(pm1)
                PECC.STATUS1_GUN1_DATA[0] = 9
                mm.digital_output_open_stop()
                time.sleep(5)
                mm1.digital_output_open_fan()

            if digitl_input[3] == '0':
                PECC.STATUS1_GUN1_DATA[0] = 5

        
        # GUN1:: Conditions 11
        elif  vehicle_status1 == 29 and vehicle_status2_g == 0 or \
            vehicle_status1 == 29 and vehicle_status2_g == 6:
            print("GUN1:: Condition 11")
            updateVI_status(vs1)
            
            mm1.digital_output_led_green1()
            _target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            # target_power_from_car1 = min(setter.getSetLimit1(), _target_power_from_car1)
            
            print("GUN1:: Condition 11")
            mm1.digital_output_close_Gun14()
            setter.setModulesLimit(120000, 250, gun_number=1)
            pm1=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]

            self._global_data.set_data_pm_assign1(len(pm1))

            startCharging(pm1)

            val = self._global_data.get_data_targetpower_ev1() - self._readPower  # This val is not used anywhere. It is just for printing. Comment this line if you are not printing anything.

            print(f"Gun1:: DC11-7 LP: {120000}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev1()}, Diff: {val}")
            
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
            else:
                print("Targer Power is beyond threshold.")
        