from datetime import datetime, timezone, timedelta
from influxdb import InfluxDBClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from a .env file if present
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

VN_TZ = timezone(timedelta(hours=7))  # Múi giờ Việt Nam

# Cùng bảng ánh xạ với ats_socket để đảm bảo ghi log đúng trường
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

def log_ats_data(data):
    try:
        client = InfluxDBClient(
            host=os.getenv("INFLUXDB_HOST"),
            port=int(os.getenv("INFLUXDB_PORT", 8086)),
            username=os.getenv("INFLUXDB_USERNAME"),
            password=os.getenv("INFLUXDB_PASSWORD"),
            database=os.getenv("INFLUXDB_DATABASE", "ats_data"),
        )
    except Exception as conn_err:
        print("❌ Không thể kết nối InfluxDB:", conn_err)
        return

    points = []
    for gen_key in ['gen1', 'gen2']:
        gen = data.get(gen_key)
        if not gen:
            continue

        # Chuyển đổi tên trường nếu dữ liệu vẫn dùng dạng r0, r1...
        gen = {FIELD_MAP.get(k, k): v for k, v in gen.items()}

        fields = {}
        ia = float(gen.get("ia", -1))
        ib = float(gen.get("ib", -1))
        ic = float(gen.get("ic", -1))
        freq = float(gen.get("freq1", -1))

        if ia != -1:
            fields["ia"] = ia
        if ib != -1:
            fields["ib"] = ib
        if ic != -1:
            fields["ic"] = ic
        if freq != -1:
            fields["freq"] = freq

        if fields:
            point = {
                "measurement": "ats_status",
                "tags": {
                    "generator": gen_key
                },
                "time": datetime.now(VN_TZ).isoformat(),
                "fields": fields
            }
            points.append(point)

    if points:
        try:
            client.write_points(points)
            print(f"✅ Đã ghi {len(points)} điểm vào InfluxDB.controllers")
        except Exception as e:
            print("❌ Lỗi khi ghi dữ liệu vào InfluxDB:", e)
