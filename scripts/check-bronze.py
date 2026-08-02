from pathlib import Path
from datetime import datetime, timedelta
import logging

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    force=True
    )

path = Path(__file__).resolve().parent
bronze_path = path/"data"/"bronze"

name_layout = "tfl-bikes-"

# time tracker starting with the first input
time_input = datetime(2026,7,24,12,45)

for file in list(bronze_path.iterdir()):

    time_track = name_layout+(time_input).strftime("%Y-%m-%d-H%H-M%M")

    if file.name == (time_track+"_FAILED.json"):
        # Check if file failed to download
        logger.info(f"{file.name} failed to download")
        # TODO 
        # Show the error code

    elif file.name != (time_track+".json"):
        # Branch if file doesn't exist
        logger.info(f"{file.name} wasn't found")

    elif not file.read_bytes():
        # Branch if file empty
        logger.info(f"{file.name} is empty")
    else:
        # Branch if no problem
        pass
        # print(f"Looks ok: {file.name}")
    time_input = time_input+timedelta(minutes=5)

print(f"Finished Search")
print(f"Synced up to : {time_input}")

