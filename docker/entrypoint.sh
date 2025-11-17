#!/usr/bin/env bash
set -euo pipefail

INFLUXDB_DATABASE=${INFLUXDB_DATABASE:-ats_data}
INFLUXDB_USERNAME=${INFLUXDB_USERNAME:-admin}
INFLUXDB_PASSWORD=${INFLUXDB_PASSWORD:-admin123}

log() {
  echo "[entrypoint] $*"
}

log "Khởi động InfluxDB"
influxd >/var/log/influxd.log 2>&1 &
INFLUXD_PID=$!

log "Chờ InfluxDB sẵn sàng..."
for i in {1..30}; do
  if curl -fs http://localhost:8086/ping >/dev/null 2>&1; then
    log "InfluxDB đã sẵn sàng."
    break
  fi
  sleep 1
done

if ! curl -fs http://localhost:8086/ping >/dev/null 2>&1; then
  log "InfluxDB không phản hồi, thoát."
  wait $INFLUXD_PID
  exit 1
fi

log "Khởi tạo cơ sở dữ liệu ${INFLUXDB_DATABASE} và người dùng ${INFLUXDB_USERNAME}."
# Lệnh có thể báo lỗi nếu đã tồn tại; bỏ qua để tránh dừng container.
influx -execute "CREATE DATABASE \"${INFLUXDB_DATABASE}\"" || true
influx -execute "CREATE USER \"${INFLUXDB_USERNAME}\" WITH PASSWORD '${INFLUXDB_PASSWORD}' WITH ALL PRIVILEGES" || true
influx -execute "GRANT ALL PRIVILEGES ON \"${INFLUXDB_DATABASE}\" TO \"${INFLUXDB_USERNAME}\"" || true

log "Khởi động Mosquitto"
mosquitto -c /etc/mosquitto/mosquitto.conf >/var/log/mosquitto.log 2>&1 &

log "Chạy ứng dụng Python"
exec python src/app.py
