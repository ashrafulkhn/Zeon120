# constant_manager_120kw.py - Manages all runtime constants and shared data for the 120kW power module.
# Includes currents, power targets, and vehicle status for the Zeon120 system.

from base_constant_manager import BaseConstantManager

# ConstantManager120KW manages all runtime constants and shared data
# for the 120kW power module, including currents, power targets, and vehicle status.

class ConstantManager120KW(BaseConstantManager):
    def __init__(self, d='', pe1current=0, pe2current=0, pe3current=0, pe4current=0, rc=0, vehiclestatus2=6, vehiclestatus1=6, targetpower1=0,targetpower2=0,maxev1power=0,maxev2power=0,maxpower1=0,maxpower2=0 ):
        # Initialize all relevant parameters and call base class constructor
        super().__init__(d, pe1current, vehiclestatus2, vehiclestatus1,maxev1power,maxev2power)
        self._pe2_current = pe2current
        self._pe3_current = pe3current
        self._pe4_current = pe4current
        self._rc = rc  # Running current (demand)
        self._power1 = targetpower1  # Target power for EV1
        self._power2 = targetpower2  # Target power for EV2
        self._maxpower1 = maxpower1  # Max allowed power for EV1
        self._maxpower2 = maxpower2  # Max allowed power for EV2

    # Getters and setters for each managed parameter

    def get_data_current_pe2(self):  # Get current for PE2
        return self._pe2_current

    def set_data_current_pe2(self, x):
        self._pe2_current = x

    def get_data_current_pe3(self):  # Get current for PE3
        return self._pe3_current

    def set_data_current_pe3(self, x):
        self._pe3_current = x

    def get_data_current_pe4(self):  # Get current for PE4
        return self._pe4_current

    def set_data_current_pe4(self, x):
        self._pe4_current = x

    def get_data_running_current(self): # Get running current (demand)
        return self._rc

    def set_data_running_current(self, x):
        self._rc = x

    def get_data_targetpower_ev1(self): # Get target power for EV1
        return self._power1

    def set_data_targetpower_ev1(self, x):
        self._power1 = x

    def get_data_targetpower_ev2(self): # Get target power for EV2
        return self._power2

    def set_data_targetpower_ev2(self, x):
        self._power2 = x

    def get_data_maxpower1(self): # Get max allowed power for EV1
        return self._maxpower1

    def set_data_maxpower1(self, x):
        self._maxpower1 = x

    def get_data_maxpower2(self): # Get max allowed power for EV2
        return self._maxpower2

    def set_data_maxpower2(self, x):
        self._maxpower2 = x
