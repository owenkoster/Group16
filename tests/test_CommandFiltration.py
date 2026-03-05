import sys
import os

sys.path.append(os.path.abspath("src/main/resources/python"))

from OBDCommModule import FilterCommands

def test_filter_commands():

    commands = {
        "RPM": {"category": "telemetry"},
        "VIN": {"category": "on_demand"},
        "GET_DTC": {"category": "internal"}
    }

    filters = ["telemetry", "internal"]

    result = FilterCommands(commands, filters)

    assert "RPM" in result
    assert "GET_DTC" in result
    assert "VIN" not in result