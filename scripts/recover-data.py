import boto3
from pathlib import Path
import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    force=True
    )

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze"

s3 = boto3.resource('s3')

def download_data():
    bucket = s3.Bucket('tfl-bikes-json')

    actual_objects = {}
    
    for obj in bucket.objects.all():
        actual_objects[obj.key] = obj

    start_time = datetime(2026, 7, 24, 12, 45, tzinfo=timezone.utc)
    end_time = datetime.now(timezone.utc)-timedelta(minutes=5)

    logger.info("test")

    current_time = start_time

    while current_time <= end_time:
        expected_key = (
            "tfl-bikes-"
            + current_time.strftime("%Y-%m-%d-H%H-M%M")
            + ".json"
        )

        logger.info(expected_key)

        current_time += timedelta(minutes=5)

        # key = obj.key

        # destination = BRONZE_PATH/key

        # destination.parent.mkdir(parents=True, exist_ok=True)
        
        # if destination.is_file() and destination.stat().st_size == obj.size:
        #     logger.info("File %s already exists (and up to date)", key)
        #     continue
        
        # try:
        #     if obj.size == 0 and (not key.glob(f"tfl-bikes-{day}*.json")):
        #         logger.info("File %s is empty, added _FAILED suffix", key)

        #     bucket.download_file(key, str(destination))
        #     logger.info("File transferred (%s)",key)
        # except Exception:
        #     logger.exception("Failed to transfer %s",key)


if __name__ == "__main__":        
    download_data()