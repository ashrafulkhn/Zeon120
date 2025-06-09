import logging

from base_reader import BaseReader
from constants import PECC
from power_120kw.constant_manager_120kw import ConstantManager120KW
from utility import bytetobinary, binaryToDecimal, DTH
from config_reader import ConfigManager

#logger = logging.getLogger(__name__)

class PowerModuleReader(BaseReader):

    def __init__(self, data):
        self.data = data
        self._global_data = ConstantManager120KW()
        self._vehicle_status1_g = None
        self._vehicle_status2_g = None
        self._maxpowerev1_g = None
        self._maxpowerev2_g = None
        self._targetpower_ev1 = None
        self._targetpower_ev2 = None
        self._pm_assign1 = None
        self._pm_assign2 = None
        self._diff_vol_current = None
        self._binary_data = bytetobinary(data)

    def read_input_data(self):
        self._vehicle_status2_g = self._global_data.get_data_status_vehicle2()
        self._vehicle_status1_g = self._global_data.get_data_status_vehicle1()
        self._maxevpower1_g = self._global_data.get_data_maxpower_ev1()
        self._maxevpower2_g = self._global_data.get_data_maxpower_ev2()
        self._targetpower_ev1 = self._global_data.get_data_targetpower_ev1()
        self._targetpower_ev2 = self._global_data.get_data_targetpower_ev2()
        self._pm_assign1 = self._global_data.get_data_pm_assign1()
        self._pm_assign2 = self._global_data.get_data_pm_assign2()
        self._diff_vol_current = binaryToDecimal(int(self._binary_data[1]))

