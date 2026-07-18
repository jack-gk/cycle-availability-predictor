import os
import json

data_timegrouped = {}

for dirName, subDirList, fileList in os.walk('C:/Users/jaack/Desktop/cycle-availability-predictor/data/bronze'):
    for file in fileList:
        if file.endswith(".json"):
            with open(f"{dirName}/{file}") as f:
                d = json.load(f)
                data_timegrouped[file]=d

print(data_timegrouped.keys())

for data_in in data_timegrouped.values():
    
    # data_in > LIST of all the entries from the single data_timegroup selected
    for ins in data_in:
        # ins is a dict of each location in the entry
        print("___")

        addP = ins["additionalProperties"]

        id = ins["id"]
        location = ins["commonName"]
        placeType = ins["placeType"]

        def checkNone(entry):
            if str(entry).strip() == "" or entry == None or entry == "None":
                return "Undefined"
            else:
                return entry

        terminalid = addP[0]["value"]
        installed = addP[1]["value"]
        locked = addP[2]["value"]
        install_date = addP[3]["value"]
        removal_date = addP[4]["value"]
        temp = addP[5]["value"]
        bikes_av = int(addP[6]["value"])
        bikes_unav = int(addP[7]["value"])
        total_bikes = int(addP[8]["value"])
        stand_bike = addP[9]["value"]
        e_bike = addP[10]["value"]
        lat = ins["lat"]
        lon = ins["lon"]

        print("ID:",id)
        print("Common Name:",location)
        print("Type:",placeType)
        print("terminal_id:",terminalid)
        print("Installed:",installed)
        print("Locked:",locked)
        print("Install Date:",checkNone(install_date))
        print("Removal Date:",checkNone(removal_date))
        print("Temperary:",temp)
        print("Bikes Available:",bikes_av)
        print("Bikes Unavailable:",bikes_unav)
        print("Total Bikes:",total_bikes)
        print("Standard Bikes:",stand_bike)
        print("E-Bikes:",e_bike)
        print("Latitude:",lat)
        print("Longitude:",lon)
