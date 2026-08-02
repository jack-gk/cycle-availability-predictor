# Cycle Availability Predictor

An end-to-end data science project that collects TfL cycle availability data from the public API every 5 minutes using AWS Lambda scheduled by EventBridge. This bronze data (raw json) is stored inside of AWS S3, it is then transformed and validated through the silver and curated to the gold layer where further implementation hasn't been developed yet. (Plans of creating a prediction model using this data)

## Pipeline

TfL API > EventBridge Scheduler > AWS Lambda > S3 Bronze data (raw JSON) > Silver data transformation (parquet files) > Gold data (curated datasets)

## Reliability and Failure Handling

Implemented:

- Scheulded API collection
  An EventBridge scheduler triggers a lambda function which stores the result inside of S3 every 5 minutes

- Response validation
  The lamda function checks the response before blindly saving

- Retry handling, timeout
  The lambda function retries certain failures such as server issues or connection throttled.
  Timeout is also utilised so there is no hanging requests
  After maximum retries the email is notified and a FAILED file is saved

- Timestamped S3 storage
  Upon successful API request, the data is stored within S3 labelled with its timestamp

- File validation: filename, data checks, failure handling/logging
  During the silver processing layer, the data is heavily checked and validated before allowing further action.
  Checks include: file type, file name, file size, required columns, duplicates
  Each failure is handled gracefully and logged with its ID and the failure reason

- Local Bronze > Silver transformation
  Successfully transforms raw JSON to daily aggregated parquet files

- Local Silver storage
  Storage of observations and station info

Planned:

- Automatic silver daily processing
  Eventually the whole pipeline would be functionable autonomously, with human input only being required for changes or unexpected errors

- More detailed dead-letter handling
  The lambda function retries certain failures such as server issues or connection throttled.
  If all attempts fail, an SNS notification is sent to a personal email address.
  This provides failure alerts, at the moment it does not provide auto replay afterwards

- Data quality alarts
  Notification when the response seems valid however the data provided isnt sufficient

- Gold-layer forecasting
  A model which can as acurately as possible predict the outcome within a nearby time based upon previous datapoints
