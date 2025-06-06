from module_assignment import ModuleSetter as ms
from module_assignment import Module
import random
from time import sleep
# from power_120kw.message_helper import Module1Message as mm1, ModuleMessage as mm
# from base_reader import BaseReader
# from utility import bytetobinary, binaryToDecimal, DTH
# from power_120kw.constant_manager_120kw import ConstantManager120KW
# from constants import PECC, CanId, GunStatus

class VehicleStatusReader():
    arbitration_id = 769
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
        ev1_status = 21
        ev2_status = 29
        # demand1 = 30500 # The demand can be from 0 to 120kW
        # demand2 = 30000

        while True:
            random_demand1 = random.randint(10, 100)
            random_demand2 = random.randint(10000, 115000)

            demand1 = self.get_effective_demand(ev1_status, random_demand1, self.MIN_MODULE_POWER)
            demand2 = self.get_effective_demand(ev2_status, random_demand2, self.MIN_MODULE_POWER)

            ms.assign_modules(demand1, demand2)
            G1_Mod = ms.getG1_modules()
            G2_Mod = ms.getG2_modules()

            if len(G1_Mod) > 0:
                # self.startCharging(G1_Mod)
                pass
            # else:
                # stop

            if(len(G2_Mod) > 0):
                # self.startCharging(G2_Mod)
                pass

            print(f"G1-Demand: {demand1/1000}kW, G2-Demand: {demand2/1000}kW, G1-Assigned: {G1_Mod},  G2-Assigned: {G2_Mod}")
            sleep(0.5)

def main():
    print("Entering the main code.")
    v1Reader = VehicleStatusReader()
    v1Reader.read_data()

if __name__ == "__main__":
    main()