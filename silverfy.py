import os
import json

data_timegrouped = {}
data_cleaned = {}

for dirName, subDirList, fileList in os.walk('C:/Users/jaack/Desktop/cycle-availability-predictor/data/bronze'):
    for file in fileList:
        if file.endswith(".json"):
            with open(f"{dirName}/{file}") as f:
                d = json.load(f)
                data_timegrouped[file]=d

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

        data_cleaned["datetime"]=data_in
        data_cleaned["id"]=ins["id"]
        data_cleaned["commonName"]=ins["commonName"]
        data_cleaned["type"]=ins["placeType"]
        data_cleaned["terminalId"]=addP[0]["value"]
        data_cleaned["installed"]=addP[1]["value"]
        data_cleaned["locked"]=addP[1]["value"]
        data_cleaned["install_date"]=addP[1]["value"]
        data_cleaned["removal_date"]=addP[1]["value"]
        data_cleaned["temp"]=addP[1]["value"]
        data_cleaned["bikes_av"]=addP[1]["value"]
        data_cleaned["bikes_unav"]=addP[1]["value"]
        data_cleaned["total_bikes"]=addP[1]["value"]
        data_cleaned["stand_bike"]=addP[1]["value"]
        data_cleaned["e_bike"]=addP[1]["value"]
        data_cleaned["lat"]=addP[1]["value"]
        data_cleaned["lon"]=addP[1]["value"]

        print(data_cleaned)
        
