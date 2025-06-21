# influx_config.py
from influxdb import InfluxDBClient

client = InfluxDBClient(
    host='localhost',
    port=8086,
    # username='',   # nếu không đặt auth thì để trống
    # password='',   # nếu không đặt auth thì để trống
    database='ats_data'
)
