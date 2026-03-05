import sys
import os

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import CacheCallback
from threading import Lock

class FakeValue:
    magnitude = 3000
    units = "rpm"

class FakeCommand:
    name = "RPM"

class FakeResponse:

    command = FakeCommand()
    value = FakeValue()

    def is_null(self):
        return False


def test_cache_callback_validation():

    cache = {
        "RPM": {
            "value": None,
            "prevValue": None,
            "lastUpdate": 0,
            "unit": None
        }
    }

    CacheCallback(FakeResponse(), cache, Lock())

    assert cache["RPM"]["value"] == 3000
    assert cache["RPM"]["unit"] == "rpm"
    assert cache["RPM"]["lastUpdate"] > 0