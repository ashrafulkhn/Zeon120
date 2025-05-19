from base_constant_manager import BaseConstantManager


class ConstantManager120KW(BaseConstantManager):

    def __init__(self, d='', pe1current=0, pe2current=0, pe3current=0, pe4current=0, rc=0, vehiclestatus2=6, vehiclestatus1=6, targetpower1=0,targetpower2=0,maxev1power=0,maxev2power=0,maxpower1=0,maxpower2=0,pm_assign1=0, pm_assign2=0 ):
        super().__init__(d, pe1current, vehiclestatus2, vehiclestatus1,maxev1power,maxev2power)
        self._pe2_current = pe2current
        self._pe3_current = pe3current
        self._pe4_current = pe4current
        self._rc = rc
        self._power1 = targetpower1
        self._power2 = targetpower2
        self._maxpower1 = maxpower1
        self._maxpower2 = maxpower2
        self._pm_assign1 = pm_assign1
        self._pm_assign2 = pm_assign2
        self._targetvoltage_ev1 = 0
        self._targetvoltage_ev2 = 0
        self._targetcurrent_ev1 = 0
        self._targetcurrent_ev2 = 0
        self._cablecheckvoltage_ev2 = 0
        self._cablecheckvoltage_ev1 = 0
        
    def get_data_current_pe2(self):  # 120kW code change
        return self._pe2_current

    def set_data_current_pe2(self, x):
        self._pe2_current = x

    def get_data_current_pe3(self):  # 120kW code change
        return self._pe3_current

    def set_data_current_pe3(self, x):
        self._pe3_current = x

    def get_data_current_pe4(self):  # 120kW code change
        return self._pe4_current

    def set_data_current_pe4(self, x):
        self._pe4_current = x

    def get_data_running_current(self): # 120kW code change
        return self._rc

    def set_data_running_current(self, x):
        self._rc = x

    def get_data_targetpower_ev1(self): # 120kW code change
        return self._power1

    def set_data_targetpower_ev1(self, x):
        self._power1 = x

    def get_data_targetpower_ev2(self): # 120kW code change
        return self._power2

    def set_data_targetpower_ev2(self, x):
        self._power2 = x

    def get_data_maxpower1(self): # 120kW code change
        return self._maxpower1

    def set_data_maxpower1(self, x):
        self._maxpower1 = x

    def get_data_maxpower2(self): # 120kW code change
        return self._maxpower2

    def set_data_maxpower2(self, x):
        self._maxpower2 = x

    def get_data_pm_assign1(self): # 120kW code change
        return self._pm_assign1

    def set_data_pm_assign1(self, x):
        self._pm_assign1 = x

    def get_data_pm_assign2(self): # 120kW code change
        return self._pm_assign2

    def set_data_pm_assign2(self, x):
        self._pm_assign2 = x

    def get_data_targetvoltage_ev1(self):
        return self._targetvoltage_ev1
    
    def set_data_targetvoltage_ev1(self, x):
        self._targetvoltage_ev1 = x

    def get_data_targetvoltage_ev2(self):
        return self._targetvoltage_ev2
    
    def set_data_targetvoltage_ev2(self, x):
        self._targetvoltage_ev2 = x

    def get_data_targetcurrent_ev1(self):
        return self._targetcurrent_ev1
    
    def set_data_targetcurrent_ev1(self, x):
        self._targetcurrent_ev1 = x

    def get_data_targetcurrent_ev2(self):
        return self._targetcurrent_ev2
    
    def set_data_targetcurrent_ev1(self, x):
        self._targetcurrent_ev2 = x

    def get_data_cablecheckvoltage_ev1(self):
        return self._cablecheckvoltage_ev1
    
    def set_data_cablecheckvoltage_ev2(self, x):
        self._cablecheckvoltage_ev2 = x

    def get_data_cablecheckvoltage_ev2(self):
        return self._cablecheckvoltage_ev2
    
    def set_data_cablecheckvoltage_ev2(self, x):
        self._cablecheckvoltage_ev2 = x