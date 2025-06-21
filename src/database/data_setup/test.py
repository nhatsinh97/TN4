import json

link = "./database/data_setup/"
file = "data_setup.json"

# Đọc dữ liệu từ file JSON
with open(link + file, "r", encoding='utf-8') as fin:
    # Chuyển dữ liệu JSON từ file thành đối tượng Python
    data = json.load(fin)

# Dữ liệu từ API (đã ở dạng dictionary)
api_data = {"idchip": "181134ab4c24", "uv1": "on"}
api_value = api_data.get("idchip")  # Lấy giá trị "idchip" từ dữ liệu API

# Trích xuất phần dữ liệu cần so sánh
chipid_data = data.get('chipid', {})

# So sánh và lấy dữ liệu nếu giá trị từ API trùng khớp
def get_data_for_chipid(api_value, chipid_data):
    # Kiểm tra xem giá trị từ API có tồn tại trong dữ liệu không
    if api_value in chipid_data:
        # Nếu có, lấy toàn bộ giá trị của đối tượng đó
        return chipid_data[api_value]
    else:
        # Nếu không, trả về thông báo hoặc giá trị mặc định
        return None

# Thực hiện so sánh và lấy dữ liệu
result = get_data_for_chipid(api_value, chipid_data)

if result:
    print("Dữ liệu trùng khớp:", result)
else:
    print("Dữ liệu không trùng khớp hoặc không tìm thấy.")
