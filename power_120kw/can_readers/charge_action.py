from power_120kw.can_readers.allocations.module_assignment import ModuleSetter
from power_120kw.can_readers.allocations.module_assignment import Module
from power_120kw.constant_manager_120kw import ConstantManager120KW
from constants import CONTACTOR
from power_120kw.can_readers.allocations.contactor_assignement import Contactors, ContactorSetter
import random
from time import sleep
import time
from base_reader import BaseReader
from constants import PECC, CanId, CONTACTOR
from utility import DigitalOutputFrameBuilder

class VehicleCharger():
    def __init__(self):
        self.max_power_of_charger = 120000   # This value should be captured from config.ini file. This will be updated by the server person from GUI.
        self.MIN_MODULE_POWER = self.max_power_of_charger/len(Module.TOTAL_MODULE)
        self.constant_manager = ConstantManager120KW()
        self.modulesetter = ModuleSetter()
        self._contactors = ContactorSetter()

    @staticmethod
    def get_effective_demand(status, demand, min_module_power):
        if status in [0, 4, 6, 35, 37]:
            _power = 0.0
            print("Inside Condition: 0 4 6 35 37")
            return _power
        
        elif status in [2, 13]:
            demand = random.randint(0.0,0.0)
            return max(demand, min_module_power)
        else:  # 21, 29
            return demand
    
    def setDigitalOutList(self, value, index):
        CONTACTOR.DIGITAL_OUT_LIST[index] = value
        
    def action(self):
        # The EV status to be collected from eVSEC device. In our case via CAN data. Remove this static data from deployment code.
        # ev1_status = 2
        # ev2_status = 0
        ev1_status = self.constant_manager.get_data_status_vehicle1()
        ev2_status = self.constant_manager.get_data_status_vehicle2()
       
        # while True:
            # random_demand1 = random.randint(0, 0)
            # random_demand2 = random.randint(0, 0)

        demand_power_vehicle1 = self.constant_manager.get_data_targetpower_ev1() # if self.constant_manager.get_data_targetpower_ev1() > 0 else 0
        demand_power_vehicle2 = self.constant_manager.get_data_targetpower_ev2() # if self.constant_manager.get_data_targetpower_ev2() > 0 else 0

        demand1 = self.get_effective_demand(ev1_status, demand_power_vehicle1, self.MIN_MODULE_POWER)
        demand2 = self.get_effective_demand(ev2_status, demand_power_vehicle2, self.MIN_MODULE_POWER)

        self.modulesetter.assign_modules(demand1, demand2)
        print(f"{time.time()}: EV1: {ev1_status}, EV2: {ev2_status}")
        G1_Mod = self.modulesetter.getG1_modules()
        G2_Mod = self.modulesetter.getG2_modules()

        for index, (cont, state) in enumerate(self._contactors.getContactors_states().items()):
            self.setDigitalOutList(state, index)

        frame_data = DigitalOutputFrameBuilder.build_contact_status_frame(CONTACTOR.DIGITAL_OUT_LIST)
        CONTACTOR.CONTACTOR_STATUS_DATA = frame_data
        print(frame_data)

        print(f"{time.time()}: G1-Demand: {demand1/1000}kW, G2-Demand: {demand2/1000}kW, G1-Assigned: {G1_Mod},  G2-Assigned: {G2_Mod}, Contactor: {self._contactors.getContactors_states()}")
        # sleep(.25)