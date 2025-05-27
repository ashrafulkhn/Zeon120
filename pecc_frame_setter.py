# pecc_frame_setter.py

from utility import DTH
from constants import PECC

class PECCFrameSetter:
    previous_power = 0
    @staticmethod
    def setModulesLimit(power, current, gun_number):
        # Step 1: Convert power (in watts) -> scale down by 10
        power_val = int(power / 10)
        power_hex = DTH.converttohexforpecc(hex(power_val))
        PECC.__dict__[f"LIMITS1_DATA_120kw_Gun{gun_number}"][4] = power_hex[1]  # Lower byte
        PECC.__dict__[f"LIMITS1_DATA_120kw_Gun{gun_number}"][5] = power_hex[0]  # Upper byte

        # Step 2: Convert current (in amps) -> scale up by 10
        current_val = int(current * 10)
        current_hex = DTH.converttohexforpecc(hex(current_val))
        PECC.__dict__[f"LIMITS2_DATA_120kw_Gun{gun_number}"][2] = current_hex[1]  # Lower byte
        PECC.__dict__[f"LIMITS2_DATA_120kw_Gun{gun_number}"][3] = current_hex[0]  # Upper byte
        # print(f"Power: {power}, 4: {power_hex[1]}, 5: {power_hex[0]}, 2: {current_hex[1]}, 3: {current_hex[0]}")
        if (power != PECCFrameSetter.previous_power):
            print(f"Gun{gun_number}: Power Limit Set to: {power/1000} kW")
            PECCFrameSetter.previous_power = power

# Example Usage
def main():
    setter = PECCFrameSetter()
    # e.g. set 80 kW @ 250 A on Gun 1
    setter.setModulesLimit(30000, 250, 1)

if __name__ == "__main__":
    main()
