#!/usr/bin/env bash
set -euo pipefail

INFLUXDB_DATABASE=${INFLUXDB_DATABASE:-ats_data}
INFLUXDB_USERNAME=${INFLUXDB_USERNAME:-admin}
INFLUXDB_PASSWORD=${INFLUXDB_PASSWORD:-admin123}

log() {
  echo "[entrypoint] $*"
}

ensure_dirs() {
  mkdir -p /var/lib/influxdb /var/log/influxdb /var/lib/mosquitto /var/log/mosquitto
  chown -R influxdb:influxdb /var/lib/influxdb /var/log/influxdb || true
  chown -R mosquitto:mosquitto /var/lib/mosquitto /var/log/mosquitto || true
}

ensure_binaries() {
  for bin in influxd influx mosquitto; do
    if ! command -v "$bin" >/dev/null 2>&1; then
      log "Thiếu binary bắt buộc: $bin"
      exit 1
    fi
  done
}

ensure_dirs
ensure_binaries

log "Khởi động InfluxDB"
runuser -u influxdb -- influxd >/var/log/influxd.log 2>&1 &
INFLUXD_PID=$!

cleanup() {
  if [[ -n "${MOSQUITTO_PID:-}" ]]; then
    log "Dừng Mosquitto (PID: ${MOSQUITTO_PID})"
    kill "${MOSQUITTO_PID}" 2>/dev/null || true
  fi
  if [[ -n "${INFLUXD_PID:-}" ]]; then
    log "Dừng InfluxDB (PID: ${INFLUXD_PID})"
    kill "${INFLUXD_PID}" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

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
runuser -u mosquitto -- mosquitto -c /etc/mosquitto/mosquitto.conf >/var/log/mosquitto.log 2>&1 &
MOSQUITTO_PID=$!

log "Chạy ứng dụng Python"
python src/app.py &
APP_PID=$!

wait "$APP_PID"
