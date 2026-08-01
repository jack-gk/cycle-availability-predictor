import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    force=True,
)

bronze_path = Path.cwd()/"data"/"bronze"

WANTED_COLUMNS = [
    "NbBikes",
    "NbEBikes",
    "NbStandardBikes",
    "NbDocks",
    "NbEmptyDocks",
]

REQUIRED_COLUMNS = [
    "id",
    "additionalProperties",
]

def validate_file(file: Path) -> dict | None:

    if not file.is_file():
        logging.warning("Skipping: %s", file.name)
        return({"file": file.name, "reason": "Not a file"})
            
    if file.stat().st_size == 0:
        logging.warning("Skipping empty file: %s", file.name)
        return({"file": file.name, "reason": "Empty File"})

    if file.name.endswith("_FAILED.json"):
        logging.warning("Skipping failed file: %s", file.name)
        return({"file": file.name, "reason": "Failed API Request"})
        
        
    valid_name = (
        file.name.startswith("tfl-bikes-")
        and file.name.endswith(".json")
        and len(file.name) == 33
    )

    if not valid_name:
        logging.error("Invalid filename: %s", file.name)
        return {
            "file": file.name,
            "reason": "Invalid naming convention",
        }
        
    return None

def transform_snapshot(file: Path) -> pd.DataFrame | dict:
            
        flag = validate_file(file)
        
        if flag is not None:
            return None, flag
        try:
            time = (file.name[10:-5])
            date_time = datetime.strptime(
                time,
                "%Y-%m-%d-H%H-M%M"
            )

            with file.open("r", encoding="utf-8") as f:
                json_input = json.load(f)
    
            if not isinstance(json_input, list):
                logging.warning(
                    "%s contains %s instead of a list",
                    file.name,
                    type(json_input).__name__,
                )
                return(None, {"file":file.name, "reason":"Not JSON input"})

            if not json_input:
                logging.warning("%s contains an empty list", file.name)
                return(None, {"file":file.name, "reason":"Contains an empty list"})

        
        except ValueError as e:
            logging.warning(f"{file.name} failed to extract datetime")
            return(None, {"file":file.name, "reason":"Couldn't Extract Datetime"})
        
        except json.JSONDecodeError as e:
            logging.warning(f"Skipping invalid JSON file: {file.name}")
            return(None, {"file":file.name, "reason":"Invalid JSON input"})

        except Exception as e:
            logging.warning(f"Unexpected error in file: {file.name}")
            return(None, {"file":file.name, "reason":e})

        
        df = pd.json_normalize(json_input)
    
        df = df[REQUIRED_COLUMNS]
        df["date_time"] = date_time

        df_long = df.explode("additionalProperties",True)

        properties = pd.json_normalize(
            df_long["additionalProperties"]
        )
        dfx = pd.concat(
            [
                df_long[["id", "date_time"]],
                properties
            ],
            axis=1
        ) 
        
        dfx_filtered = dfx[["id", "date_time", "key", "value"]]
        wanted = ["NbBikes", "NbStandardBikes", "NbEBikes", "NbEmptyDocks", "NbDocks"]

        wanted_rows = dfx_filtered[dfx_filtered["key"].isin(wanted)]

        df_pivot = wanted_rows.pivot(index=["id", "date_time"], columns="key", values="value")

        new_df = df_pivot.loc[:, WANTED_COLUMNS].copy()
        new_df = new_df.astype("Int64")
        new_df = new_df.reset_index()

        return new_df, None

def transform_day(day: str) -> pd.DataFrame | None:
    snapshot_dfs = []
    failed_files = []
    
    day_files = sorted(
        bronze_path.glob(f"tfl-bikes-{day}*.json")
    )

    for file in day_files:

        if not file.name.startswith(f"tfl-bikes-{day}"):
            continue

        snapshot_df, error = transform_snapshot(file)

        if error is not None:
            failed_files.append(error)
            continue
        
        snapshot_dfs.append(snapshot_df)
        logging.info(file.name)

    if not snapshot_dfs:
            return None, failed_files

    daily_df = pd.concat(
        snapshot_dfs,
        ignore_index=True,
    )

    successful_count = len(snapshot_dfs)
    failed_count = len(failed_files)
    total_count = successful_count + failed_count

    logging.info(
        "Day %s: %d/%d files transformed successfully; %d failed",
        day,
        successful_count,
        total_count,
        failed_count,
    )

    return daily_df, failed_files


def main() -> None:
    day_string = "2026-07-24"

    daily_df, failed_files = transform_day(day_string)

    if daily_df is not None:
        print(daily_df.tail(5))

    for error in failed_files:
        print(error)


if __name__ == "__main__":
    main()