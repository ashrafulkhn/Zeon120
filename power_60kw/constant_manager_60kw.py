from base_constant_manager import BaseConstantManager


class ConstantManager60KW(BaseConstantManager):
    def __init__(self, d='', pe1current=0, rc=0, vehiclestatus2=6, vehiclestatus1=6, maxev1power=0,maxev2power=0,targetpower1=0,targetpower2=0):
        super().__init__(d, pe1current, vehiclestatus2, vehiclestatus1, maxev1power,maxev2power)
        self._rc = rc
        self._power1 = targetpower1
        self._power2 = targetpower2
    def get_data_running_current(self):
        return self._rc

    def set_data_running_current(self, x):
        self._rc = x

    def get_data_targetpower_ev1(self):
        return self._power1

    def set_data_targetpower_ev1(self, x):
        self._power1 = x

    def get_data_targetpower_ev2(self): # 60kW code change
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