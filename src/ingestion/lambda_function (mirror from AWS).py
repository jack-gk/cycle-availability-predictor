import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime, timezone
import requests
import time
import logging

BUCKET_NAME = "tfl-bikes-json"

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def save_file(time_string, bucket, body, error=False):
    client = boto3.client('s3')
    logger.info("Client connected to s3")

    if error:
        key = f"tfl-bikes-{time_string}_FAILED.json"
        logger.error("Filetype: ERROR")
    else:
        key = f"tfl-bikes-{time_string}.json"
        logger.info("Filetype: DATA")

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body
    )
    logger.info("File saved successfully: s3://%s/%s", bucket, key)

class InvalidTfLResponseError(Exception):
    # TODO Error Handling
    pass

def lambda_handler(event, context):

    time_string = datetime.now(timezone.utc).strftime("%Y-%m-%d-H%H-M%M")

    url = "https://api.tfl.gov.uk/BikePoint/"
    logger.info("URL is: %s",url)

    total_attempts = 2

    logger.info("Total attempts are: %s", total_attempts)

    if not isinstance(total_attempts, int) or total_attempts < 1:
        raise ValueError("total_attempts must be a positive integer")

    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")
    
    for attempt_no in range(1, total_attempts + 1):

        try:
            logger.info("Attempt %s of %s", attempt_no, total_attempts)

            logger.info("Connecting to TFL API")
            r = requests.get(url, timeout=15)

            logger.info("Response recieved: %s", r.status_code)
            
            r.raise_for_status()
            response = r.json()

            if not isinstance(response, list) or not response:
                raise InvalidTfLResponseError("TfL response was not a non-empty list")

            save_file(time_string, BUCKET_NAME, json.dumps(response))

            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully saved file tfl-bikes-{time_string}.json')
            }
        
        except requests.exceptions.JSONDecodeError as e:
            logger.error("Result isnt decodable with JSON: %s",e)

            if attempt_no == total_attempts:
                save_file(time_string, BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
                raise

            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

        except InvalidTfLResponseError as e:
            logger.error("Empty or invalid TFL Response: %s", e)

            if attempt_no == total_attempts:
                save_file(time_string, BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
                raise

            logger.info("Retrying in 5 seconds...")
            time.sleep(5)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            retryable_statuses = {408, 429, 500, 502, 503, 504}

            if status_code in retryable_statuses:
                logger.warning("Temporary HTTP error: status=%s",status_code)
                if attempt_no == total_attempts:
                    logger.warning("Final attempt failed")
                    save_file(time_string, BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
                    raise
                logger.info(f"Waiting 5 seconds before retrying")
                time.sleep(5)
            else:
                logger.error("Permanent HTTP error (do not retry)")
                save_file(time_string, BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
                raise

        except (ClientError, BotoCoreError) as e:
            logger.exception("S3 operation failed")
            raise

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt_no == total_attempts:
                save_file(time_string,BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
                raise

            logger.warning("Connection failure, retrying in 5 seconds")
            time.sleep(5)

        except Exception as e:
            logger.exception("Unexpected error occurred: %s",e)
            save_file(time_string, BUCKET_NAME, json.dumps({"error": str(e)}), error=True)
            raise