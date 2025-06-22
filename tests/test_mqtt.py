import os
import sys
import json
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Stub paho.mqtt.client before import
class DummyClient:
    def __init__(self, *a, **k):
        self.on_message = None
    def connect(self, *a, **k):
        pass
    def subscribe(self, *a, **k):
        pass
    def loop_forever(self):
        pass

mqtt_stub = types.SimpleNamespace(Client=DummyClient, MQTTv311=0)
sys.modules.setdefault('paho', types.ModuleType('paho'))
sys.modules.setdefault('paho.mqtt', types.ModuleType('paho.mqtt'))
sys.modules.setdefault('paho.mqtt.client', mqtt_stub)

import mqtt

class DummyMessage:
    def __init__(self, payload):
        self.payload = payload


def test_on_message_prints(capsys):
    data = {
        "state": {
            "reported": {
                "P1": {"desc": "d1", "value": [1]},
                "P2": {"desc": "d2", "value": [2]},
                "$logotime": "now"
            }
        }
    }
    msg = DummyMessage(json.dumps(data).encode())
    mqtt.on_message(None, None, msg)
    captured = capsys.readouterr()
    assert "P1 - d1: 1" in captured.out
    assert "P2 - d2: 2" in captured.out
    assert "Logotime: now" in captured.out
