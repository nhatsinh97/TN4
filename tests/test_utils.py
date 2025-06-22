import os
import sys
import json
import socket
import types
import codecs

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Stub external modules before importing app
sys.modules.setdefault('eventlet', types.SimpleNamespace(monkey_patch=lambda: None))
cv2_stub = types.SimpleNamespace(VideoCapture=lambda *a, **k: None, imencode=lambda *a, **k: (True, b''))
sys.modules.setdefault('cv2', cv2_stub)
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
flask_stub = types.SimpleNamespace(Flask=lambda *a, **k: types.SimpleNamespace(), make_response=lambda *a, **k: None,
                                    render_template=lambda *a, **k: None, redirect=lambda *a, **k: None,
                                    send_from_directory=lambda *a, **k: None, url_for=lambda *a, **k: '',
                                    request=None, session=None, flash=lambda *a, **k: None,
                                    send_file=lambda *a, **k: None, jsonify=lambda *a, **k: None)
sys.modules.setdefault('flask', flask_stub)
sys.modules.setdefault('flask_socketio', types.SimpleNamespace(SocketIO=lambda *a, **k: types.SimpleNamespace(on=lambda *a, **k: lambda f: f, emit=lambda *a, **k: None)))
sys.modules.setdefault('influxdb', types.SimpleNamespace(InfluxDBClient=lambda *a, **k: None))
sys.modules.setdefault('ats_socket', types.SimpleNamespace(start_ats_socketio_listener=lambda *a, **k: None))
sys.modules.setdefault('dotenv', types.SimpleNamespace(load_dotenv=lambda *a, **k: None))
urllib3_stub = types.ModuleType('urllib3')
urllib3_stub.exceptions = types.SimpleNamespace(InsecureRequestWarning=Exception)
sys.modules.setdefault('urllib3', urllib3_stub)
sys.modules.setdefault('urllib3.exceptions', urllib3_stub.exceptions)
sys.modules.setdefault('werkzeug', types.ModuleType('werkzeug'))
sys.modules.setdefault('werkzeug.utils', types.SimpleNamespace(secure_filename=lambda *a, **k: ""))
class RequestsStub(types.ModuleType):
    def __init__(self):
        super().__init__('requests')
        self.packages = types.SimpleNamespace(urllib3=types.SimpleNamespace(disable_warnings=lambda *a, **k: None))

sys.modules.setdefault('requests', RequestsStub())
sys.modules.setdefault('application', types.ModuleType('application'))
sys.modules.setdefault('application.controllers', types.ModuleType('application.controllers'))
sys.modules.setdefault('application.controllers.ats_logger', types.SimpleNamespace(log_ats_data=lambda *a, **k: None))
sys.modules.setdefault('dateutil', types.ModuleType('dateutil'))
sys.modules.setdefault('dateutil.parser', types.SimpleNamespace())

# Provide required environment variables
os.environ.setdefault('INFLUXDB_PORT', '8086')
os.environ.setdefault('MQTT_PORT', '1883')
os.environ.setdefault('MQTT_BROKER_ADDRESS', 'localhost')
os.environ.setdefault('MQTT_TOPIC', 'test')
os.environ.setdefault('SECRET_KEY', 'secret')

# Patch codecs.getwriter to avoid stdout replacement
codecs.getwriter = lambda encoding: (lambda stream: stream)
if hasattr(sys.stdout, "detach"):
    sys.stdout.detach = lambda: sys.stdout

import ast
import types

def load_app_utils():
    mod = types.ModuleType('app_utils')
    ns = mod.__dict__
    src_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'app.py')
    with open(src_path) as f:
        source = f.read()
    tree = ast.parse(source)
    ns['Path'] = __import__('pathlib').Path
    ns['os'] = os
    ns['BASE_DIR'] = __import__('pathlib').Path(os.path.join(os.path.dirname(src_path)))
    ns['socket'] = socket
    ns['json'] = json
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if getattr(target, 'id', '') == 'DATA_FILE':
                    exec(compile(ast.Module([node], []), 'app', 'exec'), ns)
        elif isinstance(node, ast.FunctionDef) and node.name in ('ping_device', 'count_online_offline_devices'):
            exec(compile(ast.Module([node], []), 'app', 'exec'), ns)
    sys.modules['app_utils'] = mod
    return mod

app_utils = load_app_utils()
ping_device = app_utils.ping_device
count_online_offline_devices = app_utils.count_online_offline_devices

class DummySocket:
    def close(self):
        pass


def test_ping_device_online(monkeypatch):
    monkeypatch.setattr(socket, 'create_connection', lambda *a, **kw: DummySocket())
    assert ping_device('1.1.1.1') is True

def test_ping_device_offline(monkeypatch):
    def raise_timeout(*a, **kw):
        raise socket.timeout
    monkeypatch.setattr(socket, 'create_connection', raise_timeout)
    assert ping_device('1.1.1.1') is False

def test_count_online_offline_devices(monkeypatch, tmp_path):
    data = {
        "chipid": {
            "c1": {"about": {"ip": "1"}},
            "c2": {"about": {"ip": "2"}}
        }
    }
    file_path = tmp_path / 'data_setup.json'
    file_path.write_text(json.dumps(data))
    monkeypatch.setattr(sys.modules[ping_device.__module__], 'DATA_FILE', str(file_path))
    monkeypatch.setattr(sys.modules[ping_device.__module__], 'ping_device', lambda ip: ip == '1')
    online, offline = count_online_offline_devices()
    assert online == 1
    assert offline == 1
