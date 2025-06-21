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

## Cấu trúc thư mục chính

```
src/        # mã nguồn của ứng dụng
templates/  # các tệp giao diện HTML
static/     # tài nguyên tĩnh như CSS, JS, hình ảnh
database/   # file cấu hình và dữ liệu mẫu
```