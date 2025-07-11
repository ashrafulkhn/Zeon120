# # Optimized Vehicle Status Handler for GUN2

# class VehicleStatusHandler:
#     def __init__(self, global_data, setter, mm, mm2):
#         self._global_data = global_data
#         self.setter = setter
#         self.mm = mm
#         self.mm2 = mm2
#         self.limitChangeRequested = False

#     def handle_imd_check(self, digital_input, pm2, condition_num):
#         """Common IMD status check logic"""
#         if digital_input[4] == '1':
#             self.mm2.digital_output_led_red2()
#             self.mm.stopcharging(CanId.STOP_GUN2)
#             stopActiveModules(pm2)
#             PECC.STATUS1_GUN2_DATA[0] = 9
            
#             # Different actions based on condition
#             if condition_num in [5, 8]:
#                 self.mm.digital_output_open_stop()
#                 time.sleep(5)
#                 self.mm2.digital_output_open_fan()
#             elif condition_num in [6, 9]:
#                 self.mm2.digital_output_open_load21()
#             elif condition_num in [7, 10]:
#                 self.mm2.digital_output_open_load21()
#             else:
#                 self.mm2.digital_output_open_load22()
#         else:
#             PECC.STATUS1_GUN2_DATA[0] = 5

#     def setup_basic_charging(self, power_limit, current_limit, gun_number=2):
#         """Common setup for basic charging conditions"""
#         self.setter.setModulesLimit(power_limit, current_limit, gun_number)
#         pm2 = []
#         self._global_data.set_data_pm_assign2(len(pm2))
#         digital_input = self._global_data.get_data()
#         standByled()
#         return digital_input

#     def setup_module_charging(self, power_limit, current_limit, modules, gun_number=2):
#         """Setup charging with specific modules"""
#         self.setter.setModulesLimit(power_limit, current_limit, gun_number)
#         self._global_data.set_data_pm_assign2(len(modules))
#         return modules

#     def handle_power_demand_conditions(self, target_power, pm_assign1, condition_base):
#         """Handle complex power demand conditions for condition 11-13"""
#         _target_power = self._global_data.get_data_targetpower_ev2()
#         target_power = min(self.setter.getSetLimit2(), _target_power)
        
#         # Power thresholds and corresponding actions
#         power_configs = [
#             (28000, 55000, 100, [CanId.CAN_ID_2]),
#             (32000, 58000, 200, [CanId.CAN_ID_2, CanId.CAN_ID_4]),
#             (62000, 85000, 250, [CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]),
#             (92000, 120000, 250, [CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
#         ]
        
#         for threshold, power_limit, current_limit, modules in power_configs:
#             if target_power <= threshold:
#                 return self.execute_power_config(power_limit, current_limit, modules, condition_base)
        
#         # Default case for highest power
#         return self.execute_power_config(120000, 250, power_configs[-1][3], condition_base)

#     def execute_power_config(self, power_limit, current_limit, modules, condition_base):
#         """Execute power configuration with modules"""
#         self.setter.setModulesLimit(power_limit, current_limit, gun_number=2)
#         self._global_data.set_data_pm_assign2(len(modules))
        
#         # Handle limit change requests
#         if hasattr(self, 'limitChangeRequest'):
#             self.limitChangeRequest(power_limit)
#             if self.limitChangeRequested:
#                 self.limitChangeRequested = False
        
#         startCharging(modules)
#         digital_input = self._global_data.get_data()
#         self.handle_imd_check(digital_input, modules, condition_base)

#     def process_vehicle_status(self, vehicle_status2, vehicle_status1_g, vs2):
#         """Main processing function with optimized condition handling"""
        
#         # Group conditions by similar patterns
#         standby_conditions = [
#             ((0, 0), (6, 6), (6, 0)),  # Condition 1
#             ((0, 6), (0, 2), (0, 29))  # Condition 2
#         ]
        
