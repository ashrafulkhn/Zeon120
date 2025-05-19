from power_120kw.constant_manager_120kw import ConstantManager120KW

class powerManager:
    def __init__(self):
        self._global_data = ConstantManager120KW()
        self._targetData = {
            "targetvoltage_1": 0,
            "targetvoltage_2": 0,
            "targetcurrent_1": 0,
            "targetcurrent_2": 0,
            "targetpower_1": 0,
            "targetpower_2": 0,
            "maxev1power": 0,
            "maxev2power": 0,
            "pm_assign1": 0,
            "pm_assign2": 0,
            "vehicle_Status_1": 0,
            "vehicle_Status_2": 0,
        }

    def getTargetData(self):
        self._targetData["targetvoltage_1"] = self._global_data.get_data_targetvoltage_ev1()
        self._targetData["targetvoltage_2"] = self._global_data.get_data_targetvoltage_ev2()
        self._targetData["targetcurrent_1"] = self._global_data.get_data_targetcurrent_ev1()
        self._targetData["targetcurrent_2"] = self._global_data.get_data_targetcurrent_ev2()
        self._targetData["targetpower_1"] = self._global_data.get_data_targetpower_ev1()
        self._targetData["targetpower_2"] = self._global_data.get_data_targetpower_ev2()
        self._targetData["maxev1power"] = self._global_data.get_data_maxpower1()
        self._targetData["maxev2power"] = self._global_data.get_data_maxpower2()
        self._targetData["targetvoltage_1"] = self._global_data.get_data_targetvoltage_ev1()
        self._targetData["targetvoltage_2"] = self._global_data.get_data_targetvoltage_ev2()
        self._targetData["pm_assign1"] = self._global_data.get_data_pm_assign1()
        self._targetData["pm_assign2"] = self._global_data.get_data_pm_assign2()
        self._targetData["vehicle_Status_1"] = self._global_data.get_data_status_vehicle1()
        self._targetData["vehicle_Status_2"] = self._global_data.get_data_status_vehicle2()

        return self._targetData

class demandProcessor(powerManager):
    def __init__(self):
        self.demandData = self.getTargetData()

    def processDemand(self):
        if self.demandData["targetpower_1"] > self.demandData["maxev1power"]:
            self.demandData["targetpower_1"] = self.demandData["maxev1power"]
        if self.demandData["targetpower_2"] > self.demandData["maxev2power"]:
            self.demandData["targetpower_2"] = self.demandData["maxev2power"]
        if self.demandData["targetvoltage_1"] > 1000:
            self.demandData["targetvoltage_1"] = 1000
        if self.demandData["targetvoltage_2"] > 1000:
            self.demandData["targetvoltage_2"] = 1000
        if self.demandData["targetcurrent_1"] > 200:
            self.demandData["targetcurrent_1"] = 200
        if self.demandData["targetcurrent_2"] > 200:
            self.demandData["targetcurrent_2"] = 200



