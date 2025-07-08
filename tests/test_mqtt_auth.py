from tests import test_utils  # noqa: F401 - set up stubs and env vars
import app

class DummyMQTT:
    def __init__(self):
        self.username_pw = None
        self.connected = False
    def username_pw_set(self, username, password):
        self.username_pw = (username, password)
    def connect(self, *a, **k):
        self.connected = True
    def reconnect_delay_set(self, *a, **k):
        pass
    def loop_forever(self):
        pass

def test_start_mqtt_loop_uses_credentials(monkeypatch):
    dummy = DummyMQTT()
    monkeypatch.setattr(app, "mqtt_client", dummy)
    monkeypatch.setattr(app, "MQTT_USERNAME", "user")
    monkeypatch.setattr(app, "MQTT_PASSWORD", "pass")
    app.start_mqtt_loop()
    assert dummy.username_pw == ("user", "pass")
