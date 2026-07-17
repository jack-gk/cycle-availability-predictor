
import requests

url = "https://api.tfl.gov.uk/BikePoint/"

r = requests.get(url)
response = r.json()
#print(len(response))
#print(len(response))

for i in range(20):

    ins = response[i]
    addP = ins["additionalProperties"]

    id = ins["id"]
    location = ins["commonName"]
    placeType = ins["placeType"]

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

    print("---")
    print("ID:",id)
    print("Common Name:",location)
    print("Type:",placeType)
    print("terminal_id:",terminalid)
    print("Installed:",installed)
    print("Locked:",locked)
    print("Install Date:",install_date)
    print("Removal Date:",removal_date)
    print("Temperary:",temp)
    print("Bikes Available:",bikes_av)
    print("Bikes Unavailable:",bikes_unav)
    print("Total Bikes:",total_bikes)
    print("Standard Bikes:",stand_bike)
    print("E-Bikes:",e_bike)
    print("Latitude:",lat)
    print("Longitude:",lon)