#         error_conditions = [
#             ((2, 0), (2, 6)),  # Condition 3
#             ((2, 13), (2, 21), (2, 2), (2, 29))  # Condition 4
#         ]
        
#         charging_prep_conditions = [
#             ((13, 0), (13, 6)),  # Condition 5
#             ((13, 2), (13, 35), (13, 37)),  # Condition 6
#             ((13, 13), (13, 21), (13, 29))  # Condition 7
#         ]
        
#         active_charging_conditions = [
#             ((21, 0), (21, 6)),  # Condition 8
#             ((21, 2), (21, 35), (21, 37)),  # Condition 9
#             ((21, 13), (21, 21), (21, 29))  # Condition 10
#         ]
        
#         # Check each condition group
#         status_pair = (vehicle_status2, vehicle_status1_g)
        
#         # Handle standby conditions (1-2)
#         for i, conditions in enumerate(standby_conditions, 1):
#             if status_pair in conditions:
#                 print(f"GUN2:: Condition {i}")
#                 if i == 1:
#                     self.mm.digital_output_open_AC()
#                 self.setup_basic_charging(120000, 250)
#                 return
        
#         # Handle error conditions (3-4)
#         for i, conditions in enumerate(error_conditions, 3):
#             if status_pair in conditions:
#                 print(f"GUN2:: Condition {i}")
#                 digital_input = self.setup_basic_charging(120000, 250)
                
#                 if i == 3:
#                     self.handle_condition_3_logic(digital_input)
#                 else:
#                     self.handle_condition_4_logic(digital_input)
#                 return
        
#         # Handle charging prep conditions (5-7)
#         for i, conditions in enumerate(charging_prep_conditions, 5):
#             if status_pair in conditions:
#                 print(f"GUN2:: Condition {i}")
#                 self.handle_charging_prep(i, vs2)
#                 return
        
#         # Handle active charging conditions (8-10)
#         for i, conditions in enumerate(active_charging_conditions, 8):
#             if status_pair in conditions:
#                 print(f"GUN2:: Condition {i}")
#                 self.handle_active_charging(i, vs2)
#                 return
        
#         # Handle complex power management conditions (11-13)
#         if vehicle_status2 == 29:
#             self.handle_power_management_conditions(vehicle_status1_g, vs2)
#             return
        
#         # Handle termination conditions (14-17)
#         if vehicle_status2 in [35, 37]:
#             self.handle_termination_conditions(vehicle_status2, vehicle_status1_g, vs2)
#             return

#     def handle_condition_3_logic(self, digital_input):
#         """Handle condition 3 specific logic"""
#         try:
#             if len(digital_input) != 0:
#                 if digital_input[1] == '0' or digital_input[2] == '1':
#                     self.mm2.digital_output_led_red2()
#                     self.mm.stopcharging(CanId.STOP_GUN2)
#                     PECC.STATUS1_GUN2_DATA[0] = 2
#                 else:
#                     self.mm2.digital_output_led_red2()
#                     self.mm.digital_output_close_AC()
#                     PECC.STATUS1_GUN2_DATA[0] = 0
#             else:
#                 self.mm2.digital_output_led_red2()
#                 self.mm.digital_output_close_AC()
#                 PECC.STATUS1_GUN2_DATA[0] = 0
#         except IndexError:
#             print("GUN2: IndexError: List index out of range. Please check the input data.")

#     def handle_condition_4_logic(self, digital_input):
#         """Handle condition 4 specific logic"""
#         self.mm2.digital_output_led_red2()
#         PECC.STATUS1_GUN2_DATA[0] = 0
#         if digital_input[1] == '0' or digital_input[2] == '1':
#             self.mm2.digital_output_led_red2()
#             self.mm.stopcharging(CanId.STOP_GUN2)
#             PECC.STATUS1_GUN2_DATA[0] = 2

#     def handle_charging_prep(self, condition_num, vs2):
#         """Handle charging preparation conditions 5-7"""
#         self.setter.setModulesLimit(120000, 250, gun_number=2)
#         updateVI_status(vs2)
#         PECC.STATUS1_GUN2_DATA[0] = 1
#         self.mm2.digital_output_led_red2()
        
