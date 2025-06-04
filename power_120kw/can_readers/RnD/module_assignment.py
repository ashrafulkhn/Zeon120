class Module:
    G1_MODULE = []
    G2_MODULE = []
    TOTAL_MODULE = [
        "CAN_ID_1",
        "CAN_ID_2",
        "CAN_ID_3",
        "CAN_ID_4"
    ]
    MODULE_POWER = 30000  # Each module can serve 30kW (example)
    # Hysteresis state
    _last_g1_count = None
    _last_g2_count = None
    _pending_g1_count = None
    _pending_g2_count = None
    _pending_cycles = 0
    _hysteresis_cycles = 3  # Number of cycles to wait before switching

class ModuleSetter:
    @staticmethod
    def assign_modules(demand1, demand2):
        total_modules = len(Module.TOTAL_MODULE)
        modules_needed_g1 = (demand1 + Module.MODULE_POWER - 1) // Module.MODULE_POWER
        modules_needed_g2 = (demand2 + Module.MODULE_POWER - 1) // Module.MODULE_POWER
        total_needed = modules_needed_g1 + modules_needed_g2
        if total_needed <= total_modules:
            g1_count = modules_needed_g1
            g2_count = modules_needed_g2
        else:
            if demand1 + demand2 == 0:
                g1_share = 0
                g2_share = 0
            else:
                g1_share = demand1 / (demand1 + demand2)
                g2_share = demand2 / (demand1 + demand2)
            g1_count = int(round(g1_share * total_modules))
            g2_count = total_modules - g1_count
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
        # Assign modules based on last stable assignment
        Module.G1_MODULE.clear()
        Module.G2_MODULE.clear()
        Module.G1_MODULE.extend(Module.TOTAL_MODULE[:Module._last_g1_count])
        Module.G2_MODULE.extend(Module.TOTAL_MODULE[Module._last_g1_count:Module._last_g1_count+Module._last_g2_count])

    @staticmethod
    def getG1_modules():
        return Module.G1_MODULE

    @staticmethod
    def getG2_modules():
        return Module.G2_MODULE