import sys
import os
import csv
import time

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import TripLogger

# Simulated sensor readings representing a real driving session
SIMULATED_SENSOR_DATA = [
    ("RPM",          1500,  "rpm"),
    ("SPEED",        60,    "kph"),
    ("COOLANT_TEMP", 90,    "degC"),
    ("ENGINE_LOAD",  45.2,  "percent"),
    ("THROTTLE_POS", 22.0,  "percent"),
]

EXPECTED_COLUMNS = ["Timestamp_Unix", "PID", "Value", "Unit", "DTC_Codes"]


def test_validate_trip_log_written_with_valid_data(tmp_path):
    """
    Validation test: simulates a driving session logging multiple sensor
    readings and verifies the resulting CSV is complete and well-formed.
    """
    # Log a simulated trip
    logger = TripLogger(log_dir=str(tmp_path))
    trip_start = time.time()

    for pid, value, unit in SIMULATED_SENSOR_DATA:
        logger.log(pid, value, unit)

    logger.close()
    trip_end = time.time()

    # Locate the output file
    files = list(tmp_path.glob("trip_*.csv"))
    assert len(files) == 1, "Expected exactly one trip log file to be created"
    filepath = files[0]

    # Read and validate the CSV
    with open(filepath) as f:
        reader = csv.DictReader(f)

        # Validate header columns
        assert reader.fieldnames == EXPECTED_COLUMNS, (
            f"CSV header mismatch. Got: {reader.fieldnames}"
        )

        rows = list(reader)

    # Validate row count
    assert len(rows) == len(SIMULATED_SENSOR_DATA), (
        f"Expected {len(SIMULATED_SENSOR_DATA)} rows, got {len(rows)}"
    )

    # Validate each row matches what was logged
    for i, (pid, value, unit) in enumerate(SIMULATED_SENSOR_DATA):
        row = rows[i]

        assert row["PID"] == pid, \
            f"Row {i}: expected PID '{pid}', got '{row['PID']}'"

        assert row["Value"] == str(value), \
            f"Row {i}: expected Value '{value}', got '{row['Value']}'"

        assert row["Unit"] == unit, \
            f"Row {i}: expected Unit '{unit}', got '{row['Unit']}'"

        assert row["DTC_Codes"] == "", \
            f"Row {i}: expected empty DTC_Codes, got '{row['DTC_Codes']}'"

        ts = float(row["Timestamp_Unix"])
        assert trip_start <= ts <= trip_end, \
            f"Row {i}: timestamp {ts} is outside the expected range"
