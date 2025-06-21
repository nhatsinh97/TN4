# ats_socket.py
import json
import paho.mqtt.client as mqtt
from threading import Thread
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import time
from datetime import datetime
from application.controllers.ats_logger import log_ats_data


# Khởi tạo biến socketio, sẽ được truyền từ file chính (app.py)
socketio = None

# Cấu hình MQTT
MQTT_BROKER = "localhost"  # hoặc IP như "10.50.41.15"
MQTT_PORT = 1883
MQTT_TOPIC = "ats/data"

# Hàm callback khi nhận dữ liệu từ MQTT
def on_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"[MQTT] Nhận từ {topic}: {data}")

        if topic == "ats/data":
            # 🔴 Ghi dữ liệu điện năng vào InfluxDB
            log_ats_data(data)

            # Gửi dữ liệu đến client qua Socket.IO
            if socketio:
                print("[SOCKET.IO] Gửi dữ liệu ATS qua Socket.IO")
                socketio.emit("ats_data", data)

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
    client = ModbusTcpClient('10.16.40.160', port=502)
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

