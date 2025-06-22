# ats_socket.py
import json
import os
import paho.mqtt.client as mqtt
from threading import Thread
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import time
from datetime import datetime
from application.controllers.ats_logger import log_ats_data

# Mapping từ các khóa dữ liệu nhận được sang id trong giao diện ATS
FIELD_MAP = {
    'r0': 'uab1',
    'r1': 'ubc1',
    'r2': 'uca1',
    'r3': 'ua1',
    'r4': 'ub1',
    'r5': 'uc1',
    'r6': 'phaA1',
    'r7': 'phaB1',
    'r8': 'phaC1',
    'r9': 'freq1',
    'r10': 'uab2',
    'r11': 'ubc2',
    'r12': 'uca2',
    'r13': 'ua2',
    'r14': 'ub2',
    'r15': 'uc2',
    'r16': 'phaA2',
    'r17': 'phaB2',
    'r18': 'phaC2',
    'r19': 'freq2',
    'r20': 'ia',
    'r21': 'ib',
    'r22': 'ic',
    'r23': 'status_close_a',
    'r24': 'status_close_b',
    'r25': 'status_open',
    'r26': 'auto_mode'
}

def map_generator_fields(gen_data: dict) -> dict:
    """Convert raw generator data using FIELD_MAP."""
    return {FIELD_MAP.get(k, k): v for k, v in gen_data.items()}


# Khởi tạo biến socketio, sẽ được truyền từ file chính (app.py)
socketio = None

# Cấu hình MQTT
# Broker và cổng có thể cấu hình qua biến môi trường
MQTT_BROKER = os.getenv("MQTT_BROKER_ADDRESS_ATS", "localhost")  # hoặc IP như "10.50.41.15"
MQTT_PORT = int(os.getenv("MQTT_PORT_ATS", 1883))
MQTT_TOPIC = "ats/data"

# Hàm callback khi nhận dữ liệu từ MQTT
def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"[MQTT] Nhận từ {topic}: {data}")

        if topic == "ats/data":
            # Chuyển đổi tên trường theo bảng ánh xạ
            mapped = {}
            for gen_key in ["gen1", "gen2"]:
                if gen_key in data:
                    mapped[gen_key] = map_generator_fields(data[gen_key])

            # 🔴 Ghi dữ liệu điện năng vào InfluxDB
            log_ats_data(mapped)

            # Gửi dữ liệu đến client qua Socket.IO
            if socketio:
                print("[SOCKET.IO] Gửi dữ liệu ATS qua Socket.IO")
                socketio.emit("ats_data", mapped)

        elif topic == "ats/water":
            # 👉 Gửi dữ liệu nước tới frontend
            if socketio is not None:
                print("[SOCKET.IO] Gửi dữ liệu NƯỚC:", data)
                socketio.emit("water_data", data)
            else:
                print("⚠️ socketio chưa sẵn sàng, bỏ qua gửi dữ liệu nước")


    except Exception as e:
        print("[MQTT] Lỗi:", e)

def read_real_from_offset(client, offset_byte):
    address = offset_byte // 2
    result = client.read_holding_registers(address, 2, unit=1)
    if not result.isError():
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.Big, wordorder=Endian.Big)
        return decoder.decode_32bit_float()
    else:
        print(f"❌ Lỗi đọc tại offset {offset_byte}")
        return None

def read_modbus_water_loop():
    global socketio  # ✅ THÊM DÒNG NÀY
    # Địa chỉ PLC nước được cấu hình qua biến môi trường
    water_ip = os.getenv("PLC_WATER_IP", "10.16.40.160")
    client = ModbusTcpClient(water_ip, port=502)
    variables = {
        "DifferentialTotalFlow": 0,
        "ReverseTotalFlow": 4,
        "ForwardFlow": 8,
        "Flow": 16,
        "FlowRate": 20,
    }

    if client.connect():
        print("✅ Kết nối PLC nước thành công")
        try:
            while True:
                data = {"timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                for name, offset in variables.items():
                    try:
                        value = read_real_from_offset(client, offset)
                        data[name] = round(value, 1) if value is not None else None
                    except Exception as e:
                        print(f"[MODBUS] Lỗi đọc {name}:", e)
                        data[name] = None


                print("[MODBUS] Dữ liệu nước:", data)
                if socketio:
                    socketio.emit("water_data", data)

                time.sleep(5)
        except Exception as e:
            print("🛑 Lỗi luồng đọc PLC:", e)
        finally:
            client.close()
    else:
        print("❌ Không thể kết nối đến PLC nước")

def start_ats_socketio_listener(socketio_instance):
    global socketio, mqtt_client
    socketio = socketio_instance

    mqtt_client = mqtt.Client()
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe("ats/data")
    mqtt_client.subscribe("ats/water")  # 👈 Thêm dòng này
    socketio.sleep(0)  # Giúp Socket.IO không bị nghẽn khi dùng eventlet/gevent
    thread = Thread(target=mqtt_client.loop_forever)
    thread.daemon = True
    thread.start()
    # 👉 Bắt đầu luồng đọc dữ liệu nước từ PLC (Modbus TCP)
    water_thread = Thread(target=read_modbus_water_loop)
    water_thread.daemon = True
    water_thread.start()

