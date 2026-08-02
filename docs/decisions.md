API

Decision: To save each json result from an api request as a seperate, timestamped file
Reason: This makes the timestamp easily fetchable and each request is accounted for making failures tracable
Trade Off: This creates a lot of seperate files, it is ok for this project but on a larger scale these files would need to be compacted

BRONZE / SILVER LAYERS

Decision: Keep bronze layer as raw, unmanipulated data
Reason: Raw input is preserved incase goals change or errors deform the dataset

Decision: Splitting observational / station data into different files
Reason: Due to the sheer size of the data each additional column costs a large increase in storage, this data rarely changes and is largely repeated therefore only one table needs to be maintained
Risk: The data changes unexpectedly, leaving the data using old data
Goal: Add in a check which updates upon a change every time it is run, storing the datetime of the last time it was updated
