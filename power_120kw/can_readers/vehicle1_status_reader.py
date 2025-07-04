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
from power_120kw.can_readers.charge_action import VehicleCharger

# logger = logging.getLogger(__name__)

class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769   # 0x301

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self.limitChangeRequested = False
        self.vehicleCharger = VehicleCharger()
    
    # def getRealTimeVIP(self):
    #     print("INFO:: Indside getRealtimeVIP")
    #     # Return the real-time voltage, current and power
    #     s2g1d = bytetobinary(PECC.STATUS2_GUN1_DATA)
    #     voltage_pre = binaryToDecimal(int(s2g1d[1] + s2g1d[0]))
    #     self._voltage = (voltage_pre / 10)
    #     current_pre = binaryToDecimal(int(s2g1d[3] + s2g1d[2]))
    #     self._current = (current_pre / 10)
    #     self._readPower = int(self._voltage * self._current)
    #     return self._readPower, self._voltage, self._current
    
    # def limitChangeRequest(self, limitPower):
    #     print("INFO:: Indside Limit Change Function Gun1")
    #     realTimeVIP = self.getRealTimeVIP()
    #     # val = abs(limitPower - self._readPower)    # 35 - 34 = 1; 35 - 36 = -1
    #     val = abs(limitPower - realTimeVIP[0])    # 35 - 34 = 1; 35 - 36 = -1
    #     if self._global_data.get_data_targetpower_ev1() != 0:
    #         if val <= 2000:  # 2kW
    #             self.limitChangeRequested = True
    #         else:
    #             self.limitChangeRequested = False
    #     else:
    #         self.limitChangeRequested = False
    #     print(f"Gun1 :: LP: {limitPower}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev1()}, SLP: {min(setter.getSetLimit1(), self._global_data.get_data_targetpower_ev1())}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")
    
    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        print("Inside read_input_data of Vehicle-1 status")
        vs1 = self._binary_data
        self._global_data.set_data_status_vehicle1(binaryToDecimal(int(vs1[0])))
        # vehicle_status1 = binaryToDecimal(int(vs1[0]))
        #logger.info(f'Vehicle-1 status {vehicle_status1}')
        # vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        
        # self.getRealTimeVIP()   # To update the real-time voltage, current and power
        # print(f"Real-time Power: {self._readPower}W")

        #logger.info(f'Vehicle-2 status {vehicle_status2_g}')
        tag_vol1 = binaryToDecimal(int(vs1[2] + vs1[1]))
        target_volatge_from_car1 = (tag_vol1 / 10)

        tag_curr1 = binaryToDecimal(int(vs1[4] + vs1[3]))
        tag_curr11 = (tag_curr1 / 10)
        # target_current_from_car1 = (tag_curr11)

        target_power1 = int(target_volatge_from_car1 * tag_curr11)
        self._global_data.set_data_targetpower_ev1(target_power1)
        print(f"Target Voltage: {target_volatge_from_car1}, Target Current: {tag_curr11}")
        self.vehicleCharger.action()

        # def cableCheck():
        #     print("GUN1:: Cable Check")
        #     cable_check_voltage1 = binaryToDecimal(int(vs1[7] + vs1[6]))
        #     if cable_check_voltage1 <= 500:
        #         mm.lowMode(CanId.CAN_ID_1)
        #     if cable_check_voltage1 > 500:
        #         mm.highMode(CanId.CAN_ID_1)

        #     mm.setVoltage(DTH.convertohex(cable_check_voltage1), CanId.CAN_ID_1)
        #     mm.startModule(CanId.CAN_ID_1)
        #     mm.readModule_Voltage(CanId.CAN_ID_1)
        #     digitl_input = self._global_data.get_data()

        #     if digitl_input[1] == '0' or digitl_input[2] == '1' :
        #         mm1.digital_output_led_red1()
        #         mm.stopcharging(CanId.STOP_GUN1)
        #         mm.stopModule(CanId.CAN_ID_1)
        #         PECC.STATUS1_GUN1_DATA[0] = 3

        # def handleError(module_ids):
        #     """"
        #     Check the digital input from the VSECC.
        #     Digital input 1: Emergency Button Status, 0 is Active
        #     Digital input 2: SPD Status/ELR Status, 1 is active
        #     Digital input 7: 3 Phase Monitoring Device Status, 0 is active
        #     If any of the above digital input is Active, then stop the charging and turn on the red LED.

        #     """
        #     # Handle error conditions here

        #     # Check the digital input from the VSECC.
        #     mm1.digital_output_led_red1()
        #     mm.stopcharging(CanId.STOP_GUN1)
        #     print("Error Occured.")
        #     for module_id in module_ids:
        #         mm.stopModule(module_id)

        #     PECC.STATUS1_GUN1_DATA[0] = 3

        # def standByled():
        #     digitl_input = self._global_data.get_data()
        #     if len(digitl_input) != 0 :
        #         if digitl_input[1] == '0' or digitl_input[2] == '1' :
        #             PECC.STATUS1_GUN1_DATA[0] = 2
        #             mm1.digital_output_led_red1()
        #         else:
        #             PECC.STATUS1_GUN1_DATA[0] = 0
        #             mm1.digital_output_led_red1()
        #     else:
        #         PECC.STATUS1_GUN1_DATA[0] = 0
        #         mm1.digital_output_led_red1()
            
        # def updateVI_status(vs1):
        #     """
        #     Update the VI status of the vehicle
        #     vs1: Vehicle status
        #     """
        #     # print("GUN1: UPDATE REQESTED for voltage and Current.")
        #     PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
        #     PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
        #     PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
        #     PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))

        # def startCharging(module_ids):
        #     """
        #     Call the startCharging function to start the charging process
        #     modue_ids: List of module IDs to be started
        #     Example:
        #     module_ids = [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
        #     """
        #     # print(f"INFO:: Indside Start Charging Function, Module List: {module_ids}")

        #     if target_volatge_from_car1 <= 500:
        #         for module_id in module_ids:
        #             mm.lowMode(module_id)
        #     elif target_volatge_from_car1 > 500:
        #         for module_id in module_ids:
        #             mm.highMode(module_id)

        #     RUNNING_CURRENT = (target_current_from_car1/len(module_ids))
        #     self._global_data.set_data_running_current(RUNNING_CURRENT)

        #     for module_id in module_ids:
        #         voltage_value = DTH.convertohex(target_volatge_from_car1)
        #         mm.setVoltage(voltage_value, module_id)
        #         mm.setCurrent(module_id)
        #         mm.startModule(module_id)
        #         mm.readModule_Current(module_id)
        #     mm.readModule_Voltage(module_ids[0])
            
        #     # Handle error conditions here
        #     digitl_input = self._global_data.get_data()
        #     if digitl_input[1] == '0' or digitl_input[2] == '1'  :
        #         handleError(module_ids)

        # def stopActiveModules(module_ids):
        #     # print(f"Stopping Modules {module_ids}")
        #     for module_id in module_ids:
        #         mm.stopModule(module_id)
        
        # # self.vehicleCharger.read_data()