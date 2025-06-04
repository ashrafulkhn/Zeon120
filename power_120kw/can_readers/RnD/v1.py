from module_assignment import ModuleSetter as ms
import random
from time import sleep

def read_data():
    ev1_status = 29
    # demand1 = 30500 # The demand can be from 0 to 120kW
    # demand2 = 30000
    while True:
        demand1 = random.randint(29000, 31000)
        demand2 = random.randint(59000, 61000)

        if ev1_status in [13, 21, 29]:
            ms.assign_modules(demand1, demand2)
            G1_Mod = ms.getG1_modules()
            # print(G1_Mod)
            G2_Mod = ms.getG2_modules()
            # print(G2_Mod)
            print(f"G1 Demand: {demand1/1000}kW, Assigned Module: {G1_Mod}, G2 Demand: {demand2/1000}kW, Assigned Module: {G2_Mod}")
        sleep(2)

def main():
    print("Entering the main code.")
    read_data()

if __name__ == "__main__":
    main()