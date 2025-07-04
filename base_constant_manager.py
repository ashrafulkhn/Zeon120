from utility import Singleton


class BaseConstantManager(metaclass=Singleton):

    def __init__(self, d='', pe1current=0, vehiclestatus2=6, vehiclestatus1=6,maxev1power=0,maxev2power=0):
        self._digitalinput = d
        self._pe1_current = pe1current
        self._vehicle_status2 = vehiclestatus2
        self._vehicle_status1 = vehiclestatus1
        self._maxev1_power = maxev1power
        self._maxev2_power = maxev2power

    def get_data(self):
        return self._digitalinput

    def set_data(self, x):
        self._digitalinput = x

    def get_data_current_pe1(self):
        return self._pe1_current

    def set_data_current_pe1(self, x):
        self._pe1_current = x

    def get_data_running_current(self):
        return self._rc

    def set_data_running_current(self, x):
        self._rc = x

    def get_data_status_vehicle2(self):
        return self._vehicle_status2

    def set_data_status_vehicle2(self, x):
        self._vehicle_status2 = x

    def get_data_status_vehicle1(self):
        return self._vehicle_status1

    def set_data_status_vehicle1(self, x):
        self._vehicle_status1 = x

    def get_data_maxpower_ev1(self):
        return self._maxev1_power

    def set_data_maxpower_ev1(self, x):
        self._maxev1_power = x

    def get_data_maxpower_ev2(self):
        return self._maxev2_power

    def set_data_maxpower_ev2(self, x):
        self._maxev2_power = x

    def set_digital_output_list(self, data, index):
        self._digitalinput[index] = data
