import logging
from base_reader import BaseReader
from constants import PECC
from config_reader import ConfigManager
from power_60kw.constant_manager_60kw import ConstantManager60KW
from utility import bytetobinary, binaryToDecimal, DTH

#logger = logging.getLogger(__name__)


class PowerModuleReader(BaseReader):

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager60KW()
        self._vehicle_status1_g = None
        self._vehicle_status2_g = None
        self.maxevpower1_g = None
        self.maxevpower2_g = None
        self.target_power_car1 = None
        self.target_power_car2 = None
        self._diff_vol_current = None
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        self._vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        self._vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        self.maxevpower1_g = self._global_data.get_data_maxpower_ev1()
        self.maxevpower2_g = self._global_data.get_data_maxpower_ev2()
        self.target_power_car1 = self._global_data.get_data_targetpower_ev1()
        self.target_power_car2 = self._global_data.get_data_targetpower_ev2()
        self._diff_vol_current = binaryToDecimal(int(self._binary_data[1]))


class PowerModule1Reader(PowerModuleReader):
    arbitration_id = 35677237

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 60KW Power module-1')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            voltage_pe1 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol = int(voltage_pe1) / 1000

            t1 = int(divide_vol) * 10
            #print('voltage1=', t1)
            vl = DTH.converttohexforpecc(hex(t1))
            PECC.STATUS2_GUN1_DATA[1] = vl[0]
            PECC.STATUS2_GUN1_DATA[0] = vl[1]

        if self._diff_vol_current == 48:
            self._global_data.set_data_current_pe1(binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])))
            if self._vehicle_status2_g == 0 or self._vehicle_status2_g == 6:
                if self.maxevpower1_g <= 30000 or self.target_power_car1 <= 30000:
                    pe1current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))                
                    tot_current1 = int(int(pe1current/1000) * 10)
                    cu_vl_21 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_21[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_21[1]
                    print(f"exptected _diff_vol_current1 == 48 and {cu_vl_21[1]} {cu_vl_21[0]}")
            if self._vehicle_status1_g == 21 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 29 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 35 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 37 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6:
                pe1current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
                c1 = int(int(pe1current) / 1000)
                current1 = int(c1) * 10
                cu_vl_1 = DTH.converttohexforpecc(hex(current1))
                PECC.STATUS2_GUN1_DATA[3] = cu_vl_1[0]
                PECC.STATUS2_GUN1_DATA[2] = cu_vl_1[1]


class PowerModule2Reader(PowerModuleReader):
    arbitration_id = 35693618

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 60KW Power module-2')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            volatge_pe2 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol2 = int(int(volatge_pe2) / 1000)
            t2 = int(divide_vol2) * 10
            vl2 = DTH.converttohexforpecc(hex(t2))
            PECC.STATUS2_GUN2_DATA[1] = vl2[0]
            PECC.STATUS2_GUN2_DATA[0] = vl2[1]
            
        if self._diff_vol_current == 48:
            c_pe2 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            current_pe2 = int(int(c_pe2) / 1000)
            t = int(self._global_data.get_data_current_pe1()) / 1000
            if self._vehicle_status2_g == 0 or self._vehicle_status2_g == 6:
                
                tot_current1 = int(current_pe2 + t) * 10
                cu_vl_21 = DTH.converttohexforpecc(hex(tot_current1))
                PECC.STATUS2_GUN1_DATA[3] = cu_vl_21[0]
                PECC.STATUS2_GUN1_DATA[2] = cu_vl_21[1]
                print(f"exptected _diff_vol_current2 == 48 and  {cu_vl_21[1]} {cu_vl_21[0]}")
            if self._vehicle_status1_g == 0 or self._vehicle_status1_g == 6:
                if self.maxevpower2_g <= 30000 or self.target_power_car2 <= 30000:
                    tot_current2 = int(current_pe2) * 10
                    cu_vl_21 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_21[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_21[1]

                else:
                    tot_current2 = int(current_pe2 + t) * 10
                    cu_vl_21 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_21[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_21[1]

            if self._vehicle_status2_g == 21 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 29 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 35 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 37 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6:
                tot_current2 = int(current_pe2) * 10
                cu_vl_22 = DTH.converttohexforpecc(hex(tot_current2))
                PECC.STATUS2_GUN2_DATA[3] = cu_vl_22[0]
                PECC.STATUS2_GUN2_DATA[2] = cu_vl_22[1]
