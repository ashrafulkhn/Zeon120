from RnD.module_assignment import ModuleSetter as ms
from RnD.module_assignment import Module
from power_120kw.constant_manager_120kw import ConstantManager120KW as cm
import random
from time import sleep
import time
from base_reader import BaseReader
from constants import PECC, CanId

class VehicleCharger():
    # arbitration_id = 769
    def __init__(self):
        self.max_power_of_charger = 120000   # This value should be captured from config.ini file. This will be updated by the server person from GUI.
        self.MIN_MODULE_POWER = self.max_power_of_charger/len(Module.TOTAL_MODULE)

    def get_effective_demand(self, status, demand, min_module_power):
        if status in [0, 35, 37]:
            return 0
        elif status in [2, 13]:
            demand = random.randint(0,0)
            return max(demand, min_module_power)
        else:
            return demand
    
    def read_data(self):
        # The EV status to be collected from eVSEC device. In our case via CAN data. Remove this static data from deployment code.
        # ev1_status = 29
        # ev2_status = 29
        ev1_status = cm.get_data_status_vehicle1()
        ev2_status = cm.get_data_status_vehicle2()

        # while True:
            # random_demand1 = random.randint(0, 0)
            # random_demand2 = random.randint(0, 0)

        demand_power_vehicle1 = cm.get_data_targetpower_ev1() if demand_power_vehicle1 > 0 else 0
        demand_power_vehicle2 = cm.get_data_targetpower_ev2() if demand_power_vehicle1 > 0 else 0

        demand1 = self.get_effective_demand(ev1_status, demand_power_vehicle1, self.MIN_MODULE_POWER)
        demand2 = self.get_effective_demand(ev2_status, demand_power_vehicle2, self.MIN_MODULE_POWER)

        ms.assign_modules(demand1, demand2)
        G1_Mod = ms.getG1_modules()
        G2_Mod = ms.getG2_modules()

        # if len(G1_Mod) or len(G2_Mod) > 0:
            # self.stopInactiveModules()
            # self.startCharging(G1_Mod)
            # self.startCharging(G2_Mod)
        # else:
            # self.stopAllModules()

        print(f"{time.time()}: G1-Demand: {demand1/1000}kW, G2-Demand: {demand2/1000}kW, G1-Assigned: {G1_Mod},  G2-Assigned: {G2_Mod}, Contactor: {ContactorSetter.getContactors_states()}")
        # sleep(.25)

