import sys
import os

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import PublishVehicleData

class FakePublisher:

    def __init__(self):
        self.message = None

    def send_string(self, msg):
        self.message = msg


def test_publish_vehicle_data():

    fake_pub = FakePublisher()

    zmq_pub = {
        "publisher": fake_pub,
        "enabled": True
    }

    cache = {
        "RPM": {
            "value": 1500,
            "unit": "rpm",
            "lastUpdate": 123
        },
        "MAF": {
            "value": "None",
            "unit": "None",
            "lastUpdate": 12345
        }
    }

    PublishVehicleData(zmq_pub, cache)

    assert fake_pub.message is not None
    assert "VEHICLE_DATA" in fake_pub.message
    assert "RPM" in fake_pub.message