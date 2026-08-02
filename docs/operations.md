## Operations

- Ingestion has been setup to run automatically, I know if there is a problem due to the different checks
  which trigger a notification email upon failing
- Detailed logs have been added into the code for best debug and understanding practice.
  These logs are found on CloudWatch AWS servers and can be accessed through the lambda function dashboard
- When TfL returns an error, after the configured retries a file is saved with the "\_FAILED" suffix for
  easy identification later on, A notificaiton email is sent.
- If in the case an error is found during the silver output, or more data is needed in the original files:
  bronze is kept as the source of the data's historical truth. This is kept and can be reconfigured in
  different ways if needed

TODO

- Better EventBridge stopping procedures (not required at the moment within such a small project at minimal cost)
- Better duplicate handling within Bronze layer / Silver layer
