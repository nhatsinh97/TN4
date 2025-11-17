FROM python:3.9-slim

WORKDIR /app

# Cài đặt Mosquitto, InfluxDB và các tiện ích hỗ trợ
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends curl gnupg2 ca-certificates mosquitto; \
    . /etc/os-release; \
    echo "deb [signed-by=/etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg] https://repos.influxdata.com/debian ${VERSION_CODENAME} stable" > /etc/apt/sources.list.d/influxdata.list; \
    curl -fsSL https://repos.influxdata.com/influxdata-archive_compat.key | gpg --dearmor > /etc/apt/trusted.gpg.d/influxdata-archive_compat.gpg; \
    apt-get update; \
    apt-get install -y --no-install-recommends influxdb; \
    rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn và cấu hình
COPY src ./src
COPY database ./database
COPY docker/mosquitto.conf /etc/mosquitto/mosquitto.conf
COPY docker/entrypoint.sh ./docker/entrypoint.sh
RUN mkdir -p /var/lib/mosquitto /var/log/mosquitto

# Biến môi trường được truyền qua file .env ngoài container
# để tránh lưu thông tin nhạy cảm trực tiếp trong image.

EXPOSE 58888 1883 8086

ENTRYPOINT ["/app/docker/entrypoint.sh"]