#         pm2 = [CanId.CAN_ID_2]
#         self._global_data.set_data_pm_assign2(len(pm2))
        
#         # Condition-specific actions
#         if condition_num == 5:
#             self.mm2.digital_output_close_Gun21()
#         elif condition_num == 6:
#             self.mm2.digital_output_Gun2_load11()
#             stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
#         else:  # condition_num == 7
#             self.mm2.digital_output_load21()
        
#         cableCheck()
#         digital_input = self._global_data.get_data()
#         self.handle_imd_check(digital_input, pm2, condition_num)

#     def handle_active_charging(self, condition_num, vs2):
#         """Handle active charging conditions 8-10"""
#         updateVI_status(vs2)
#         self.mm2.digital_output_led_red2()
        
#         if condition_num == 8:
#             self.setter.setModulesLimit(20000, 100, gun_number=2)
#             self.mm2.digital_output_close_Gun21()
#         else:
#             self.setter.setModulesLimit(20000, 100, 2)
#             if condition_num == 9:
#                 self.mm2.digital_output_Gun2_load11()
#                 stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])
#             else:  # condition_num == 10
#                 self.mm2.digital_output_load21()
        
#         pm2 = [CanId.CAN_ID_2]
#         self._global_data.set_data_pm_assign2(len(pm2))
#         startCharging(pm2)
        
#         digital_input = self._global_data.get_data()
#         self.handle_imd_check(digital_input, pm2, condition_num)

#     def handle_power_management_conditions(self, vehicle_status1_g, vs2):
#         """Handle complex power management conditions 11-13"""
#         condition_map = {
#             (0, 6): 11,
#             (2, 35, 37): 12,
#             (13, 21, 29): 13
#         }
        
#         condition_num = None
#         for statuses, num in condition_map.items():
#             if vehicle_status1_g in statuses:
#                 condition_num = num
#                 break
        
#         if condition_num:
#             print(f"GUN2:: Condition {condition_num}")
#             updateVI_status(vs2)
#             self.mm2.digital_output_led_green2()
            
#             pm_assign1 = self._global_data.get_data_pm_assign1()
#             self.handle_power_demand_conditions(None, pm_assign1, condition_num)

#     def handle_termination_conditions(self, vehicle_status2, vehicle_status1_g, vs2):
#         """Handle termination conditions 14-17"""
#         condition_map = {
#             (35, 37): {
#                 (0, 6): 14,
#                 (35, 37): 15,
#                 (2, 13, 21, 29): 16 if vehicle_status2 == 37 else 17
#             }
#         }
        
#         print(f"GUN2:: Condition {14 + (vehicle_status1_g in [35, 37]) + (vehicle_status1_g in [2, 13, 21, 29]) * 2}")
        
#         self.mm2.digital_output_led_red2()
#         updateVI_status(vs2)
        
#         if vehicle_status1_g in [0, 6, 35, 37]:
#             stopActiveModules([CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4])
#         else:
#             pm_assign2 = self._global_data.get_data_pm_assign2()
#             modules_to_stop = {
#                 1: [CanId.CAN_ID_2],
#                 2: [CanId.CAN_ID_2, CanId.CAN_ID_4],
#                 3: [CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
#             }
#             stopActiveModules(modules_to_stop.get(pm_assign2, []))
        
#         self.mm.readModule_Voltage(CanId.CAN_ID_2)
#         self.mm.readModule_Current(CanId.CAN_ID_2)
#         PECC.STATUS1_GUN2_DATA[0] = 1


# # Usage example:
# def optimized_vehicle_status_handler(vehicle_status2, vehicle_status1_g, vs2, global_data, setter, mm, mm2):
#     """Optimized main handler function"""
#     handler = VehicleStatusHandler(global_data, setter, mm, mm2)
#     handler.process_vehicle_status(vehicle_status2, vehicle_status1_g, vs2)