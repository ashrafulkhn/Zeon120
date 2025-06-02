global_demand = 32000
limit1 = 0
def setLimit(limit):
    global limit1
    limit1 = limit
def getPresetLimit():
    return limit1

def main():
    while True:
        demand = min(getPresetLimit(), global_demand)
        print("Smaller number is:", demand)
        if demand <=29000:
            setLimit(55000)