import sys
import os
import csv
import json
from threading import Lock
from unittest.mock import patch

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import (
    CacheCallback,
    TripLogger,
    PublishVehicleData,
    PlaybackLog,
)

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

# Helpers

SENSOR_READINGS = [
    ("RPM",          3000, "rpm"),
    ("SPEED",        80,   "kph"),
    ("COOLANT_TEMP", 92,   "degC"),
]

def run_system_test(tmp_path, platform_name):
    """
    Runs the full system test pipeline for a given simulated platform.
    Tests CacheCallback -> TripLogger -> PublishVehicleData -> PlaybackLog.
    """

    # Step 1: CacheCallback populates the shared cache
    cache = {
        pid: {"value": None, "prevValue": None, "lastUpdate": 0, "unit": None}
        for pid, _, _ in SENSOR_READINGS
    }
    lock = Lock()

    for pid, magnitude, units in SENSOR_READINGS:
        CacheCallback(FakeResponse(pid, magnitude, units), cache, lock)

    for pid, magnitude, units in SENSOR_READINGS:
        assert cache[pid]["value"] == magnitude, \
            f"[{platform_name}] CacheCallback: wrong value for {pid}"
        assert cache[pid]["unit"] == units, \
            f"[{platform_name}] CacheCallback: wrong unit for {pid}"

    # Step 2: TripLogger writes the cache to CSV
    log_dir = os.path.join(str(tmp_path), platform_name.lower(), "logs")
    logger = TripLogger(log_dir=log_dir)
    for pid, data in cache.items():
        logger.log(pid, data["value"], data["unit"])
    logger.close()

    # Verify log directory and file were created using OS-appropriate paths
    assert os.path.isdir(log_dir), \
        f"[{platform_name}] TripLogger: log directory not created at '{log_dir}'"

    files = list(f for f in os.listdir(log_dir) if f.endswith(".csv"))
    assert len(files) == 1, \
        f"[{platform_name}] TripLogger: expected 1 CSV file, found {len(files)}"

    log_filepath = os.path.join(log_dir, files[0])

    # Verify path separator is handled correctly for the platform
    assert os.sep in log_filepath, \
        f"[{platform_name}] TripLogger: file path does not use correct OS separator"

    with open(log_filepath) as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == len(SENSOR_READINGS), \
        f"[{platform_name}] TripLogger: expected {len(SENSOR_READINGS)} rows, got {len(rows)}"

    for pid, magnitude, units in SENSOR_READINGS:
        match = next((r for r in rows if r["PID"] == pid), None)
        assert match is not None, \
            f"[{platform_name}] TripLogger: PID '{pid}' missing from CSV"
        assert match["Value"] == str(magnitude), \
            f"[{platform_name}] TripLogger: wrong value for {pid}"
        assert match["Unit"] == units, \
            f"[{platform_name}] TripLogger: wrong unit for {pid}"

    # Step 3: PublishVehicleData publishes the cache
    fake_pub = FakePublisher()
    zmq_publisher = {"publisher": fake_pub, "enabled": True}
    PublishVehicleData(zmq_publisher, cache)

    assert len(fake_pub.messages) == 1, \
        f"[{platform_name}] PublishVehicleData: expected 1 message, got {len(fake_pub.messages)}"

    payload = json.loads(fake_pub.messages[0][len("VEHICLE_DATA "):])
    for pid, magnitude, units in SENSOR_READINGS:
        assert pid in payload["data"], \
            f"[{platform_name}] PublishVehicleData: '{pid}' missing from payload"
        assert payload["data"][pid]["value"] == magnitude, \
            f"[{platform_name}] PublishVehicleData: wrong value for {pid}"

    # Step 4: PlaybackLog replays the CSV and publishes correctly
    playback_pub = FakePublisher()
    playback_zmq = {"publisher": playback_pub, "enabled": True}

    # Patch time.sleep so playback runs instantly in CI
    with patch("time.sleep", return_value=None):
        PlaybackLog(log_filepath, playback_zmq)

    assert len(playback_pub.messages) > 0, \
        f"[{platform_name}] PlaybackLog: no messages published during playback"

    for pid, _, _ in SENSOR_READINGS:
        assert any(pid in msg for msg in playback_pub.messages), \
            f"[{platform_name}] PlaybackLog: PID '{pid}' never appeared in playback output"

# System tests — one per simulated platform

def test_system_windows(tmp_path):
    """System test simulating a Windows environment (win32 platform)."""
    with patch("sys.platform", "win32"):
        run_system_test(tmp_path, "Windows")


def test_system_macos(tmp_path):
    """System test simulating a macOS environment (darwin platform)."""
    with patch("sys.platform", "darwin"):
        run_system_test(tmp_path, "macOS")
