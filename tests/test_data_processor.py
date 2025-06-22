import os
import json
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Stub external modules before importing module
sys.modules.setdefault('cv2', types.SimpleNamespace(VideoCapture=lambda *a, **k: None, imencode=lambda *a, **k: (True, b'')))
urllib3_stub = types.ModuleType('urllib3')
urllib3_stub.exceptions = types.SimpleNamespace(InsecureRequestWarning=Exception)
sys.modules.setdefault('urllib3', urllib3_stub)
sys.modules.setdefault('urllib3.exceptions', urllib3_stub.exceptions)
class RequestsStub(types.ModuleType):
    def __init__(self):
        super().__init__('requests')
        self.packages = types.SimpleNamespace(urllib3=types.SimpleNamespace(disable_warnings=lambda *a, **k: None))
    def post(self, *a, **k):
        pass

sys.modules.setdefault('requests', RequestsStub())

import data_processor

class DummyResponse:
    def __init__(self, status_code=200, text='OK'):
        self.status_code = status_code
        self.text = text

class DummyCap:
    def read(self):
        return True, 'frame'
    def release(self):
        pass


def setup_tmp_json(tmp_path):
    data = {
        "chipid": {
            "chip123": {
                "uv1": {
                    "mac_address": "AA:BB",
                    "camera": "0",
                    "timer": 5
                },
                "about": {"ip": "old", "version": "v1"}
            }
        }
    }
    path = tmp_path / "data_setup.json"
    path.write_text(json.dumps(data))
    return path

def test_process_data_success(monkeypatch, tmp_path):
    json_path = setup_tmp_json(tmp_path)
    monkeypatch.setattr(data_processor, "link", str(tmp_path) + "/")
    monkeypatch.setattr(data_processor, "file", "data_setup.json")
    monkeypatch.setattr(data_processor.cv2, "VideoCapture", lambda cam: DummyCap())
    monkeypatch.setattr(data_processor.cv2, "imencode", lambda ext, img: (True, b"img"))
    monkeypatch.setattr(data_processor.requests, "post", lambda *a, **kw: DummyResponse())

    data = {"idchip": "chip123", "name": "uv1", "status": "start", "ip": "1.2.3.4", "version": "v2"}
    result = data_processor.process_data(data)

    assert result == {"status_code": 200, "response_text": "OK"}
    updated = json.loads(json_path.read_text())
    assert updated["chipid"]["chip123"]["about"]["ip"] == "1.2.3.4"
    assert updated["chipid"]["chip123"]["about"]["version"] == "v2"

def test_process_data_invalid_id(monkeypatch, tmp_path):
    setup_tmp_json(tmp_path)
    monkeypatch.setattr(data_processor, "link", str(tmp_path) + "/")
    monkeypatch.setattr(data_processor, "file", "data_setup.json")

    data = {"idchip": "unknown", "name": "uv1", "status": "start", "ip": "1", "version": "v"}
    result = data_processor.process_data(data)
    assert result["status_code"] is None
    assert "ID chip" in result["error"]
