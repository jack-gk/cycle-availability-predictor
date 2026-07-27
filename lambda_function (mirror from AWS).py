"""
Lambda function hosted on AWS to collect bronze data from the TFL API 
endpoint every 5 minutes and store it in S3.
"""


import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime
import requests
import time

def save_file(time_string, bucket, body, error=False):
    client = boto3.client('s3')
    print("Client connected to s3")

    if error:
        key = f"tfl-bikes-{time_string}_FAILED.json"
        print("Filetype: ERROR")
    else:
        key = f"tfl-bikes-{time_string}.json"
        print("Filetype: DATA")

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=body
    )
    print("File saved to s3")

class InvalidTfLResponseError(Exception):
    pass

def lambda_handler(event, context):

    time_string = datetime.now().strftime("%Y-%m-%d-H%H-M%M")

    url = event.get("url")
    print("URL is:", url)

    total_attempts = event.get("total_attempts")
    print("Total attempts are:", total_attempts)

    if not isinstance(total_attempts, int) or total_attempts < 1:
        raise ValueError("total_attempts must be a positive integer")

    if not isinstance(url, str) or not url.strip():
        raise ValueError("url must be a non-empty string")
    
    for attempt_no in range(1, total_attempts + 1):

        try:
            print(f"Attempt {attempt_no} of {total_attempts}")

            print("Connecting to TFL API")
            r = requests.get(url, timeout=15)

            print("Response recieved:", r.status_code)

            r.raise_for_status()

            response = r.json()

            if not isinstance(response, list) or not response:
                raise InvalidTfLResponseError("TfL response was not a non-empty list")

            save_file(time_string, "tfl-bikes-dev", json.dumps(response))

            return {
                'statusCode': 200,
                'body': json.dumps(f'Successfully saved file tfl-bikes-{time_string}.json')
            }
        
        except requests.exceptions.JSONDecodeError as e:
            print("Result isnt decodable with JSON", e)

            if attempt_no == total_attempts:
                save_file(time_string, "tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
                raise

            print("Retrying in 5 seconds...")
            time.sleep(5)

        except InvalidTfLResponseError as e:
            print("Empty or invalid TFL Response", e)

            if attempt_no == total_attempts:
                save_file(time_string, "tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
                raise

            print("Retrying in 5 seconds...")
            time.sleep(5)

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            retryable_statuses = {408, 429, 500, 502, 503, 504}

            if status_code in retryable_statuses:
                print("Temporary HTTP error")
                if attempt_no == total_attempts:
                    print("Final attempt failed")
                    save_file(time_string, "tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
                    raise
                print(f"Waiting 5 seconds before retrying")
                time.sleep(5)
            else:
                print("Permanent HTTP error (do not retry)")
                save_file(time_string, "tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
                raise

        except (ClientError, BotoCoreError) as e:
            print("S3 operation failed:", e)
            raise

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt_no == total_attempts:
                save_file(time_string,"tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
                raise

            print("Connection failure, retrying in 5 seconds")
            time.sleep(5)

        except Exception as e:
            print("Unexpected error occurred:",e)
            save_file(time_string, "tfl-bikes-dev", json.dumps({"error": str(e)}), error=True)
            raise