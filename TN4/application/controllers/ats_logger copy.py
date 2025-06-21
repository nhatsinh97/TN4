from datetime import datetime, timezone, timedelta
from influxdb import InfluxDBClient

client = InfluxDBClient(host='localhost', port=8086, username='cico', password='2020@GreenFeed')
client.switch_database('ats_data')

VN_TZ = timezone(timedelta(hours=7))  # Múi giờ Việt Nam

def log_ats_data(data):
    points = []
    for gen_key in ['gen1', 'gen2']:
        gen = data.get(gen_key)
        if not gen:
            continue

        point = {
            "measurement": "ats_status",
            "tags": {
                "generator": gen_key
            },
            "time": datetime.now(VN_TZ).isoformat(),  # ✅ Dùng giờ Việt Nam ISO 8601
            "fields": {
                "ia": float(gen.get("ia", 0)),
                "ib": float(gen.get("ib", 0)),
                "ic": float(gen.get("ic", 0)),
                "freq": float(gen.get("freq1", 0))
            }
        }
        points.append(point)

    if points:
        client.write_points(points)
