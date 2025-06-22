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
python TN4/app.py
```
Ứng dụng sẽ khởi động tại địa chỉ `http://localhost:58888` ở chế độ mặc định.

### Cấu hình đường dẫn cơ sở

Ứng dụng lấy đường dẫn tới thư mục dữ liệu dựa trên biến môi trường
`TN4_BASE_DIR`. Nếu biến này không được thiết lập, ứng dụng sẽ mặc định sử
dụng thư mục chứa tệp `app.py`.

Ví dụ:

```bash
export TN4_BASE_DIR=/opt/tn4/src
python TN4/app.py
```

### Cấu hình `SECRET_KEY`

Biến môi trường `SECRET_KEY` dùng để thiết lập khóa phiên cho ứng dụng.
Nếu biến này không được khai báo, ứng dụng sẽ tự tạo một khóa ngẫu nhiên
mỗi lần khởi động.

Ví dụ:

```bash
export SECRET_KEY=mysecretkey
python TN4/app.py
```

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
