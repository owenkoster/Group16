import csv
import time
import sys
import os

sys.path.append(os.path.abspath("src/main/resources/python"))
from OBDCommModule import PlaybackLog

class FakePublisher:

    def __init__(self):
        self.messages = []

    def send_string(self, msg):
        self.messages.append(msg)


def test_playback(tmp_path):

    file = tmp_path / "trip.csv"

    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp_Unix","PID","Value","Unit","DTC_Codes"])
        writer.writerow([time.time(), "RPM", "2000", "rpm", ""])

    fake_pub = {"publisher": FakePublisher(), "enabled": True}

    PlaybackLog(file, fake_pub)

    assert len(fake_pub["publisher"].messages) > 0