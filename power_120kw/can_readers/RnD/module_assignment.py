class Module:
    G1_MODULE = []
    G2_MODULE = []
    TOTAL_MODULE = [
        "CAN_ID_1",
        "CAN_ID_3",
        "CAN_ID_4",
        "CAN_ID_2"
    ]

    MODULE_POWER = 30000  # Each module can serve 30kW (example)
    # Hysteresis state
    _last_g1_count = None
    _last_g2_count = None
    _pending_g1_count = None
    _pending_g2_count = None
    _pending_cycles = 0
    _hysteresis_cycles = 3  # Number of cycles to wait before switching

class Contactors:
    G1_Contactors = []
    G2_Contactors = []
    contactor_states = {}
    TOTAL_CONTACTORS = [
        "CON1",
        "CON3",
        "CON5",
        "CON4",
        "CON2",
    ]

class ModuleSetter:
    @staticmethod
    def assign_modules(demand1, demand2):
        total_modules = len(Module.TOTAL_MODULE)
        modules_needed_g1 = int((demand1 + Module.MODULE_POWER - 1) // Module.MODULE_POWER if demand1 > 0 else 0)
        modules_needed_g2 = int((demand2 + Module.MODULE_POWER - 1) // Module.MODULE_POWER if demand2 > 0 else 0)

        # Proportional assignment if not enough modules
        if modules_needed_g1 + modules_needed_g2 > total_modules:
            total_demand = demand1 + demand2
            if total_demand == 0:
                g1_count = 0
                g2_count = 0
            else:
                g1_count = max(1 if demand1 > 0 else 0, int(round((demand1 / total_demand) * total_modules)))
                g2_count = max(1 if demand2 > 0 else 0, total_modules - g1_count)
                # If rounding causes over-allocation, adjust
                if g1_count + g2_count > total_modules:
                    if g1_count > g2_count:
                        g1_count -= 1
                    else:
                        g2_count -= 1
        else:
            g1_count = modules_needed_g1
            g2_count = modules_needed_g2

        # Hysteresis logic
        if (Module._last_g1_count is None) or (Module._last_g2_count is None):
            # First run, assign directly
            Module._last_g1_count = g1_count
            Module._last_g2_count = g2_count
            Module._pending_g1_count = g1_count
            Module._pending_g2_count = g2_count
            Module._pending_cycles = 0
        elif (g1_count != Module._last_g1_count) or (g2_count != Module._last_g2_count):
            # Proposed change
            if (g1_count == Module._pending_g1_count) and (g2_count == Module._pending_g2_count):
                Module._pending_cycles += 1
            else:
                Module._pending_g1_count = g1_count
                Module._pending_g2_count = g2_count
                Module._pending_cycles = 1
            if Module._pending_cycles >= Module._hysteresis_cycles:
                Module._last_g1_count = g1_count
                Module._last_g2_count = g2_count
                Module._pending_cycles = 0
        else:
            # No change needed
            Module._pending_g1_count = g1_count
            Module._pending_g2_count = g2_count
            Module._pending_cycles = 0

        # Assign modules based on last stable assignment, avoiding overlap
        Module.G1_MODULE.clear()
        Module.G2_MODULE.clear()
        g1 = Module._last_g1_count
        g2 = Module._last_g2_count
        if g1 + g2 > total_modules:
            # Should not happen, but just in case
            g2 = total_modules - g1 if g1 < total_modules else 0
        g2 = max(0, g2)  # Ensure g2 is never negative
        g1 = max(0, g1)  # Ensure g1 is never negative
        Module.G1_MODULE.extend(Module.TOTAL_MODULE[:g1])
        if g2 > 0:
            Module.G2_MODULE.extend(Module.TOTAL_MODULE[-g2:])
        else:
            Module.G2_MODULE.clear()

    @staticmethod
    def contactorSetter(G1_Module, G2_Module):
        """
        Dynamically determines which contactors to turn ON/OFF based on module assignment.
        Ensures a break (open contactor) between Gun1 and Gun2 modules at all times.
        """
        total_modules = len(Module.TOTAL_MODULE)
        total_contactors = len(Contactors.TOTAL_CONTACTORS)
        g1_count = len(G1_Module)
        g2_count = len(G2_Module)

        # The break is always at index = g1_count
        # ON: indices < g1_count (for Gun1), indices >= total_contactors - g2_count (for Gun2)
        # OFF: all others (including the break)
        for idx, contactor in enumerate(Contactors.TOTAL_CONTACTORS):
            if idx < g1_count or idx >= total_contactors - g2_count:
                Contactors.contactor_states[contactor] = True  # ON
            else:
                Contactors.contactor_states[contactor] = False  # OFF (break or unused)

        # For debug: print the states
        print("Contactor States:")
        for c in Contactors.TOTAL_CONTACTORS:
            print(f"  {c}: {'ON' if Contactors.contactor_states[c] else 'OFF'}")

        # Optionally, return the states for further use
        return Contactors.contactor_states
    
    @staticmethod
    def getContactors_states():
        return Contactors.contactor_states

    @staticmethod
    def getG1_modules():
        return Module.G1_MODULE

    @staticmethod
    def getG2_modules():
        return Module.G2_MODULE