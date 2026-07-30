import os
import json
from pathlib import Path
import pandas as pd

def get_time(input_string):
    if input_string[-5:] == ".json":
        print("Taken Away .json")
        if input_string[:10] == "tfl-bikes-":
            print("Taken away prefix")
            return input_string[10:-5]
        
    raise ValueError("Input isnt to standard:",input_string)



path = Path(__file__).resolve().parent

data_timegrouped = {}
data_cleaned = {}

bronze_path = path/"data"/"bronze"

file_name = "tfl-bikes-2026-07-24-H13-M40.json"

date = get_time(file_name)
print(date)

with open(bronze_path/file_name) as f:
    # data_in > LIST of all the entries from the single data_timegroup selected
    data_in = json.load(f)
    for value in data_in[0]["additionalProperties"]:
        print(value.keys())

    df_cleaned = pd.json_normalize(data_in, record_path="additionalProperties", meta=["id", "commonName"], meta_prefix="location.")

    #df_cleaned = df_cleaned[df_cleaned["key"].isin(wanted)]
    
    print(df_cleaned.keys)

    
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

        # terminalid = addP[0]["value"]
        # installed = addP[1]["value"]
        # locked = addP[2]["value"]
        # install_date = addP[3]["value"]
        # removal_date = addP[4]["value"]
        # temp = addP[5]["value"]
        # bikes_av = int(addP[6]["value"])
        # bikes_unav = int(addP[7]["value"])
        # total_bikes = int(addP[8]["value"])
        # stand_bike = addP[9]["value"]
        # e_bike = addP[10]["value"]
        # lat = ins["lat"]
        # lon = ins["lon"]

        # data_cleaned["datetime"]=date
        # data_cleaned["id"]=ins["id"]
        # data_cleaned["commonName"]=ins["commonName"]
        # data_cleaned["type"]=ins["placeType"]
        # data_cleaned["terminalId"]=addP[0]["value"]
        # data_cleaned["installed"]=addP[1]["value"]
        # data_cleaned["locked"]=addP[1]["value"]
        # data_cleaned["install_date"]=addP[1]["value"]
        # data_cleaned["removal_date"]=addP[1]["value"]
        # data_cleaned["temp"]=addP[1]["value"]
        # data_cleaned["bikes_av"]=addP[1]["value"]
        # data_cleaned["bikes_unav"]=addP[1]["value"]
        # data_cleaned["total_bikes"]=addP[1]["value"]
        # data_cleaned["stand_bike"]=addP[1]["value"]
        # data_cleaned["e_bike"]=addP[1]["value"]
        # data_cleaned["lat"]=addP[1]["value"]
        # data_cleaned["lon"]=addP[1]["value"]

        for i in data_cleaned:
            print(f"{i} : {data_cleaned[i]}")
        
