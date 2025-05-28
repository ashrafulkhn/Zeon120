import threading
import time
import random

x = 20000
demand = x
read_val = 0
limitChangeRequested = False
pm_assigned1 = 0

def setLimit(limit_power):
    print(f"Limit set to {limit_power/1000}kW")

def limitChangeRequest(limit_to_check):
    global limitChangeRequested
    val = abs(limit_to_check - read_val)
    if val < 2000:
        limitChangeRequested = True
    else:
        limitChangeRequested = False  # Fixed assignment operator

def pmUsed(len):
    return len

def start(pm):
    global pm_assigned1
    pm_assigned1 = len(pm)
    pmUsed(len(pm))

# Precharge limit 30kW -> 20kW

def conditions():
    if demand <= 29000:     
        setLimit(25000)
        limitChangeRequest(25000)

        if limitChangeRequested == False:
            start(pm1=[1])
        else:
            setLimit(55000)
            limitChangeRequested = False

    if (29000 < demand < 31000):
        limitChangeRequest(29000)
        if limitChangeRequested == True:
            setLimit(55000)
            limitChangeRequested = False

        if pm_assigned1 == 1:
            start(pm=[1])
        elif pm_assigned1 == 2:
            start(pm=[1,3])
        

    if 31000 < demand < 59000:
        setLimit(55000)
        limitChangeRequest(55000)

        if limitChangeRequested == False:
            start(pm=[1])
        else:
            limitChangeRequested = False
            setLimit(85000)

    if 59000 < demand < 61000:
        limitChangeRequest(59000)
        if limitChangeRequested == True:
            setLimit(85000)
            limitChangeRequested = False
        # setLimit(85000)
        if pm_assigned1 == 2:
            start(pm=[1, 3])
        elif pm_assigned1 == 3:
            start(pm=[1,3,4])

    if 61000 < demand < 89000:
        setLimit(85000)
        limitChangeRequest(85000)
        if limitChangeRequested == False:
            start(pm=[1,3,4])
        else:
            limitChangeRequested=False
            setLimit(12000)

    if demand > 89000:
        start(pm=[1,3,4,2])

def update_demand():
    global demand
    while True:
        # Gradually increase demand from 0 to 120kW (120000W)
        for d in range(0, 120001, 1000):  # Step by 1kW
            demand = d
            print(f"\nDEMAND UPDATE: Current demand = {demand/1000:.1f} kW")
            time.sleep(1)  # Wait 1 second between updates
        
        # Reset to 0 when reaching max
        demand = 0
        print("\nDEMAND RESET: Restarting demand cycle")

def update_read_val():
    global read_val
    while True:
        # Read value should follow demand but stay slightly below
        target = demand * random(0.8, 0.95)  # Stay 5% below demand
        
        # Gradually increase/decrease read_val towards target
        if read_val < target:
            read_val += random.randint(500, 1000)  # Random increase between 0.5-1kW
        elif read_val > target:
            read_val = target  # Immediately adjust if we somehow go over
            
        print(f"READ UPDATE: Current read value = {read_val/1000:.1f} kW")
        time.sleep(0.5)  # Update twice per second

def main():
    global demand, read_val
    
    print("Starting power monitoring simulation...")
    print("=======================================")
    
    # Create threads for updating demand and read values
    demand_thread = threading.Thread(target=update_demand, daemon=True)
    read_thread = threading.Thread(target=update_read_val, daemon=True)
    
    # Start threads
    print("Starting demand and read value monitors...")
    demand_thread.start()
    read_thread.start()
    
    # Main loop to check conditions
    try:
        while True:
            conditions()  # Check conditions based on current demand/read values
            time.sleep(1)  # Check conditions every second
            
            # Print status summary
            print(f"\nSTATUS SUMMARY:")
            print(f"Demand Power: {demand/1000:.1f} kW")
            print(f"Read Power: {read_val/1000:.1f} kW")
            print(f"Difference: {(demand-read_val)/1000:.1f} kW")
            print("=======================================")
            
    except KeyboardInterrupt:
        print("\nShutting down simulation...")
        return

if __name__ == "__main__":
    main()