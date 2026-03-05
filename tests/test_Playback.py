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
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    fake_pub = {"publisher": FakePublisher(), "enabled": True}

    for file in os.listdir(data_dir):
        if not file.endswith(".csv"):
            continue
        log_file = os.path.join(data_dir, file)
        # ---- Extract expected PIDs from CSV ----
        expected_pids = set()

        with open(log_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                expected_pids.add(row["PID"])

        # ---- Run playback ----
        PlaybackLog(log_file, fake_pub)

        messages = fake_pub["publisher"].messages

        assert len(messages) > 0

        # ---- Verify each PID appears in output ----
        for pid in expected_pids:
            assert any(pid in msg for msg in messages)
