from datetime import datetime, timezone, timedelta
from influxdb import InfluxDBClient

VN_TZ = timezone(timedelta(hours=7))  # Múi giờ Việt Nam

def log_ats_data(data):
    try:
        client = InfluxDBClient(host='localhost', port=8086)
        client.switch_database('ats_data')
    except Exception as conn_err:
        print("❌ Không thể kết nối InfluxDB:", conn_err)
        return

    points = []
    for gen_key in ['gen1', 'gen2']:
        gen = data.get(gen_key)
        if not gen:
            continue

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
