import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    force=True,
)

BRONZE_PATH = Path.cwd()/"data"/"bronze"
SILVER_PATH = Path.cwd() / "data" / "silver"
OBSERVATIONS_PATH = SILVER_PATH / "observations"
STATIONS_PATH = SILVER_PATH / "stations"

WANTED_COLUMNS = [
    "NbBikes",
    "NbEBikes",
    "NbStandardBikes",
    "NbDocks",
    "NbEmptyDocks"
]

REFERENCE_COLUMNS = [
     "id",
    "lat",
    "lon",
    "commonName"
]

REQUIRED_COLUMNS = [
    "id",
    "additionalProperties"
]

def checkFile(file: Path):

    def fail(name: str, reason: str) -> tuple[pd.DataFrame | None, datetime | None, dict[str, str] | None]:
            logging.warning("Skipping: %s (%s)", name, reason)
            return(None, None, {"file": name, "reason": reason})

    if not file.is_file():
            return fail(file.name, "Not a file")
                
    if file.stat().st_size == 0:
        return fail(file.name, "Empty file")

    if file.name.endswith("_FAILED.json"):
        return fail(file.name, "Failed API request")

    if len(file.name) != 33:
        return fail(file.name, "Invalid filename size")

    try:
        time = (file.name[10:-5])
        date_time = datetime.strptime(
            time,
            "%Y-%m-%d-H%H-M%M"
        )

        with file.open("r", encoding="utf-8") as f:
            json_input = json.load(f)

        if not isinstance(json_input, list):
            return fail(file.name, "Not JSON input")

        if not json_input:
            return fail(file.name, "Contains an empty list")
        
    except json.JSONDecodeError as e:
        return fail(file.name, "Invalid JSON input")

    except OSError as error:
        return fail(file.name, f"Could not read file: {error}")
    
    except ValueError as e:
        return fail(file.name, "Couldn't extract datetime")

    except Exception as e:
        return fail(file.name, f"Unexpected error: {e}")

    return pd.json_normalize(json_input), date_time, None

def transform_snapshot(file: Path) -> tuple[pd.DataFrame | None, dict[str, str] | None]:

    raw_df, date_time, error = checkFile(file)

    if error is not None:
         return None, error

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in raw_df.columns:
            missing_columns.append(column)

    if missing_columns:
        return None, {"file":file.name, "reason":f"Missing column(s): {missing_columns}"}

    df = raw_df[REQUIRED_COLUMNS].copy()
    
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

    wanted_rows = dfx_filtered[dfx_filtered["key"].isin(WANTED_COLUMNS)]

    df_pivot = wanted_rows.pivot(index=["id", "date_time"], columns="key", values="value")

    new_df = df_pivot.loc[:, WANTED_COLUMNS].copy()
    new_df = new_df.astype("Int64")
    new_df = new_df.reset_index()

    return new_df, None

def create_station_ref(file: Path) -> tuple[pd.DataFrame | None, dict[str, str] | None]:

    raw_df, date_time, error = checkFile(file)

    if error is not None:
         return None, error

    missing_columns = []

    for column in REFERENCE_COLUMNS:
        if column not in raw_df.columns:
            missing_columns.append(column)
    
    if missing_columns:
        return None, {"file":file.name, "reason":f"Missing column(s): {missing_columns}"}

    station_df = raw_df[REFERENCE_COLUMNS].copy()

    station_df = station_df.drop_duplicates(subset=["id"], keep="last").sort_values("id").reset_index(drop=True)

    station_df["updated_at"] = date_time

    return station_df, None

def save_station_ref(station_df: pd.DataFrame) -> Path:
    STATIONS_PATH.mkdir(parents=True, exist_ok=True)
    output_file = STATIONS_PATH/"stations.parquet"

    station_df.to_parquet(output_file, index=False)
    logging.info(f"Saved {len(station_df)} stations to {output_file}")

    return output_file

def save_daily_observation(daily_df: pd.DataFrame, day: str) -> Path:
    day_path = OBSERVATIONS_PATH / f"date={day}"
    day_path.mkdir(parents=True, exist_ok=True)
    output_file = day_path/"observation.parquet"

    daily_df.to_parquet(output_file, index=False)
    logging.info(f"Saved {len(daily_df)} observations to {output_file}")

    return output_file

def transform_day(day: str) -> pd.DataFrame | None:
    observation_dfs = []
    failed_files = []

    day_files = sorted(
        BRONZE_PATH.glob(f"tfl-bikes-{day}*.json")
    )

    for file in day_files:

        if not file.name.startswith(f"tfl-bikes-{day}"):
            continue

        observation_df, error = transform_snapshot(file)

        if error is not None:
            failed_files.append(error)
            continue
        
        observation_dfs.append(observation_df)

    if not observation_dfs:
            return None, failed_files

    daily_df = pd.concat(
        observation_dfs,
        ignore_index=True,
    )

    successful_count = len(observation_dfs)
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

#mode = "instance"
#mode = "day"
#mode = "ref"
mode = "catchup"

def main() -> None:

    def find_unwritten_days() -> set[datetime.date]:
        unique_dates = set()
        unique_bronze = set()

        for file in BRONZE_PATH.iterdir():

            try:
                date_text = file.name[10:20]
                parsed_date = datetime.strptime(date_text, "%Y-%m-%d").date()
                unique_bronze.add(parsed_date)
                if not (SILVER_PATH / "observations" / f"date={parsed_date}" / "observation.parquet").exists():
                    unique_dates.add(parsed_date)

            except Exception as e:
                logging.warning(f"Error: {e}")

        if len(unique_dates)>1:
            latest = max(unique_bronze)
            unique_dates.remove(latest)
            logging.info(f"REMOVING {latest} due to being most recent partial file")
            logging.info(f"Processing dates {unique_dates}...")
            return(sorted(unique_dates))
        else:
            logging.warning("No files left")
            return []

        
        

    if mode == "catchup":
        logging.info("Catch Up Loading...")

        days = find_unwritten_days()

        for day in days:

            logging.info("Processing catch-up date: %s", day)

            daily_df, failed_files = transform_day(day)

            if daily_df is not None:
                save_daily_observation(
                    daily_df,
                    day
                )
            else:
                logging.warning(f"No file for date {day}")


    elif mode == "day":
        day_string = "2026-07-25"
        daily_df, failed_files = transform_day(day_string)
        if daily_df is not None:
            print(daily_df.tail(5))
            save_daily_observation(daily_df, day_string)

        for error in failed_files:
            print(error)

    else:
         
        snapshot = "tfl-bikes-2026-07-24-H12-M45.json"
        file = BRONZE_PATH / snapshot

        if mode == "instance":
            df, errors = transform_snapshot(file)
            print(df.head(10))

        if mode == "ref":
            df_ref, fail = create_station_ref(file)
            if fail is None:
                print(df_ref.head(10))
                save_station_ref(df_ref)


if __name__ == "__main__":
    main()