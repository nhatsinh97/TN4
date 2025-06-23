# TN4

Dự án **TN4** được phát triển nhằm thu thập và xử lý dữ liệu IoT thông qua ứng dụng web. Mục tiêu chính là cung cấp giao diện giám sát và quản lý thiết bị một cách thuận tiện.

## Thiết lập môi trường

1. Tạo môi trường ảo:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

## Chạy ứng dụng

Kích hoạt môi trường ảo (nếu chưa), sau đó chạy:
```bash
python src/app.py
```
Ứng dụng sẽ khởi động tại địa chỉ `http://localhost:58888` ở chế độ mặc định.

### Cấu hình đường dẫn cơ sở

Ứng dụng lấy đường dẫn tới thư mục dữ liệu dựa trên biến môi trường
`TN4_BASE_DIR`. Nếu biến này không được thiết lập, ứng dụng sẽ mặc định sử
dụng thư mục chứa tệp `app.py`.

Ví dụ:

```bash
export TN4_BASE_DIR=/opt/tn4/src
python src/app.py
```

### Cấu hình `SECRET_KEY`

Biến môi trường `SECRET_KEY` dùng để thiết lập khóa phiên cho ứng dụng.
Nếu biến này không được khai báo, ứng dụng sẽ tự tạo một khóa ngẫu nhiên
mỗi lần khởi động.

Ví dụ:

```bash
export SECRET_KEY=mysecretkey
python src/app.py
```

### Tạo file `.env`

Sao chép `src/.env.example` thành `src/.env` và thay đổi các giá trị phù hợp.
Tệp mẫu chứa các biến môi trường cần thiết, ví dụ:

```ini
SECRET_KEY=your-secret
INFLUXDB_HOST=127.0.0.1
INFLUXDB_PORT=8086
INFLUXDB_USERNAME={USER}
INFLUXDB_PASSWORD={PASS}
MQTT_BROKER_ADDRESS=127.0.0.1
MQTT_PORT=1883
MQTT_TOPIC=tn4/data
MQTT_BROKER_ADDRESS_ATS=127.0.0.1
MQTT_PORT_ATS=1883
USER_FILE=./database/data_setup/users.json
# ...các biến khác...
```

Các giá trị thật (như tên đăng nhập và mật khẩu) nên được thiết lập qua biến
môi trường hoặc tệp cấu hình nằm ngoài Git. Ví dụ khi chạy Docker:

```bash
docker run --env-file src/.env tn4-app
```

Bạn cần đảm bảo một MQTT broker đang chạy và có thể truy cập tại các địa chỉ trên trước khi khởi động container.

Tệp này chỉ dùng cho môi trường cục bộ và đã được bỏ qua khỏi kho mã nguồn.

### Tệp người dùng

File `src/database/data_setup/users.json` trong repository chỉ chứa các giá trị
giả ở trường `username` và `password`. Hãy tạo một bản sao bên ngoài Git và đặt
đường dẫn của file thật qua biến môi trường `USER_FILE` (khai báo trong `.env`).

### Chạy bằng Docker

Bạn có thể chạy ứng dụng mà không cần cài đặt Python thủ công bằng cách sử dụng Docker:

```bash
docker build -t tn4-app .
docker run -p 58888:58888 --env-file src/.env tn4-app
sudo docker run -d --restart unless-stopped \
  -p 58888:58888 \
  --env-file /home/jetson/project/TN4/src/.env \
  --name tn4 tn4-app

```
Hình ảnh Docker đã bao gồm thư viện **OpenCV** thông qua gói
`opencv-python-headless`, vì vậy bạn không cần cài đặt thủ công.

## Cấu trúc thư mục chính

```
src/        # mã nguồn của ứng dụng (thư mục TN4 hiện tại)
templates/  # các tệp giao diện HTML
static/     # tài nguyên tĩnh như CSS, JS, hình ảnh
database/   # file cấu hình và dữ liệu mẫu
```

## Quản lý thư viện

Các thư viện phục vụ giao diện (ví dụ Bootstrap, Chart.js...) hiện có trong
`src/static/dashboard/vendors/`. Để giảm kích thước repository, nên cân nhắc sử
dụng CDN hoặc cài đặt thông qua trình quản lý gói (npm, yarn...) thay vì commit
trực tiếp vào kho mã nguồn.
## Kiểm thử

Các bài test nằm trong thư mục `tests/`. Cài đặt `pytest` nếu muốn chạy kiểm thử:

```bash
pip install pytest
```

Sau đó chạy:

```bash
pytest
```

Các script thử nghiệm cũ đã được di chuyển vào thư mục `scripts/` để tránh ảnh hưởng tới quá trình thu thập test.

## Giấy phép

Dự án được phát hành theo giấy phép MIT. Xem tệp [LICENSE](LICENSE) để biết thêm chi tiết.
