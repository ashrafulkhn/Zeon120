import logging
import time

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module2Message as mm2, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH
from pecc_frame_setter import PECCFrameSetter as setter
from power_120kw.can_readers.charge_action import VehicleCharger

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
        self.vehicleCharger = VehicleCharger()

    #  #  Return the real-time voltage, current and power
    # def getRealTimeVIP(self):
    #     s2g2d = bytetobinary(PECC.STATUS2_GUN2_DATA)
    #     voltage_pre = binaryToDecimal(int(s2g2d[1] + s2g2d[0]))
    #     self._voltage = (voltage_pre / 10)
    #     current_pre = binaryToDecimal(int(s2g2d[3] + s2g2d[2]))
    #     self._current = (current_pre / 10)

    #     self._readPower = int(self._voltage * self._current)
    #     # print(f"Real-time G2: Voltage: {self._voltage}V, Current: {self._current}A, Power: {self._readPower}W  || Target Power: {self._global_data.get_data_targetpower_ev2()}W")
    #     return self._readPower, self._voltage, self._current

    # def limitChangeRequest(self, limitPower):
    #     """
    #     Case 1: Demand = 34kW -> Limit = 35kW -> readPower = 20kW -> Difference = 15kW
    #     Case 2: Demand = 38kW -> Limit = 35kW -> readPower = 33kW -> Difference = 2kW
    #     Case 3: Demand = 38kW -> Limit = 35kW -> readPower = 55kW -> Difference = abs(-20kW) = 20kW
    #     This means switch power only when the difference is more than 2kW both positive and negative way. If there is a drastic change in power, then we will not switch the power.
    #     """
    #     # print("INFO:: Indside Limit Change Function Gun1")
    #     realTimeVIP = self.getRealTimeVIP()
    #     # print(f"Limit Power: {limitPower}")
    #     val = abs(limitPower - realTimeVIP[0])    # 35 - 34 = 1; 35 - 36 = -1
    #     if self._global_data.get_data_targetpower_ev2() != 0:
    #     # print(f"Comparision value: Limit Power: {limitPower}, Read Power: {self._readPower}, Difference Value: {val}")
    #         if val <= 2000:  # 2kW
    #             self.limitChangeRequested = True
    #         else:
    #             self.limitChangeRequested = False
    #     else:
    #         self.limitChangeRequested = False

    #     print(f"Gun2 :: LP: {limitPower}, RP: {self._readPower}, DP: {self._global_data.get_data_targetpower_ev2()}, SLP: {min(setter.getSetLimit2(), self._global_data.get_data_targetpower_ev2())}, Diff: {val}, ChangeRequest: {self.limitChangeRequested}")

    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        print("Inside read_input_data of Vehicle-2 status")
        vs2 = self._binary_data
        self._global_data.set_data_status_vehicle2(binaryToDecimal(int(vs2[0])))
        # vehicle_status2 = binaryToDecimal(int(vs2[0]))
        #print("s2=",vehicle_status2)
        # logger.info(f'Vehicle-2 status {vehicle_status2}')
        # vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        #logger.info(f'Vehicle-1 status {vehicle_status1_g}')

        # self.getRealTimeVIP()

        tag_vol2 = binaryToDecimal(int(vs2[2] + vs2[1]))
        target_volatge_from_car2 = (tag_vol2 / 10)

        tag_curr2 = binaryToDecimal(int(vs2[4] + vs2[3]))
        tag_curr22 = (tag_curr2 / 10)
        # target_current_from_car2 = (tag_curr22)

        target_power2 = int(target_volatge_from_car2 * tag_curr22)
        self._global_data.set_data_targetpower_ev2(target_power2)
        print(f"Target Voltage: {target_volatge_from_car2}, Target Current: {tag_curr22}")
        self.vehicleCharger.action()

        # def cableCheck():
        #     print("GUN2: Cable Check")
        #     cable_check_voltage2 = binaryToDecimal(int(vs2[7] + vs2[6]))

        #     if cable_check_voltage2 <= 500:
        #         mm.lowMode(CanId.CAN_ID_2)
        #     if cable_check_voltage2 > 500:
        #         mm.highMode(CanId.CAN_ID_2)

        #     mm.setVoltage(DTH.convertohex(cable_check_voltage2), CanId.CAN_ID_2)
        #     mm.startModule(CanId.CAN_ID_2)
        #     mm.readModule_Voltage(CanId.CAN_ID_2)
        #     digitl_input = self._global_data.get_data()
            
        #     if digitl_input[1] == '0' or digitl_input[2] == '1' :
        #         mm2.digital_output_led_red2()
        #         mm.stopcharging(CanId.STOP_GUN2)
        #         mm.stopModule(CanId.CAN_ID_2)
        #         PECC.STATUS1_GUN2_DATA[0] = 3

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
        #     # mm2.digital_output_led_red1()
        #     mm2.digital_output_led_red2()
        #     mm.stopcharging(CanId.STOP_GUN2)
        #     for module_id in module_ids:
        #         mm.stopModule(module_id)

        #     PECC.STATUS1_GUN2_DATA[0] = 3

        # def standByled():
        #     """
            
        #     """
        #     digitl_input = self._global_data.get_data()
        #     if len(digitl_input) != 0 :
        #         if digitl_input[1] == '0' or digitl_input[2] == '1' :
        #             PECC.STATUS1_GUN2_DATA[0] = 2
        #             mm2.digital_output_led_red2()
        #         else:
        #             PECC.STATUS1_GUN2_DATA[0] = 0
        #             mm2.digital_output_led_red2()
        #     else:
        #         PECC.STATUS1_GUN2_DATA[0] = 0
        #         mm2.digital_output_led_red2()

        # def updateVI_status(vs2):
        #     """
        #     Update the VI status of the vehicle
        #     vs2: Vehicle status
        #     """
        #     PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
        #     PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
        #     PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
        #     PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            
        # def startCharging(module_ids):
        #     """
        #     Call the startCharging function to start the charging process
        #     modue_ids: List of module IDs to be started
        #     Example:
        #     module_ids = [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
        #     """
        #     # for module_id in module_ids:
        #     #     mm.startModule(module_id)
        #     #     mm.readModule_Voltage(module_id)
        #     #     mm.readModule_Current(module_id)

        #     if target_volatge_from_car2 <= 500:
        #         for module_id in module_ids:
        #             mm.lowMode(module_id)

        #     elif target_volatge_from_car2 > 500:
        #         for module_id in module_ids:
        #             mm.highMode(module_id)

        #     RUNNING_CURRENT = (target_current_from_car2/len(module_ids))
        #     self._global_data.set_data_running_current(RUNNING_CURRENT)
        #     for module_id in module_ids:
        #         mm.setVoltage(DTH.convertohex(target_volatge_from_car2), module_id)
        #         mm.setCurrent(module_id)
        #         mm.startModule(module_id)
        #         mm.readModule_Current(module_id)

        #     mm.readModule_Voltage(module_ids[0])  # Read and update the voltage of the first module

        #     # Handle error conditions here
        #     digitl_input = self._global_data.get_data()
        #     if digitl_input[1] == '0' or digitl_input[2] == '1' :
        #         handleError(module_ids)

        # def stopActiveModules(module_ids):
        #     for module_id in module_ids:
        #         mm.stopModule(module_id)

        # self.vehicleCharger.read_data()
