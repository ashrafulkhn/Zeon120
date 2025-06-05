from module_assignment import ModuleSetter as ms
import random
from time import sleep
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm
from base_reader import BaseReader
from utility import bytetobinary, binaryToDecimal, DTH
from power_120kw.constant_manager_120kw import ConstantManager120KW
from constants import PECC, CanId

class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769
    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self.target_current_from_car1 = 0
        self.target_volatge_from_car1 = 0
        self.digitl_input = 0
        self.vs1 = 0
    
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
            self.stopActiveModules(module_ids=module_id)
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

    def standByled(self):
        if len(self.digitl_input) != 0 :
            if self.digitl_input[1] == '0' or self.digitl_input[2] == '1' :
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
        assigned_modules_g1 = ms.getG1_modules()
        assigned_modules_g2 = ms.getG2_modules()

        if self.target_volatge_from_car1 <= 500:
            for module_id in module_ids:
                mm.lowMode(module_id)
        elif self.target_volatge_from_car1 > 500:
            for module_id in module_ids:
                mm.highMode(module_id)

        RUNNING_CURRENT = (self.target_current_from_car1/len(module_ids))
        self._global_data.set_data_running_current(RUNNING_CURRENT)

        for module_id in module_ids:
            voltage_value = DTH.convertohex(self.target_volatge_from_car1)
            mm.setVoltage(voltage_value, module_id)
            mm.setCurrent(module_id)
            mm.startModule(module_id)
            mm.readModule_Current(module_id)
        mm.readModule_Voltage(module_ids[0])
        
        # Handle error conditions here
        digitl_input = self._global_data.get_data()
        if digitl_input[1] == '0' or digitl_input[2] == '1'  :
            self.handleError(module_ids)

    def stopActiveModules(self, module_ids):
        # print(f"Stopping Modules {module_ids}")
        for module_id in module_ids:
            mm.stopModule(module_id)
    
    def read_input_data(self):
        #logger.info('Read input for Vehicle-1 status')
        # print("Reading input status of Vehicle 1")
        self.vs1 = self._binary_data
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

        _target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
        target_power_from_car1 = min(setter.getSetLimit1(), _target_power_from_car1)

        _target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
        target_power_from_car2 = min(setter.getSetLimit1(), _target_power_from_car2)
        

    def read_data(self):
        ev1_status = 29
        # demand1 = 30500 # The demand can be from 0 to 120kW
        # demand2 = 30000
        while True:
            demand1 = random.randint(10000, 115000)
            demand2 = random.randint(10000, 115000)

            if ev1_status in [13, 21, 29]:
                ms.assign_modules(demand1, demand2)
                G1_Mod = ms.getG1_modules()
                if G1_Mod > 0:

                    self.startCharging(G1_Mod)
                # print(G1_Mod)
                G2_Mod = ms.getG2_modules()
                # print(G2_Mod)
                print(f"G1-Demand: {demand1/1000}kW, G2-Demand: {demand2/1000}kW, G1-Assigned: {G1_Mod},  G2-Assigned: {G2_Mod}")
            sleep(0.5)

    def main():
        print("Entering the main code.")
        v1Reader = Vehicle1StatusReader
        v1Reader.read_data()

    if __name__ == "__main__":
        main()