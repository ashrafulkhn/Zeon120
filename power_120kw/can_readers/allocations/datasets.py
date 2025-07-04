import json
import re

class Datasets:
    # This class will have demand attributes dynamically set at runtime
    pass

class DataHandler(Datasets):
    @staticmethod
    def updateMessage(payload):
        data = json.loads(payload)

        gun_data = {}
        for key, value in data.items():
            match = re.match(r"v(\d+)_(current|voltage)", key)
            if match:
                gun_number, dtype = match.groups()  # e.g. ("1", "current")
                if gun_number not in gun_data:
                    gun_data[gun_number] = {}
                gun_data[gun_number][dtype] = value

        for gun_number, values in gun_data.items():
            if "current" in values and "voltage" in values:
                demand = [values["current"], values["voltage"]]
                gun_id = f"gun{gun_number}"
                DataHandler.setDemand_vehicle(demand, gun_id)

    @staticmethod
    def setDemand_vehicle(demand, gun_id):
        # Extract number from "gunX"
        gun_number = ''.join(filter(str.isdigit, gun_id))

        # Set demand attributes dynamically
        current_attr = f"vehicle{gun_number}_demand_current"
        voltage_attr = f"vehicle{gun_number}_demand_voltage"

        setattr(Datasets, current_attr, demand[0])
        setattr(Datasets, voltage_attr, demand[1])

        # print(f"[SET] {current_attr} = {demand[0]}, {voltage_attr} = {demand[1]}")

    @staticmethod
    def getDemand_vehicle(gun_id):
        gun_number = ''.join(filter(str.isdigit, gun_id))
        current_attr = f"vehicle{gun_number}_demand_current"
        voltage_attr = f"vehicle{gun_number}_demand_voltage"

        current = getattr(Datasets, current_attr, 0)
        voltage = getattr(Datasets, voltage_attr, 0)

        # print(f"[GET] {current_attr} = {current}, {voltage_attr} = {voltage}")
        return [current, voltage]
