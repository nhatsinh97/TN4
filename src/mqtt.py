import json
import paho.mqtt.client as mqtt

# Thông tin MQTT
BROKER_ADDRESS = "172.17.128.24"
PORT = 1883
TOPIC = "PLC/LOGO"

# Hàm callback khi nhận được tin nhắn từ MQTT
def on_message(client, userdata, message):
    try:
        # Chuyển dữ liệu JSON từ chuỗi thành từ điển Python
        data = json.loads(message.payload.decode())
        
        # Trích xuất các giá trị từ dữ liệu
        reported = data.get("state", {}).get("reported", {})
        
        P1_desc = reported.get("P1", {}).get("desc", "N/A")
        P1_value = reported.get("P1", {}).get("value", [])[0] if reported.get("P1", {}).get("value") else None
        
        P2_desc = reported.get("P2", {}).get("desc", "N/A")
        P2_value = reported.get("P2", {}).get("value", [])[0] if reported.get("P2", {}).get("value") else None

        logotime = reported.get("$logotime", "N/A")
        
        # In ra dữ liệu để kiểm tra
        print(f"P1 - {P1_desc}: {P1_value}")
        print(f"P2 - {P2_desc}: {P2_value}")
        print(f"Logotime: {logotime}")
        print("-" * 30)
        
    except json.JSONDecodeError:
        print("Lỗi giải mã JSON.")

# Thiết lập MQTT client
client = mqtt.Client("PC")
client.on_message = on_message

# Kết nối đến broker và đăng ký chủ đề
client.connect(BROKER_ADDRESS, PORT)
client.subscribe(TOPIC)

# Bắt đầu vòng lặp để nhận tin nhắn
client.loop_forever()
