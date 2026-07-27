# File to check if the downloaded bronze data is 
# missing any datapoints


from pathlib import Path
from datetime import datetime, timedelta
import time

path = Path(__file__).resolve().parent
bronze_path = path/"data"/"bronze"

name_layout = "tfl-bikes-"

# time tracker starting with the first input
time_input = datetime(2026,7,24,12,45)

for file in list(bronze_path.iterdir()):

    time_track = name_layout+(time_input).strftime("%Y-%m-%d-H%H-M%M")+".json"
    
    if file.name != time_track:
        # Branch if file doesn't exist
        print(f"{file.name} wasn't found")
        print(f"{time_track} wasn't found")
    elif not file.read_bytes():
        # Brand if file empty
        print(f"File empty: {file.name}")
    else:
        # Branch if no problem
        pass
        # print(f"Looks ok: {file.name}")
    time_input = time_input+timedelta(minutes=5)

print(f"Finished Search")
print(f"Synced up to : {time_input}")

