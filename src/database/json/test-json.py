import json
link = "./database/json/"
file = "GF_TN4.json"
# Chuỗi JSON ban đầu (đã là đối tượng dict)
with open(link + file, "r", encoding='utf-8') as fin:
        # Chuyển chuỗi JSON thành đối tượng Python
        json_string = json.load(fin)
# Cập nhật giá trị

json_string['GF_TN4']['reset'] = '1'  # Ví dụ: thay đổi chip thành ESP33
# json_string['GF_TN4_2']['about']['chip'] = 'ESP33'
# # Chuyển đối tượng dictionary thành chuỗi JSON
# updated_json_string = json.dumps(json_string, indent=4)

# Lưu đối tượng dictionary thành file JSON
with open(link + file , 'w', encoding='utf-8') as fout:
    json.dump(json_string, fout, ensure_ascii=False, indent=4)
    print('Đã lưu file')
