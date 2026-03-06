import sys
import os
import csv

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import TripLogger

def test_trip_logger_writes_log_entry(tmp_path):
    """ A logged entry should appear in the CSV with correct values."""
    logger = TripLogger(log_dir=str(tmp_path))
    logger.log("RPM", 3000, "rpm")
    logger.close()

    filepath = list(tmp_path.glob("trip_*.csv"))[0]
    with open(filepath) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["PID"] == "RPM"
    assert rows[0]["Value"] == "3000"
    assert rows[0]["Unit"] == "rpm"
    assert rows[0]["DTC_Codes"] == ""
