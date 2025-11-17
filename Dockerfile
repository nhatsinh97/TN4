FROM python:3.9-slim

WORKDIR /app

ARG INFLUXDB_VERSION=1.8.10

# Cài đặt Mosquitto, InfluxDB 1.8.10 (tải trực tiếp) và các tiện ích hỗ trợ
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl ca-certificates mosquitto util-linux; \
    curl -fsSL "https://dl.influxdata.com/influxdb/releases/influxdb_${INFLUXDB_VERSION}_amd64.deb" -o /tmp/influxdb.deb; \
    dpkg -i /tmp/influxdb.deb; \
    rm /tmp/influxdb.deb; \
    rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn và cấu hình
COPY src ./src
COPY database ./database
COPY docker/mosquitto.conf /etc/mosquitto/mosquitto.conf
COPY docker/entrypoint.sh ./docker/entrypoint.sh
RUN set -eux; \
    mkdir -p /var/lib/mosquitto /var/log/mosquitto /var/lib/influxdb /var/log/influxdb; \
    chown -R mosquitto:mosquitto /var/lib/mosquitto /var/log/mosquitto; \
    chown -R influxdb:influxdb /var/lib/influxdb /var/log/influxdb

# Biến môi trường được truyền qua file .env ngoài container
# để tránh lưu thông tin nhạy cảm trực tiếp trong image.

EXPOSE 58888 1883 8086

ENTRYPOINT ["/app/docker/entrypoint.sh"]
