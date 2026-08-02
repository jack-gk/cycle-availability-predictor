<!--

Observations Table

      Column        |       Type        |       Desciption
----------------------------------------------------------------------------
    station_id      |      string       |   Unique location identifier
    observed_at     |     datetime      |   Snapshot collection time
    num_bikes       |      integer      |   Total bikes at location
    num_ebikes      |      integer      |   Total ebikes at location
num_standard_bikes  |      integer      |   Total standard bikes at location
    num_docks       |      integer      |   Total docks at location
  num_empty_docks   |      integer      |   Total spare docks at location



  Stations Table

      Column        |       Type        |       Desciption
----------------------------------------------------------------------------
    station_id      |      string       |   Unique station identifier
    common_name     |      string       |   Plainspeak station name
    latitude        |       float       |   Station latitude
    longitude       |       float       |   Station Longitude
    valid_from      |      datetime     |   (to add) When data was last synced

-->
