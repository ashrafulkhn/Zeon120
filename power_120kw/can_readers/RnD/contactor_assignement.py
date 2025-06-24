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

class ContactorSetter:
    @staticmethod
    def contactorSetter(G1_Module, G2_Module):
        """
        Dynamically determines which contactors to turn ON/OFF based on module assignment.
        Ensures a break (open contactor) between Gun1 and Gun2 modules at all times.
        """
        # total_modules = len(Module.TOTAL_MODULE)
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
        # print("Contactor States:")
        # for c in Contactors.TOTAL_CONTACTORS:
        #     print(f"  {c}: {'ON' if Contactors.contactor_states[c] else 'OFF'}")

        # Optionally, return the states for further use
        return Contactors.contactor_states

    @staticmethod
    def getContactors_states():
        return Contactors.contactor_states