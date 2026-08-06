import pytest
import pathlib
import pandas as pd
import json
import datetime

from src.transformation import bronze_to_silver as bts

def test_empty_file_is_rejected(tmp_path):
    # Arrange
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M56.json"
    test_file.touch()

    # Act
    station_df, error = bts.create_station_ref(test_file)

    # Assert
    assert station_df is None
    assert error is not None

    print(error["reason"])

def test_invalid_json(tmp_path):
    # Arrange
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M57.json"
    test_file.write_text(
        "{this is not valid JSON"
    )

    # Act
    station_df, error = bts.create_station_ref(test_file)

    # Assert
    assert station_df is None
    assert error is not None

    print(error["file"], error["reason"])

def test_valid_station(tmp_path):
    # Arrange
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M58.json"
    station_data = [
        {
            "id": "BikePoints_1",
            "lat": 51.5,
            "lon": -0.1,
            "commonName": "Test Station",
            "additionalProperties": [],
        }
    ]
    test_file.write_text(json.dumps(station_data))

    # Act
    station_df, error = bts.create_station_ref(test_file)

    # Assert
    assert station_df is not None
    assert error is None

    print(station_df.head(10))

def test_no_common_name(tmp_path):
    # Arrange
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M58.json"
    station_data = [
        {
            "id": "BikePoints_1",
            "lat": 51.5,
            "lon": -0.1,
            "additionalProperties": [],
        }
    ]
    test_file.write_text(json.dumps(station_data))

    # Act
    station_df, error = bts.create_station_ref(test_file)

    # Assert
    assert station_df is None
    assert error is not None

    print(error["file"], error["reason"])

def test_valid_additionalProperties(tmp_path):
    # Arrange
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M58.json"
    station_data = [
        {
            "id": "BikePoints_1",
            "lat": 51.5,
            "lon": -0.1,
            "commonName": "BikePoint1",
            "additionalProperties": [
                {"key": "NbBikes", "value": "7"},
                {"key": "NbEBikes", "value": "2"},
                {"key": "NbStandardBikes", "value": "5"},
                {"key": "NbDocks", "value": "20"},
                {"key": "NbEmptyDocks", "value": "13"},
            ]
        }
    ]
    test_file.write_text(json.dumps(station_data))

    # Act
    result_df, error = bts.transform_snapshot(test_file)

    # Assert
    assert result_df is not None
    assert error is None
    assert len(result_df) == 1
    assert result_df.loc[0, "NbBikes"] == 7
    assert result_df.loc[0, "NbEBikes"] == 2
    assert result_df.loc[0, "NbStandardBikes"] == 5
    dt = datetime.datetime(2026, 7, 24, 12, 58)

    assert result_df.loc[0, "date_time"] == dt

def test_duplicate_entry(tmp_path):
    test_file = tmp_path / "tfl-bikes-2026-07-24-H12-M58.json"
    station_data = [
        {
            "id": "BikePoints_1",
            "lat": 51.5,
            "lon": -0.1,
            "commonName": "BikePoint1",
            "additionalProperties": [
                {"key": "NbBikes", "value": "7"},
                {"key": "NbEBikes", "value": "2"},
                {"key": "NbStandardBikes", "value": "5"},
                {"key": "NbDocks", "value": "20"},
                {"key": "NbEmptyDocks", "value": "13"},
            ]
        },
        {
            "id": "BikePoints_1",
            "lat": 51.5,
            "lon": -0.1,
            "commonName": "BikePoint1",
            "additionalProperties": [
                {"key": "NbBikes", "value": "7"},
                {"key": "NbEBikes", "value": "2"},
                {"key": "NbStandardBikes", "value": "5"},
                {"key": "NbDocks", "value": "20"},
                {"key": "NbEmptyDocks", "value": "13"},
            ]
        }
    ]
    test_file.write_text(json.dumps(station_data))

    result_df, error = bts.transform_snapshot(test_file)

    

