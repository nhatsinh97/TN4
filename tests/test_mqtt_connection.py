import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import stubs and env vars
from tests import test_utils  # noqa: F401

import app

class DummyClient:
    def __init__(self):
        self.subscribed = []
    def subscribe(self, topic):
        self.subscribed.append(topic)


def test_on_connect_logs_once(caplog):
    client = DummyClient()
    caplog.set_level(logging.INFO)

    app.mqtt_connected = False
    app.on_connect(client, None, None, 0)
    app.on_connect(client, None, None, 0)

    logs = [r.message for r in caplog.records if "Đã kết nối" in r.message]
    assert len(logs) == 1

    app.on_disconnect(client, None, 1)
    assert app.mqtt_connected is False

    caplog.clear()
    app.on_connect(client, None, None, 0)
    logs = [r.message for r in caplog.records if "Đã kết nối" in r.message]
    assert len(logs) == 1
