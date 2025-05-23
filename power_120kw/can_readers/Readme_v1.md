# Control Flow Diagram for `Vehicle1StatusReader.read_input_data`

This document describes the control flow of the `read_input_data` method in [`power_120kw/can_readers/vehicle1_status_reader.py`](power_120kw/can_readers/vehicle1_status_reader.py). The diagram below outlines all major conditions, sub-conditions, and the actions taken for each.

---

## Legend

- **Rectangles**: Actions or function calls
- **Diamonds**: Conditional branches
- **Indented lists**: Sub-conditions or nested logic

---

## Flow Diagram

```mermaid
flowchart TD
    Start([Start: read_input_data])
    Start --> InitVars[/"Initialize variables and update real-time VIP"/]
    InitVars -->|vehicle_status1 & vehicle_status2_g| MainConditions

    subgraph MainConditions [Main Condition Checks]
        direction TB

        C1{{"vehicle_status1 == 0 and vehicle_status2_g == 0 OR\nvehicle_status1 == 6 and vehicle_status2_g == 6 OR\nvehicle_status1 == 6 and vehicle_status2_g == 0"}}
        C2{{"vehicle_status1 == 0 and vehicle_status2_g == 6 OR\nvehicle_status1 == 0 and vehicle_status2_g == 2 OR\nvehicle_status1 == 0 and vehicle_status2_g == 29"}}
        C3{{"vehicle_status1 == 2 and vehicle_status2_g == 0 OR\nvehicle_status1 == 2 and vehicle_status2_g == 6"}}
        C4{{"vehicle_status1 == 2 and vehicle_status2_g == 13 OR\nvehicle_status1 == 2 and vehicle_status2_g == 21 OR\nvehicle_status1 == 2 and vehicle_status2_g == 29"}}
        C5{{"vehicle_status1 == 13 and vehicle_status2_g == 0 OR\nvehicle_status1 == 13 and vehicle_status2_g == 6"}}
        C6{{"vehicle_status1 == 13 and vehicle_status2_g == 2 OR\nvehicle_status1 == 13 and vehicle_status2_g == 37 OR\nvehicle_status1 == 13 and vehicle_status2_g == 35"}}
        C7{{"vehicle_status1 == 13 and vehicle_status2_g == 13 OR\nvehicle_status1 == 13 and vehicle_status2_g == 21 OR\nvehicle_status1 == 13 and vehicle_status2_g == 29"}}
        C8{{"vehicle_status1 == 21 and vehicle_status2_g == 0 OR\nvehicle_status1 == 21 and vehicle_status2_g == 6"}}
        C9{{"vehicle_status1 == 21 and vehicle_status2_g == 2 OR\nvehicle_status1 == 21 and vehicle_status2_g == 35 OR\nvehicle_status1 == 21 and vehicle_status2_g == 37"}}
        C10{{"vehicle_status1 == 21 and vehicle_status2_g == 13 OR\nvehicle_status1 == 21 and vehicle_status2_g == 21 OR\nvehicle_status1 == 21 and vehicle_status2_g == 29"}}
        C11{{"vehicle_status1 == 29 and vehicle_status2_g == 0 OR\nvehicle_status1 == 29 and vehicle_status2_g == 6"}}
        C12{{"vehicle_status1 == 29 and vehicle_status2_g == 2 OR\nvehicle_status1 == 29 and vehicle_status2_g == 35 OR\nvehicle_status1 == 29 and vehicle_status2_g == 37"}}
        C13{{"vehicle_status1 == 29 and vehicle_status2_g == 13 OR\nvehicle_status1 == 29 and vehicle_status2_g == 21 OR\nvehicle_status1 == 29 and vehicle_status2_g == 29"}}
        C14{{"vehicle_status1 == 37 and vehicle_status2_g == 0 OR\nvehicle_status1 == 35 and vehicle_status2_g == 0 OR\nvehicle_status1 == 35 and vehicle_status2_g == 6 OR\nvehicle_status1 == 37 and vehicle_status2_g == 6"}}
        C15{{"vehicle_status1 == 37 and vehicle_status2_g == 35 OR\nvehicle_status1 == 35 and vehicle_status2_g == 37 OR\nvehicle_status1 == 35 and vehicle_status2_g == 35 OR\nvehicle_status1 == 37 and vehicle_status2_g == 35"}}
        C16{{"vehicle_status1 == 37 and vehicle_status2_g == 2 OR\nvehicle_status1 == 37 and vehicle_status2_g == 13 OR\nvehicle_status1 == 37 and vehicle_status2_g == 21 OR\nvehicle_status1 == 37 and vehicle_status2_g == 29"}}
        C17{{"vehicle_status1 == 35 and vehicle_status2_g == 2 OR\nvehicle_status1 == 35 and vehicle_status2_g == 13 OR\nvehicle_status1 == 35 and vehicle_status2_g == 21 OR\nvehicle_status1 == 35 and vehicle_status2_g == 29"}}
    end

    InitVars --> C1
    C1 -->|true| StandByled1["standByled()"]
    C1 --> C2
    C2 -->|true| StandByled2["standByled()"]
    C2 --> C3
    C3 -->|true| C3Check["Check digitl_input"]
    C3Check -->|digitl_input[1]=='0' or digitl_input[2]=='1' or digitl_input[7]=='0'| RedLED2["Red LED, stopcharging, STATUS1_GUN1_DATA[0]=2"]
    C3Check -->|else| GreenLED2["Green LED, close AC, STATUS1_GUN1_DATA[0]=0"]
    C3Check -->|digitl_input empty| GreenLED2b["Green LED, close AC, STATUS1_GUN1_DATA[0]=0"]
    C3 --> C4
    C4 -->|true| C4Actions["Green LED, STATUS1_GUN1_DATA[0]=0, get target_power_from_car2, standByled()"]
    C4 --> C5
    C5 -->|true| C5Actions["Set limits, STATUS1_GUN1_DATA[0]=1, updateVI_status, Green LED, close Gun11, funct_40_cc()"]
    C5Actions --> C5IMD["Check digitl_input[3]"]
    C5IMD -->|digitl_input[3]=='1'| C5IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_stop, open_fan"]
    C5IMD -->|digitl_input[3]=='0'| C5IMD2["STATUS1_GUN1_DATA[0]=5"]
    C5 --> C6
    C6 -->|true| C6Actions["updateVI_status, STATUS1_GUN1_DATA[0]=1, Green LED, Gun1_load21, stopModule(2,4,3), funct_40_cc()"]
    C6Actions --> C6IMD["Check digitl_input[3]"]
    C6IMD -->|digitl_input[3]=='1'| C6IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_load11"]
    C6IMD -->|digitl_input[3]=='0'| C6IMD2["STATUS1_GUN1_DATA[0]=5"]
    C6 --> C7
    C7 -->|true| C7Actions["updateVI_status, STATUS1_GUN1_DATA[0]=1, Green LED, load11, set pm1, funct_40_cc()"]
    C7Actions --> C7IMD["Check digitl_input[3]"]
    C7IMD -->|digitl_input[3]=='1'| C7IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_load11"]
    C7IMD -->|digitl_input[3]=='0'| C7IMD2["STATUS1_GUN1_DATA[0]=5"]
    C7 --> C8
    C8 -->|true| C8Actions["updateVI_status, set limits, Green LED, close Gun11, set pm1, startCharging(pm1)"]
    C8Actions --> C8IMD["Check digitl_input[3]"]
    C8IMD -->|digitl_input[3]=='1'| C8IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_stop, open_fan"]
    C8IMD -->|digitl_input[3]=='0'| C8IMD2["STATUS1_GUN1_DATA[0]=5"]
    C8 --> C9
    C9 -->|true| C9Actions["updateVI_status, Green LED, set limits, Gun1_load21, stopModule(2,4,3), set pm1, startCharging(pm1)"]
    C9Actions --> C9IMD["Check digitl_input[3]"]
    C9IMD -->|digitl_input[3]=='1'| C9IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_load11"]
    C9IMD -->|digitl_input[3]=='0'| C9IMD2["STATUS1_GUN1_DATA[0]=5"]
    C9 --> C10
    C10 -->|true| C10Actions["updateVI_status, Green LED, set limits, load11, set pm1, startCharging(pm1)"]
    C10Actions --> C10IMD["Check digitl_input[3]"]
    C10IMD -->|digitl_input[3]=='1'| C10IMD1["Red LED, stopcharging, stopModule, STATUS1_GUN1_DATA[0]=9, open_load11"]
    C10IMD -->|digitl_input[3]=='0'| C10IMD2["STATUS1_GUN1_DATA[0]=5"]
    C10 --> C11
    C11 -->|true| C11Branch["Multiple Demand Conditions (target_power_from_car1)"]
    C11Branch -->|<=38000| C11D1["Set limits, set pm1, close Gun11, stopModule(2,4,3), limitChangeRequest(35000), if not requested: startCharging(pm1), else: set limit to 75kW"]
    C11D1 --> C11IMD["Check digitl_input[3]"]
    C11IMD -->|digitl_input[3]=='1'| C11IMD1["Red LED, stopcharging, stopActiveModules(pm1), STATUS1_GUN1_DATA[0]=9, open_stop, open_fan"]
    C11IMD -->|digitl_input[3]=='0'| C11IMD2["STATUS1_GUN1_DATA[0]=5"]
    C11Branch -->|>38000 and <42000| C11D2["Check pm_assign1, if 1: stopActiveModules(2,3,4), close Gun11, startCharging(1), if 2: close Gun12, stopModule(2,4), startCharging(1,3)"]
    C11D2 --> C11IMD
    C11Branch -->|>=42000 and <=78000| C11D3["set pm1(1,3), stopModule(2,4), limitChangeRequest(75000), if not requested: close Gun12, startCharging(pm1), else: set limit to 115kW"]
    C11D3 --> C11IMD
    C11Branch -->|>78000 and <82000| C11D4["Check pm_assign1, if 2: stopModule(2,4), close Gun12, startCharging(1,3), if 3: close Gun13, stopModule(2), startCharging(1,3,4)"]
    C11D4 --> C11IMD
    C11Branch -->|>=82000 and <=118000| C11D5["stopModule(2), set pm1(1,3,4), limitChangeRequest(115000), if not requested: close Gun13, startCharging(pm1), else: set limit to 160kW"]
    C11D5 --> C11IMD
    C11Branch -->|>118000 and <122000| C11D6["Check pm_assign1, if 3: stopModule(2), close Gun13, startCharging(1,3,4), if 4: close Gun14, startCharging(1,2,3,4)"]
    C11D6 --> C11IMD
    C11Branch -->|>=122000| C11D7["close Gun14, set pm1(1,2,3,4), startCharging(pm1)"]
    C11D7 --> C11IMD
    C11 --> C12
    C12 -->|true| C12Branch["Multiple Demand Conditions (target_power_from_car1, pm_assign2)"]
    C12Branch -->|<=38000| C12D1["Set limits, set pm1, Gun1_load21, stopActiveModules(2,4,3), startCharging(pm1)"]
    C12D1 --> C12IMD["Check digitl_input[3]"]
    C12IMD -->|digitl_input[3]=='1'| C12IMD1["Red LED, stopcharging, stopModule(1), STATUS1_GUN1_DATA[0]=9, open_load11"]
    C12IMD -->|digitl_input[3]=='0'| C12IMD2["STATUS1_GUN1_DATA[0]=5"]
    C12Branch -->|38000< and <=42000| C12D2["Check pm_assign1, if 1: set limits, Gun1_load21, stopActiveModules(2,4,3), startCharging(1), if 2: set limits, stopActiveModules(2,4), Gun1_load22, startCharging(1,3)"]
    C12D2 --> C12IMD
    C12Branch -->|42000< and <=78000| C12D3["set limits, pm1(1,3), stopActiveModules(2,4), Gun1_load22, startCharging(pm1)"]
    C12D3 --> C12IMD
    C12Branch -->|78000< and <=82000 and pm_assign2==1 or ...| C12D4["Check pm_assign1, if 2: set limits, stopActiveModules(2,4), Gun1_load22, startCharging(1,3), if 3: set limits, stopModule(2), Gun1_load23, startCharging(1,3,4)"]
    C12D4 --> C12IMD
    C12Branch -->|78000< and <=82000 and pm_assign2==2 or 3| C12D5["Check pm_assign1, if 2: set limits, stopActiveModules(2,4), Gun1_load22, startCharging(1,3), if 3: set limits, stopActiveModules(2,4), Gun1_load22, startCharging(1,3)"]
    C12D5 --> C12IMD
    C12Branch -->|>82000 and pm_assign2==1 or ...| C12D6["set limits, pm1(1,3,4), stopModule(2), Gun1_load23, startCharging(pm1)"]
    C12D6 --> C12IMD
    C12Branch -->|>82000 and pm_assign2==2 or 3| C12D7["set limits, load12, pm1(1,3), stopActiveModules(2,4), Gun1_load22, startCharging(pm1)"]
    C12D7 --> C12IMD
    C12 --> C13
    C13 -->|true| C13Branch["Multiple Demand Conditions (target_power_from_car1, pm_assign2)"]
    C13Branch -->|<=38000 and pm_assign2==1 or 2| C13D1["set limits, load11, stopModule(3), pm1(1), startCharging(pm1)"]
    C13D1 --> C13IMD["Check digitl_input[3]"]
    C13IMD -->|digitl_input[3]=='1'| C13IMD1["Red LED, stopcharging, stopActiveModules(pm1), STATUS1_GUN1_DATA[0]=9, open_load11"]
    C13IMD -->|digitl_input[3]=='0'| C13IMD2["STATUS1_GUN1_DATA[0]=5"]
    C13Branch -->|<=38000 and pm_assign2==3| C13D2["set limits, load11, pm1(1), startCharging(pm1)"]
    C13D2 --> C13IMD
    C13Branch -->|38000< and <=42000| C13D3["Check pm_assign1, if 1: set limits, load11, startCharging(1), if 2: set limits, load12, startCharging(1,3)"]
    C13D3 --> C13IMD
    C13Branch -->|42000< and <=78000| C13D4["pm1(1,3), set limits, load12, startCharging(pm1)"]
    C13D4 --> C13IMD
    C13Branch -->|78000< and <=82000 and pm_assign2==1 or ...| C13D5["Check pm_assign1, if 2: set limits, load12, startCharging(1,3), if 3: set limits, load13, startCharging(1,3,4)"]
    C13D5 --> C13IMD
    C13Branch -->|78000< and <=82000 and pm_assign2==2 or 3| C13D6["Check pm_assign1, if 2: set limits, load12, startCharging(1,3), if 3: set limits, load12, startCharging(1,3)"]
    C13D6 --> C13IMD
    C13Branch -->|>82000 and pm_assign2==1 or ...| C13D7["set limits, load13, pm1(1,3,4), startCharging(pm1)"]
    C13D7 --> C13IMD
    C13Branch -->|>82000 and pm_assign2==2 or 3 or target_power_from_car2>42000| C13D8["set limits, load12, pm1(1,3), startCharging(pm1)"]
    C13D8 --> C13IMD
    C13 --> C14
    C14 -->|true| C14Actions["Red LED, updateVI_status, stopActiveModules(1,2,3,4), readModule_Voltage/Current, STATUS1_GUN1_DATA[0]=1"]
    C14 --> C15
    C15 -->|true| C15Actions["Red LED, updateVI_status, stopActiveModules(1,2,3,4), readModule_Voltage/Current, STATUS1_GUN1_DATA[0]=1"]
    C15 --> C16
    C16 -->|true| C16Branch["Red LED, updateVI_status, check pm_assign1"]
    C16Branch -->|pm_assign1==1| C16A1["stopActiveModules(1), readModule_Voltage/Current(1)"]
    C16Branch -->|pm_assign1==2| C16A2["stopActiveModules(1,3), readModule_Voltage/Current(1,3)"]
    C16Branch -->|pm_assign1==3| C16A3["stopActiveModules(1,3,4), readModule_Voltage/Current(1,3,4)"]
    C16 --> C17
    C17 -->|true| C17Branch["Red LED, updateVI_status, check pm_assign1"]
    C17Branch -->|pm_assign1==1| C17A1["stopActiveModules(1), readModule_Voltage/Current(1)"]
    C17Branch -->|pm_assign1==2| C17A2["stopActiveModules(1,3), readModule_Voltage/Current(1,3)"]
    C17Branch -->|pm_assign1==3| C17A3["stopActiveModules(1,3,4), readModule_Voltage/Current(1,3,4)"]
    C17 --> End([End])
```

---

## Notes

- Each main condition (C1–C17) corresponds to a specific combination of `vehicle_status1` and `vehicle_status2_g`.
- Sub-conditions (such as IMD checks, module assignments, and demand conditions) are handled within each main branch.
- Actions include setting LED states, stopping/starting modules, updating status arrays, and calling helper functions.
- The flow is highly dependent on the values of `vehicle_status1`, `vehicle_status2_g`, and digital input states.

---

## References

- [`Vehicle1StatusReader`](power_120kw/can_readers/vehicle1_status_reader.py)
- [`PECC`](../../constants.py)
- [`CanId`](../../constants.py)
- [`Module1Message`](../message_helper.py)
- [`ConstantManager120KW`](../constant_manager_120kw.py)
