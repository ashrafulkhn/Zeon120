import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional

from base_reader import BaseReader
from constants import PECC, CanId
from power_120kw.constant_manager_120kw import ConstantManager120KW
from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm
from utility import bytetobinary, binaryToDecimal, DTH
from pecc_frame_setter import PECCFrameSetter as setter

# Constants
POWER_LIMIT_BUFFER = 2000  # 2kW buffer for limit changes
MAX_RETRIES = 3
MODULE_ASSIGNMENTS = {
    1: [CanId.CAN_ID_1],
    2: [CanId.CAN_ID_1, CanId.CAN_ID_3],
    3: [CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4],
    4: [CanId.CAN_ID_1, CanId.CAN_ID_2, CanId.CAN_ID_3, CanId.CAN_ID_4]
}

# Enums
class VehicleState(Enum):
    NOT_CONNECTED = 0
    CONNECTED = 2
    DISCONNECTED = 6
    CABLE_CHECK = 13
    PRE_CHARGE = 21
    CHARGING = 29
    SESSION_STOP = 35
    ERROR = 37

class ChargingMode(Enum):
    LOW = auto()
    HIGH = auto()

@dataclass
class PowerDemand:
    min_power: int
    max_power: int
    limit: int
    modules_needed: int

class Vehicle1StatusReader(BaseReader):
    arbitration_id = 769

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._binary_data = bytetobinary(data)
        self._voltage = 0
        self._current = 0
        self._read_power = 0
        self.limit_change_retries = 0
        self.current_mode: Optional[ChargingMode] = None

    def get_real_time_vip(self) -> tuple:
        """Return real-time voltage, current and power"""
        s2g1d = bytetobinary(PECC.STATUS2_GUN1_DATA)
        voltage_pre = binaryToDecimal(int(s2g1d[1] + s2g1d[0]))
        self._voltage = voltage_pre / 10
        current_pre = binaryToDecimal(int(s2g1d[3] + s2g1d[2]))
        self._current = current_pre / 10
        self._read_power = int(self._voltage * self._current)
        return self._read_power, self._voltage, self._current

    def check_limit_change(self, limit_power: int) -> bool:
        """Check if power limit needs adjustment"""
        difference = abs(limit_power - self._read_power)
        return difference <= POWER_LIMIT_BUFFER

    def set_charging_mode(self, voltage: float):
        """Set charging mode based on target voltage"""
        new_mode = ChargingMode.LOW if voltage <= 500 else ChargingMode.HIGH
        if new_mode != self.current_mode:
            self.current_mode = new_mode
            return True
        return False

    def handle_error(self, module_ids: List[CanId]):
        """Handle error conditions and stop charging"""
        mm1.digital_output_led_red1()
        mm.stopcharging(CanId.STOP_GUN1)
        self.stop_active_modules(module_ids)
        PECC.STATUS1_GUN1_DATA[0] = 3

    def stop_active_modules(self, module_ids: List[CanId]):
        """Stop specified modules gracefully"""
        for module_id in module_ids:
            mm.stopModule(module_id)

    def start_charging(self, module_ids: List[CanId], target_voltage: float, target_current: float):
        """Start charging with specified modules"""
        if self.set_charging_mode(target_voltage):
            mode = mm.lowMode if self.current_mode == ChargingMode.LOW else mm.highMode
            for module_id in module_ids:
                mode(module_id)

        running_current = target_current / len(module_ids)
        self._global_data.set_data_running_current(running_current)

        for module_id in module_ids:
            mm.setVoltage(DTH.convertohex(target_voltage), module_id)
            mm.setCurrent(module_id)
            mm.startModule(module_id)
            mm.readModule_Current(module_id)

        mm.readModule_Voltage(module_ids[0])

        # Check for errors after starting
        digitl_input = self._global_data.get_data()
        if any((digitl_input[1] == '0', digitl_input[2] == '1', digitl_input[7] == '0')):
            self.handle_error(module_ids)

    def update_vi_status(self, vs1: str):
        """Update voltage and current status"""
        PECC.STATUS1_GUN1_DATA[2] = binaryToDecimal(int(vs1[2]))
        PECC.STATUS1_GUN1_DATA[1] = binaryToDecimal(int(vs1[1]))
        PECC.STATUS1_GUN1_DATA[3] = binaryToDecimal(int(vs1[3]))
        PECC.STATUS1_GUN1_DATA[4] = binaryToDecimal(int(vs1[4]))

    def handle_demand_condition(self, demand: PowerDemand, target_power: int):
        """Handle power demand with limit checking and module assignment"""
        if demand.min_power <= target_power <= demand.max_power:
            modules = MODULE_ASSIGNMENTS[demand.modules_needed]
            self._global_data.set_data_pm_assign1(len(modules))
            
            if not self.check_limit_change(demand.limit):
                setter.setModulesLimit(demand.limit, 250, gun_number=1)
                self.start_charging(modules, 
                                  self._global_data.get_data_target_voltage_ev1(),
                                  self._global_data.get_data_target_current_ev1())
            else:
                if self.limit_change_retries < MAX_RETRIES:
                    self.limit_change_retries += 1
                else:
                    # Fallback to lower power mode
                    self.handle_demand_condition(
                        PowerDemand(38000, 42000, 40000, 1), 
                        40000
                    )

    def read_input_data(self):
        vs1 = self._binary_data
        vehicle_status1 = VehicleState(binaryToDecimal(int(vs1[0])))
        vehicle_status2 = VehicleState(self._global_data.get_data_status_vehicle2())

        # Update real-time measurements
        self.get_real_time_vip()

        # Extract target values from vehicle
        tag_vol1 = binaryToDecimal(int(vs1[2] + vs1[1]))
        target_voltage = tag_vol1 / 10
        tag_curr1 = binaryToDecimal(int(vs1[4] + vs1[3]))
        target_current = tag_curr1 / 10
        target_power = int(target_voltage * target_current)
        self._global_data.set_data_targetpower_ev1(target_power)

        # Main state machine
        if vehicle_status1 == VehicleState.NOT_CONNECTED:
            self.handle_not_connected(vehicle_status2)
        elif vehicle_status1 == VehicleState.CONNECTED:
            self.handle_connected(vehicle_status2)
        elif vehicle_status1 == VehicleState.CABLE_CHECK:
            self.handle_cable_check(vehicle_status2, vs1)
        elif vehicle_status1 == VehicleState.PRE_CHARGE:
            self.handle_pre_charge(vehicle_status2, vs1)
        elif vehicle_status1 == VehicleState.CHARGING:
            self.handle_charging(vehicle_status2, vs1, target_power)
        elif vehicle_status1 in (VehicleState.SESSION_STOP, VehicleState.ERROR):
            self.handle_fault_condition(vehicle_status2, vs1)

    def handle_not_connected(self, vehicle_status2: VehicleState):
        """Handle not connected state"""
        mm.digital_output_open_AC()
        setter.setModulesLimit(160000, 250, 1)
        self._global_data.set_data_pm_assign1(0)
        self.set_led_status()

    def handle_connected(self, vehicle_status2: VehicleState):
        """Handle connected state"""
        setter.setModulesLimit(160000, 250, gun_number=1)
        self._global_data.set_data_pm_assign1(0)
        self.set_led_status()

    def handle_cable_check(self, vehicle_status2: VehicleState, vs1: str):
        """Handle cable check state"""
        self.update_vi_status(vs1)
        PECC.STATUS1_GUN1_DATA[0] = 1
        mm1.digital_output_led_green1()

        if vehicle_status2 in (VehicleState.NOT_CONNECTED, VehicleState.DISCONNECTED):
            mm1.digital_output_close_Gun11()
        elif vehicle_status2 == VehicleState.CONNECTED:
            mm1.digital_output_Gun1_load21()

        pm1 = [CanId.CAN_ID_1]
        self._global_data.set_data_pm_assign1(len(pm1))
        self.perform_cable_check(vs1)

    def perform_cable_check(self, vs1: str):
        """Perform cable check procedure"""
        cable_check_voltage = binaryToDecimal(int(vs1[7] + vs1[6]))
        self.set_charging_mode(cable_check_voltage)
        mm.setVoltage(DTH.convertohex(cable_check_voltage), CanId.CAN_ID_1)
        mm.startModule(CanId.CAN_ID_1)
        mm.readModule_Voltage(CanId.CAN_ID_1)

        digitl_input = self._global_data.get_data()
        if digitl_input[3] == '1':
            self.handle_error([CanId.CAN_ID_1])
        else:
            PECC.STATUS1_GUN1_DATA[0] = 5

    def handle_pre_charge(self, vehicle_status2: VehicleState, vs1: str):
        """Handle pre-charge state"""
        self.update_vi_status(vs1)
        setter.setModulesLimit(40000, 133, gun_number=1)
        mm1.digital_output_led_green1()

        if vehicle_status2 in (VehicleState.NOT_CONNECTED, VehicleState.DISCONNECTED):
            mm1.digital_output_close_Gun11()
        elif vehicle_status2 == VehicleState.CONNECTED:
            mm1.digital_output_Gun1_load21()

        pm1 = [CanId.CAN_ID_1]
        self._global_data.set_data_pm_assign1(len(pm1))
        self.start_charging(pm1, 
                          self._global_data.get_data_target_voltage_ev1(),
                          self._global_data.get_data_target_current_ev1())

    def handle_charging(self, vehicle_status2: VehicleState, vs1: str, target_power: int):
        """Handle charging state with power demand conditions"""
        self.update_vi_status(vs1)
        mm1.digital_output_led_blue1()

        # Define power demand conditions
        demand_conditions = [
            PowerDemand(0, 38000, 35000, 1),
            PowerDemand(38001, 42000, 75000, 1 if self._global_data.get_data_pm_assign1() == 1 else 2),
            PowerDemand(42001, 78000, 75000, 2),
            PowerDemand(78001, 82000, 115000, 2 if self._global_data.get_data_pm_assign1() == 2 else 3),
            PowerDemand(82001, 118000, 115000, 3),
            PowerDemand(118001, 122000, 160000, 3 if self._global_data.get_data_pm_assign1() == 3 else 4),
            PowerDemand(122001, float('inf'), 160000, 4)
        ]

        for condition in demand_conditions:
            if condition.min_power <= target_power <= condition.max_power:
                self.handle_demand_condition(condition, target_power)
                break

    def handle_fault_condition(self, vehicle_status2: VehicleState, vs1: str):
        """Handle fault conditions"""
        mm1.digital_output_led_red1()
        self.update_vi_status(vs1)
        
        pm_assign1 = self._global_data.get_data_pm_assign1()
        if pm_assign1 == 1:
            self.stop_active_modules([CanId.CAN_ID_1])
        elif pm_assign1 == 2:
            self.stop_active_modules([CanId.CAN_ID_1, CanId.CAN_ID_3])
        elif pm_assign1 == 3:
            self.stop_active_modules([CanId.CAN_ID_1, CanId.CAN_ID_3, CanId.CAN_ID_4])

        mm.readModule_Voltage(CanId.CAN_ID_1)
        PECC.STATUS1_GUN1_DATA[0] = 1

    def set_led_status(self):
        """Set LED status based on digital inputs"""
        digitl_input = self._global_data.get_data()
        if digitl_input and any((digitl_input[1] == '0', digitl_input[2] == '1', digitl_input[7] == '0')):
            mm1.digital_output_led_red1()
            PECC.STATUS1_GUN1_DATA[0] = 2
        else:
            mm1.digital_output_led_green1()
            PECC.STATUS1_GUN1_DATA[0] = 0