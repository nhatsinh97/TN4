# influx_config.py
from influxdb import InfluxDBClient
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

client = InfluxDBClient(
    host=os.getenv("INFLUXDB_HOST"),
    port=int(os.getenv("INFLUXDB_PORT", 8086)),
    username=os.getenv("INFLUXDB_USERNAME"),
    password=os.getenv("INFLUXDB_PASSWORD"),
    database=os.getenv("INFLUXDB_DATABASE", "ats_data"),
)
