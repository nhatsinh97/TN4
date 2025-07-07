import os
import sys
import types
from datetime import datetime

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test_utils for stubs and env vars
from tests import test_utils  # noqa: F401

# Ensure the Flask stub provides context_processor
def make_flask(*a, **k):
    class DummyFlask(types.SimpleNamespace):
        def route(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

        def context_processor(self, func=None):
            def decorator(f):
                return f
            return decorator(func) if func else decorator
    return DummyFlask()

test_utils.sys.modules['flask'].Flask = make_flask
test_utils.sys.modules['requests'].post = lambda *a, **k: None

import app

class DummyResult:
    def __init__(self):
        self._points = [{"time": "2024-01-01T00:00:00Z", "ia": 1, "ib": 2, "ic": 3}]
    def get_points(self):
        return self._points

class DummyClient:
    def __init__(self):
        self.queries = []
    def query(self, q):
        self.queries.append(q)
        return DummyResult()


def test_get_history_start_end(monkeypatch):
    dummy = DummyClient()
    monkeypatch.setattr(app, 'InfluxDBClient', lambda *a, **k: dummy)
    monkeypatch.setattr(app, 'parser', types.SimpleNamespace(parse=lambda s: datetime.fromisoformat(s)))
    monkeypatch.setattr(app, 'jsonify', lambda x: x)
    app.request = types.SimpleNamespace(args={
        'start': '2024-01-01T07:00',
        'end': '2024-01-01T08:00'
    })
    result = app.get_ats_history(1)
    assert dummy.queries
    q = dummy.queries[0]
    assert 'time >=' in q and 'time <=' in q
    assert result[0]['ia'] == 1
    assert result[0]['time'].endswith('+07:00')


def test_get_history_range(monkeypatch):
    dummy = DummyClient()
    monkeypatch.setattr(app, 'InfluxDBClient', lambda *a, **k: dummy)
    monkeypatch.setattr(app, 'parser', types.SimpleNamespace(parse=lambda s: datetime.fromisoformat(s)))
    monkeypatch.setattr(app, 'jsonify', lambda x: x)
    app.request = types.SimpleNamespace(args={'range': '15m'})
    result = app.get_ats_history(1)
    assert dummy.queries
    q = dummy.queries[0]
    assert 'time >=' in q and 'time <=' in q
    assert result[0]['ia'] == 1