class PMSetDataCurrentPeccStatus1(PowerModuleReader):
    arbitration_id = int(ConfigManager().get_power_config('PS1_id'))

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 120KW PECC-1 Status')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            volatge_pe1 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol = ((volatge_pe1) / 1000)
            t1 = int(divide_vol* 10)
            vl1 = DTH.converttohexforpecc(hex(t1))
            PECC.STATUS2_GUN1_DATA[1] = vl1[0]
            PECC.STATUS2_GUN1_DATA[0] = vl1[1]
        if self._diff_vol_current == 48:
            self._global_data.set_data_current_pe1(binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])))
            if self._vehicle_status2_g == 0 or self._vehicle_status2_g == 6:
                if self._targetpower_ev1 <= 28000 or self._pm_assign1 == 1:
                    pe1current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))                
                    tot_current1 = int((pe1current/1000) * 10)
                    cu_vl_11 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_11[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_11[1]
            if self._vehicle_status1_g == 21 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 29 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 35 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 37 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6:
                if self._targetpower_ev1 <= 28000 or self._pm_assign1 == 1:
                    pe1current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))                
                    tot_current1 = int((pe1current/1000) * 10)
                    cu_vl_11 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_11[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_11[1]



class PMSetDataCurrentPeccStatus2(PowerModuleReader):
    arbitration_id = int(ConfigManager().get_power_config('PS2_id'))

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 120KW PECC-2 Status')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            volatge_pe2 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol2 = ((volatge_pe2) / 1000)
            t2 = int(divide_vol2) * 10
            vl2 = DTH.converttohexforpecc(hex(t2))
            PECC.STATUS2_GUN2_DATA[1] = vl2[0]
            PECC.STATUS2_GUN2_DATA[0] = vl2[1]
        
        if self._diff_vol_current == 48:
            self._global_data.set_data_current_pe2(binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])))
            if self._vehicle_status1_g == 0 or self._vehicle_status1_g == 6:
                if self._targetpower_ev2 <= 28000 or self._pm_assign2 == 1:
                    pe2current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))                
                    tot_current2 = int((pe2current/1000) * 10)
                    cu_vl_22 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_22[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_22[1]
            if self._vehicle_status2_g == 21 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 29 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 35 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 37 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6:
                if self._targetpower_ev2 <= 28000 or self._pm_assign2 == 1:
                    pe2current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))                
                    tot_current2 = int((pe2current/1000) * 10)
                    cu_vl_22 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_22[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_22[1]

class PMSetDataCurrentPeccStatus4(PowerModuleReader):
    arbitration_id = int(ConfigManager().get_power_config('PS4_id'))

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 120KW PECC-4 Status')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            volatge_pe4 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol4 = (volatge_pe4) / 1000
            t4 = int(divide_vol4 * 10)
            vl4 = DTH.converttohexforpecc(hex(t4))
            PECC.STATUS2_GUN2_DATA[1] = vl4[0]
            PECC.STATUS2_GUN2_DATA[0] = vl4[1]
        if self._diff_vol_current == 48:
            self._global_data.set_data_current_pe4(binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])))
            c_pe4 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            current_pe4 = (c_pe4) / 1000
            tc1 = (self._global_data.get_data_current_pe1()) / 1000
            tc2 = (self._global_data.get_data_current_pe2()) / 1000
            tc3 = (self._global_data.get_data_current_pe3()) / 1000
            if self._vehicle_status2_g == 0 or self._vehicle_status2_g == 6 :
                if self._pm_assign1 == 3:
                    tot_current1 = int((current_pe4 + tc1 + tc3) * 10)
                    cu_vl_13 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_13[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_13[1]

                elif self._pm_assign1 == 4:
                    tot_current1 = int((current_pe4 + tc1 + tc2 + tc3) * 10)
                    cu_vl_14 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_14[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_14[1]
            if self._vehicle_status1_g == 0 or self._vehicle_status1_g == 6 :
                if self._pm_assign2 == 2:             
                    tot_current2 = int((current_pe4 + tc2 ) * 10)
                    cu_vl_22 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_22[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_22[1]
                elif self._pm_assign2 == 4:
                    tot_current2 = int((current_pe4 + tc1 + tc2 + tc3) * 10)
                    cu_vl_24 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_24[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_24[1]
            if self._vehicle_status1_g == 21 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 29 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 35 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 37 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6:
                if self._pm_assign1 == 3:
                    tot_current1 = int((current_pe4 + tc3 + tc1 ) * 10)
                    cu_vl_14 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_14[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_14[1]

            if self._vehicle_status2_g == 21 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 29 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 35 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6 or self._vehicle_status2_g == 37 and self._vehicle_status1_g != 0 and self._vehicle_status1_g != 6:    
                if (self._pm_assign2 == 2):
                    tot_current2 = int((current_pe4 + tc2 ) * 10)
                    cu_vl_23 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_23[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_23[1]
                elif self._pm_assign2 == 3:
                    tot_current2 = int((current_pe4 + tc2 + tc3 ) * 10)
                    cu_vl_24 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_24[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_24[1]
class PMSetDataCurrentPeccStatus3(PowerModuleReader):
    arbitration_id = int(ConfigManager().get_power_config('PS3_id'))

    def __init__(self, data):
        super().__init__(data)

    def read_input_data(self):
        #logger.info('Reading input for 120KW PECC-3 Status')
        bd = self._binary_data
        super().read_input_data()
        if self._diff_vol_current == 98:
            volatge_pe3 = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7]))
            divide_vol3 = (volatge_pe3) / 1000
            t3 = int(divide_vol3 * 10)
            vl3 = DTH.converttohexforpecc(hex(t3))
            PECC.STATUS2_GUN1_DATA[1] = vl3[0]
            PECC.STATUS2_GUN1_DATA[0] = vl3[1]
        if self._diff_vol_current == 48:
            self._global_data.set_data_current_pe3(binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])))
            pe3current = binaryToDecimal(int(bd[4] + bd[5] + bd[6] + bd[7])) 
            current_pe3 = (pe3current/1000)  
            tc2 = (self._global_data.get_data_current_pe2()) / 1000
            tc4 = (self._global_data.get_data_current_pe4()) / 1000
            if self._vehicle_status2_g == 0 or self._vehicle_status2_g == 6 :
                if self._pm_assign1 == 2:             
                    tc1 = (self._global_data.get_data_current_pe1()) / 1000
                    tot_current1 = int((current_pe3 + tc1 ) * 10)
                    cu_vl_12 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_12[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_12[1]
            if self._vehicle_status1_g == 0 or self._vehicle_status1_g == 6 :
                if self._pm_assign2 == 3:
                    tot_current2 = int((current_pe3 + tc4 + tc2) * 10)
                    cu_vl_23 = DTH.converttohexforpecc(hex(tot_current2))
                    PECC.STATUS2_GUN2_DATA[3] = cu_vl_23[0]
                    PECC.STATUS2_GUN2_DATA[2] = cu_vl_23[1]
            if self._vehicle_status1_g == 21 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 29 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 35 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6 or self._vehicle_status1_g == 37 and self._vehicle_status2_g != 0 and self._vehicle_status2_g != 6:
                if (self._pm_assign1 == 2):
                    tc1 = (self._global_data.get_data_current_pe1()) / 1000
                    tot_current1 = int((current_pe3 + tc1 ) * 10)
                    cu_vl_13 = DTH.converttohexforpecc(hex(tot_current1))
                    PECC.STATUS2_GUN1_DATA[3] = cu_vl_13[0]
                    PECC.STATUS2_GUN1_DATA[2] = cu_vl_13[1]