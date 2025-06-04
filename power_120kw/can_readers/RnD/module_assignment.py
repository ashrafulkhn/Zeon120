# from constants import CanId as CanId


class Module:
    G1_MODULE = []
    G2_MODULE = []
    TOTAL_MODULE = ["CAN_ID_1", 
                    "CAN_ID_2", 
                    "CAN_ID_3", 
                    "CAN_ID_4"]

class ModuleSetter:
    def setG1_modules():
        # Wrtie logic to set modules list for Gun1
        for module in Module.TOTAL_MODULE:
            if len(Module.G2_MODULE) ==0:
                if module not in Module.G2_MODULE:
                    Module.G1_MODULE.append(module)

    def getG1_modules():
        return Module.G1_MODULE


def read_data():
    ev_status = 0
    module_setter = ModuleSetter
    if ev_status == 0:
        module_setter.setG1_modules()
        G1_Mod = module_setter.getG1_modules()
        print(G1_Mod)

def main():
    print("Entering the main code.")
    read_data()

if __name__ == "__main__":
    main()