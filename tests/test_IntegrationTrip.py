import sys
import os
import csv
import json
import time
from threading import Lock

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import CacheCallback, TripLogger, PublishVehicleData

# Fakes

class FakeValue:
    def __init__(self, magnitude, units):
        self.magnitude = magnitude
        self.units = units

class FakeCommand:
    def __init__(self, name):
        self.name = name

class FakeResponse:
    def __init__(self, name, magnitude, units):
        self.command = FakeCommand(name)
        self.value = FakeValue(magnitude, units)

    def is_null(self):
        return False

class FakePublisher:
    def __init__(self):
        self.messages = []

    def send_string(self, msg):
        self.messages.append(msg)

# Integration test

def test_integration_obd_response_logged_and_published(tmp_path):
    """
    Integration test: simulates a sequence of OBD sensor responses flowing
    through CacheCallback -> TripLogger -> PublishVehicleData, and verifies
    that data is correctly cached, written to CSV, and published over ZMQ.

    Components exercised:
        - CacheCallback: parses OBD responses into the shared cache
        - TripLogger: writes cache entries to a CSV log file
        - PublishVehicleData: publishes the cache as a ZMQ VEHICLE_DATA message
    """

    # Setup shared cache
    sensor_readings = [
        ("RPM",          3000, "rpm"),
        ("SPEED",        80,   "kph"),
        ("COOLANT_TEMP", 92,   "degC"),
    ]

    cache = {
        pid: {"value": None, "prevValue": None, "lastUpdate": 0, "unit": None}
        for pid, _, _ in sensor_readings
    }
    lock = Lock()

    # Step 1: Feed OBD responses through CacheCallback
    for pid, magnitude, units in sensor_readings:
        response = FakeResponse(pid, magnitude, units)
        CacheCallback(response, cache, lock)

    # Verify cache was populated correctly
    for pid, magnitude, units in sensor_readings:
        assert cache[pid]["value"] == magnitude, \
            f"CacheCallback: expected {pid} value {magnitude}, got {cache[pid]['value']}"
        assert cache[pid]["unit"] == units, \
            f"CacheCallback: expected {pid} unit '{units}', got {cache[pid]['unit']}"
        assert cache[pid]["lastUpdate"] > 0, \
            f"CacheCallback: expected {pid} lastUpdate to be set"

    # Step 2: Log cached data to CSV via TripLogger
    logger = TripLogger(log_dir=str(tmp_path))
    for pid, data in cache.items():
        logger.log(pid, data["value"], data["unit"])
    logger.close()

    # Verify CSV was written with correct values
    files = list(tmp_path.glob("trip_*.csv"))
    assert len(files) == 1, "TripLogger: expected exactly one CSV file"

    with open(files[0]) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == len(sensor_readings), \
        f"TripLogger: expected {len(sensor_readings)} rows, got {len(rows)}"

    logged_pids = {row["PID"]: row for row in rows}
    for pid, magnitude, units in sensor_readings:
        assert pid in logged_pids, \
            f"TripLogger: PID '{pid}' not found in CSV"
        assert logged_pids[pid]["Value"] == str(magnitude), \
            f"TripLogger: expected {pid} value '{magnitude}', got '{logged_pids[pid]['Value']}'"
        assert logged_pids[pid]["Unit"] == units, \
            f"TripLogger: expected {pid} unit '{units}', got '{logged_pids[pid]['Unit']}'"

    # Step 3: Publish cached data via PublishVehicleData
    fake_pub = FakePublisher()
    zmq_publisher = {"publisher": fake_pub, "enabled": True}

    PublishVehicleData(zmq_publisher, cache)

    # Verify a message was published
    assert len(fake_pub.messages) == 1, \
        "PublishVehicleData: expected exactly one ZMQ message to be sent"

    message = fake_pub.messages[0]
    assert message.startswith("VEHICLE_DATA"), \
        "PublishVehicleData: message should start with 'VEHICLE_DATA'"

    # Verify published JSON contains all PIDs with correct values
    payload = json.loads(message[len("VEHICLE_DATA "):])
    assert "data" in payload, "PublishVehicleData: published message missing 'data' field"

    for pid, magnitude, units in sensor_readings:
        assert pid in payload["data"], \
            f"PublishVehicleData: PID '{pid}' missing from published payload"
        assert payload["data"][pid]["value"] == magnitude, \
            f"PublishVehicleData: expected {pid} value {magnitude}, got {payload['data'][pid]['value']}"
        assert payload["data"][pid]["unit"] == units, \
            f"PublishVehicleData: expected {pid} unit '{units}', got {payload['data'][pid]['unit']}"
