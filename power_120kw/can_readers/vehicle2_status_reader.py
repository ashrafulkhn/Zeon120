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
        print(f"Real-time Voltage: {self._voltage}V, Current: {self._current}A, Power: {self._readPower}W  || Target Power: {self._global_data.get_data_targetpower_ev1()}W")
        return self._readPower, self._voltage, self._current
    
    def limitChangeRequest(self, limitPower):
        """
        Case 1:
        Demand = 34kW -> Limit = 35kW -> readPower = 20kW -> Difference = 15kW
        Case 2:
        Demand = 38kW -> Limit = 35kW -> readPower = 33kW -> Difference = 2kW
        Case 3:
        Demand = 38kW -> Limit = 35kW -> readPower = 55kW -> Difference = abs(-20kW) = 20kW

        This means switch power only when the difference is more than 2kW both positive and negative way. If there is a drastic change in power, then we will not switch the power.
        """
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

        maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
        maxpowerev2_g = self._global_data.get_data_maxpower_ev2()

        def funct_40_cc2():
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
            
        def startCharging(module_ids):
            """
            Call the startCharging function to start the charging process
            modue_ids: List of module IDs to be started
            Example:
            module_ids = [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4]
            """
            for module_id in module_ids:
                mm.startModule(module_id)
                mm.readModule_Voltage(module_id)
                mm.readModule_Current(module_id)

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

        if vehicle_status2 == 0 and vehicle_status1_g == 0 or vehicle_status2 == 6 and vehicle_status1_g == 6 or vehicle_status2 == 6 and vehicle_status1_g == 0:
            mm.digital_output_open_AC()
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 11
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1'  or digitl_input[7] == '0':
                    mm2.digital_output_led_red2()
                    PECC.STATUS1_GUN2_DATA[0] = 2
                else:
                    mm2.digital_output_led_green2()
                    PECC.STATUS1_GUN2_DATA[0] = 0
            else:
                mm2.digital_output_led_green2()
                PECC.STATUS1_GUN2_DATA[0] = 0   

        if vehicle_status2 == 0 and vehicle_status1_g == 6 or vehicle_status2 == 0 and vehicle_status1_g == 2 or vehicle_status2 == 0 and vehicle_status1_g == 29:
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 11
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)
            digitl_input = self._global_data.get_data()
            if len(digitl_input) != 0 :
                if digitl_input[1] == '0' or digitl_input[2] == '1'  or digitl_input[7] == '0':
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
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 11      
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)    
            digitl_input = self._global_data.get_data()
            try:
                if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    PECC.STATUS1_GUN2_DATA[0] = 2
                
                else:
                    mm2.digital_output_led_green2()
                    mm.digital_output_close_AC()
                    PECC.STATUS1_GUN2_DATA[0] = 0 
            except IndexError:
                print("Error")
        
        if vehicle_status2 == 2 and vehicle_status1_g != 0 or vehicle_status2 == 2 and vehicle_status1_g != 6:
            """
            Condition Needs to be Verified
            """
            # maxpowerev1_g = self._global_data.get_data_maxpower_ev1()         
            # maxpowerev2_g = self._global_data.get_data_maxpower_ev2()         
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 11      
            pm2=0
            self._global_data.set_data_pm_assign2(pm2)    
            digitl_input = self._global_data.get_data()
            if digitl_input[1] == '0' or digitl_input[2] == '1' or digitl_input[7] == '0':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
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
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 11
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
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)
            mm2.digital_output_Gun2_load11()
            funct_40_cc2()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()
                

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5


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
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            mm2.digital_output_load21()
            funct_40_cc2()
            digitl_input = self._global_data.get_data()
            if digitl_input[4] == '1':
                mm2.digital_output_led_red2()
                mm.stopcharging(CanId.STOP_GUN2)
                mm.stopModule(CanId.CAN_ID_2)                
                PECC.STATUS1_GUN2_DATA[0] = 9
                mm2.digital_output_open_load21()

            if digitl_input[4] == '0':
                PECC.STATUS1_GUN2_DATA[0] = 5

               
                

        if vehicle_status2 == 21 and vehicle_status1_g == 0 or vehicle_status2 == 21 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm2.digital_output_led_green2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            pm2=1
            self._global_data.set_data_pm_assign2(pm2)
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 5
            mm2.digital_output_close_Gun21()
            startCharging([CanId.CAN_ID_2])

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
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            
            mm2.digital_output_led_green2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()

            
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 5

            mm.stopModule(CanId.CAN_ID_1)
            mm.stopModule(CanId.CAN_ID_3)
            mm.stopModule(CanId.CAN_ID_4)

            mm2.digital_output_Gun2_load11()

            pm2=1
            self._global_data.set_data_pm_assign2(pm2)

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
                
        if vehicle_status2 == 21 and vehicle_status1_g == 13 or vehicle_status2 == 21 and vehicle_status1_g == 21 or vehicle_status2 == 21 and vehicle_status1_g == 29:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            mm2.digital_output_led_green2()
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            
            PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
            PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
            PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
            PECC.LIMITS2_DATA_120kw_Gun2[3] = 5
            mm2.digital_output_load21()

            pm2=1
            self._global_data.set_data_pm_assign2(pm2)

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

                

        if vehicle_status2 == 29 and vehicle_status1_g == 0 or vehicle_status2 == 29 and vehicle_status1_g == 6:
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))

            mm2.digital_output_led_blue2()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            #self._global_data.set_data_maxpower2(maxpowerev2_g)
            
            """
            We are removing the check for maxpowerev1_g as we are doing the check based onj the target power power from car
            """

            if target_power_from_car2 <= 38000:
                # Set Limit to 35kW
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 172
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 13
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9

                pm2=[CanId.CAN_ID_2]
                # pm_assign2 = self._global_data.set_data_pm_assign2(pm2)
                self._global_data.set_data_pm_assign2(pm2)

                mm2.digital_output_close_Gun21()
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                
                # Check the realtime votage and current
                
                self.limitChangeRequest(35000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm2.digital_output_close_Gun21()
                    # funct_40_1()
                    startCharging([CanId.CAN_ID_2])

                else:
                    # set limit to 75kW
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 76
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 29
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 75kW.")

                digitl_input = self._global_data.get_data()

                # IMD Status Check
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
                
            if target_power_from_car2 > 38000 and target_power_from_car2 < 42000:
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 1):
                    mm2.digital_output_close_Gun21()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    startCharging([CanId.CAN_ID_2])

                elif (pm_assign2 == 2):
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    startCharging([CanId.CAN_ID_2,CanId.CAN_ID_4])

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
                
            if target_power_from_car2 >= 42000 and target_power_from_car2 <= 78000:
                
                pm2=[CanId.CAN_ID_2,CanId.CAN_ID_4]
                # pm_assign2 = self._global_data.set_data_pm_assign2(pm2)
                self._global_data.set_data_pm_assign2(pm2)

                mm2.digital_output_close_Gun22()    # Closing contactors for 2 modules for Gun2
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                
                self.limitChangeRequest(75000)  # Updates the limitChangeRequested variable to true if the limit is reached

                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm2.digital_output_close_Gun22()
                    # funct_80_1()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                else:
                    # set limit to 115kW
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 236
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 44
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 75kW.")
                
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

            if target_power_from_car2 > 78000 and target_power_from_car2 < 82000:
                
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    mm2.digital_output_close_Gun22()
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
                elif (pm_assign2 == 3):
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3,CanId.CAN_ID_4])
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
                
            if target_power_from_car2 >= 82000 and target_power_from_car2 <= 118000:
                pm2=[CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                # pm_assign2 = self._global_data.set_data_pm_assign2(pm2)
                self._global_data.set_data_pm_assign2(pm2)

                mm2.digital_output_close_Gun23()
                mm.stopModule(CanId.CAN_ID_1)


                self.limitChangeRequest(115000)  # Updates the limitChangeRequested variable to true if the limit is reached
                if (self.limitChangeRequested == False):
                    print(f"INFO: Limit change requested: {self.limitChangeRequested}")
                    mm2.digital_output_close_Gun23()
                    # funct_120_1()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                else:
                    # set limit to 160kW
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 128
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 62
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 134
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 11
                    self.limitChangeRequested = False
                    print(f"INFO: Limit changed to 160kW.")
               
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
                
            if target_power_from_car2 > 118000 and target_power_from_car2 < 122000:
                
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 3):
                    mm2.digital_output_close_Gun23()
                    mm.stopModule(CanId.CAN_ID_1)
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                elif (pm_assign2 == 4):
                    mm2.digital_output_close_Gun24()
                    startCharging([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4, CanId.CAN_ID_1])
                
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

            if target_power_from_car2 >= 122000:
                mm2.digital_output_close_Gun24()
                pm2=[CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
                self._global_data.set_data_pm_assign2(pm2)
                startCharging([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
                
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
            pm_assign1 = self._global_data.get_data_pm_assign1()
            if (target_power_from_car2 <= 38000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 5
                pm2=1
                self._global_data.set_data_pm_assign2(pm2)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm.stopModule(CanId.CAN_ID_4)
                mm2.digital_output_Gun2_load11()
                # funct_40_2()
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
                
            if 38000 < target_power_from_car2 <= 42000 :
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm.stopModule(CanId.CAN_ID_4)
                    mm2.digital_output_Gun2_load11()
                    # funct_40_2()
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
                elif(pm_assign2 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    # funct_80_2()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])

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

            if (42000 < target_power_from_car2 <= 78000):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                pm2=2
                self._global_data.set_data_pm_assign2(pm2)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_Gun2_load12()
                # funct_80_2()
                startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
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

            if (78000 < target_power_from_car2 <= 82000 and pm_assign1 == 1) or (78000 < target_power_from_car2 <= 82000 and target_power_from_car1 <= 38000):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    # funct_80_2()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
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
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    
                    mm.stopModule(CanId.CAN_ID_1)
                    mm2.digital_output_Gun2_load13()
                    # funct_120_2()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])

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

            if (78000 < target_power_from_car2 <= 82000 and pm_assign1 == 2) or (78000 < target_power_from_car2 <= 82000 and pm_assign1 == 3):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    # funct_80_2() 
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
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
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm.stopModule(CanId.CAN_ID_1)
                    mm.stopModule(CanId.CAN_ID_3)
                    mm2.digital_output_Gun2_load12()
                    # funct_80_2()
                    startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4])
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

            if (target_power_from_car2 > 82000 and target_power_from_car1 <= 38000) or (target_power_from_car2 > 82000 and pm_assign1 == 1):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                pm2=3
                self._global_data.set_data_pm_assign2(pm2)
                mm.stopModule(CanId.CAN_ID_1)
                mm2.digital_output_Gun2_load13()
                # funct_120_2()
                startCharging([CanId.CAN_ID_2, CanId.CAN_ID_4, CanId.CAN_ID_3])
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

            if (target_power_from_car2 > 82000 and pm_assign1 == 2) or (target_power_from_car2 > 82000 and pm_assign1 == 3):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
               
                pm2=2
                self._global_data.set_data_pm_assign2(pm2)
                mm.stopModule(CanId.CAN_ID_1)
                mm.stopModule(CanId.CAN_ID_3)
                mm2.digital_output_Gun2_load12()
                # funct_80_2()
                startCharging(CanId.CAN_ID_2,CanId.CAN_ID_4)
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
            mm2.digital_output_led_blue2()
            PECC.STATUS1_GUN2_DATA[2] = binaryToDecimal(int(vs2[2]))
            PECC.STATUS1_GUN2_DATA[1] = binaryToDecimal(int(vs2[1]))
            PECC.STATUS1_GUN2_DATA[3] = binaryToDecimal(int(vs2[3]))
            PECC.STATUS1_GUN2_DATA[4] = binaryToDecimal(int(vs2[4]))
            maxpowerev1_g = self._global_data.get_data_maxpower_ev1()
            maxpowerev2_g = self._global_data.get_data_maxpower_ev2()
            target_power_from_car1 = self._global_data.get_data_targetpower_ev1()
            target_power_from_car2 = self._global_data.get_data_targetpower_ev2()
            pm_assign1 = self._global_data.get_data_pm_assign1()
            if (target_power_from_car2 <= 38000 and pm_assign1 == 1) or (target_power_from_car2 <= 38000 and pm_assign1 == 2) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 5
                mm2.digital_output_load21()
                mm.stopModule(CanId.CAN_ID_4)
                pm2=1
                self._global_data.set_data_pm_assign2(pm2)
                # funct_40_2()
                startCharging(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5
            if (target_power_from_car2 <= 38000 and pm_assign1 == 3) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 160
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 15
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 50
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 5
                mm2.digital_output_load21()
                pm2=1
                self._global_data.set_data_pm_assign2(pm2)
                # funct_40_2()
                startCharging(CanId.CAN_ID_2)
                digitl_input = self._global_data.get_data()
                if digitl_input[4] == '1':
                    mm2.digital_output_led_red2()
                    mm.stopcharging(CanId.STOP_GUN2)
                    mm.stopModule(CanId.CAN_ID_2)                
                    PECC.STATUS1_GUN2_DATA[0] = 9
                    mm2.digital_output_open_load21()

                if digitl_input[4] == '0':
                    PECC.STATUS1_GUN2_DATA[0] = 5

            if 38000 < target_power_from_car2 <= 42000 :
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 1):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load21()
                    # funct_40_2()
                    startCharging(CanId.CAN_ID_2)
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
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load22()
                    # funct_80_2()
                    startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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

            if 42000 < target_power_from_car2 <= 78000:
                pm2=2
                self._global_data.set_data_pm_assign2(pm2)
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                mm2.digital_output_load22()
                # funct_80_2()
                startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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

            if (78000 < target_power_from_car2 <= 82000 and pm_assign1 == 1) or (78000 < target_power_from_car2 <= 82000 and target_power_from_car1 <= 38000) :
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load22()
                    # funct_80_2()
                    startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load23()
                    # funct_120_2()
                    startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4, CanId.CAN_ID_3)
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

            if (78000 < target_power_from_car2 <= 82000 and pm_assign1== 2) or (78000 < target_power_from_car2 <= 82000 and pm_assign1 == 3):
                pm_assign2 = self._global_data.get_data_pm_assign2()
                if (pm_assign2 == 2):
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load22()
                    # funct_80_2()
                    startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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
                    PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                    PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                    PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                    PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                    mm2.digital_output_load22()
                    # funct_80_2()
                    startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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
                    
         
            if (target_power_from_car2 > 82000 and target_power_from_car1 <= 38000) or (target_power_from_car2 > 82000 and pm_assign1 == 1):
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 224
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 46
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                pm2=3
                self._global_data.set_data_pm_assign2(pm2)
                mm2.digital_output_load23()
                # funct_120_2()
                startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4, CanId.CAN_ID_3)
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

            if (target_power_from_car2 > 82000 and pm_assign1 == 2) or (target_power_from_car2 > 82000 and pm_assign1 == 3) or (target_power_from_car2 > 82000 and target_power_from_car1 > 42000) :
                PECC.LIMITS1_DATA_120kw_Gun2[4] = 64
                PECC.LIMITS1_DATA_120kw_Gun2[5] = 31
                PECC.LIMITS2_DATA_120kw_Gun2[2] = 196
                PECC.LIMITS2_DATA_120kw_Gun2[3] = 9
                mm2.digital_output_load22()
                pm2=2
                self._global_data.set_data_pm_assign2(pm2)
                # funct_80_2()
                startCharging(CanId.CAN_ID_2, CanId.CAN_ID_4)
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
                mm.readModule_Current(CanId.CAN_ID_3)
                mm.readModule_Current(CanId.CAN_ID_4)
            PECC.STATUS1_GUN2_DATA[0] = 1
          
