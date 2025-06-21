import logging
import cv2
import json
import threading
from urllib3.exceptions import *
import requests
import base64
# from app import logger, uv_data
# Tắt cảnh báo liên quan đến SSL
# http = urllib3.PoolManager()
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# API chính
url        = 'http://10.50.41.18:58185/api/Farm/postbiohistory' 
url_cico   = 'https://10.50.41.18:58187/api/Farm/postbiohistory'
link = "./database/data_setup/"
file = "data_setup.json"



def process_data(data):
    logger = logging.getLogger('cico_log')

    # Danh sách các chipid không cần cập nhật
    excluded_chipids = {"PLC_LOGO_1","ESP32"} 

    # Chuyển đổi từ điển thành chuỗi JSON
    api_data = json.dumps(data, ensure_ascii=False, indent=4)

    # Đọc dữ liệu từ file JSON
    with open(link + file, "r", encoding='utf-8') as fin:
        data_json = json.load(fin)

    # Chuyển chuỗi JSON thành từ điển
    data_dict = json.loads(api_data)
    api_value = data_dict.get("idchip")
    name = data_dict.get("name")
    status = data_dict.get("status")
    ip = data_dict.get("ip")
    version = data_dict.get("version")

    # Trích xuất phần dữ liệu cần so sánh
    chipid_data = data_json.get('chipid', {})

    if api_value in chipid_data:
        chip_data = chipid_data[api_value]
        if name in chip_data:
            name_data = chip_data[name]
            mac_address = name_data["mac_address"]
            camera = name_data["camera"]
            timer = name_data["timer"]

            logger.debug(f"Dữ liệu cho {name}: {name_data}")

            # Xử lý hình ảnh
            cap = cv2.VideoCapture(camera)
            retval, img = cap.read()
            if retval:
                strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
            else:
                logger.warning(f"Không thể đọc frame từ camera: {camera}, sử dụng ảnh mặc định.")
                with open('./database/json/abc.jpg', "rb") as f:
                    strImg64 = base64.b64encode(f.read()).decode()

            # Tạo data gửi server
            data = {
                "mac_address": mac_address,
                "action_name": status,
                "timer": timer,
                "img": strImg64
            }

            try:
                r = requests.post("http://10.50.41.18:58185/api/Farm/postbiohistory",
                                  json.dumps(data),
                                  headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                code = r.status_code
                response_text = r.text
            except requests.RequestException as e:
                logger.error("Lỗi khi gửi request đến server: %s", e)
                return {"status_code": None, "error": str(e)}

            # Kiểm tra xem `api_value` có nằm trong danh sách loại trừ không
            if api_value in excluded_chipids:
                logger.info(f"Chipid {api_value} nằm trong danh sách loại trừ, không cập nhật dữ liệu.")
            else:
                # Cập nhật giá trị ip và version nếu không nằm trong danh sách loại trừ
                about_data = data_json['chipid'].get(api_value, {}).get('about', {})
                if 'ip' in about_data and 'version' in about_data:
                    about_data['ip'] = ip
                    about_data['version'] = version
                    with open(link + file, 'w', encoding='utf-8') as fout:
                        json.dump(data_json, fout, ensure_ascii=False, indent=4)
                    logger.critical('Đã cập nhật dữ liệu about: %s', api_value)
                else:
                    logger.error("Không tìm thấy dữ liệu about để cập nhật cho ID: %s", api_value)

            data_log = {
                "mac_address": mac_address,
                "action_name": status,
                "timer": timer
            }
            logger.critical("\n Dữ liệu process_data: %s\n Mã trạng thái HTTP server: %s, Phản hồi từ server: %s",
                            data_log, code, response_text)

            return {"status_code": code, "response_text": response_text}
        else:
            logger.error("Không tìm thấy thông tin cho ID: %s -> %s -> %s", api_value, name, status)
            return {"status_code": None, "error": "Name không tồn tại"}
    else:
        logger.error("Dữ liệu không trùng khớp hoặc không tìm thấy.")
        return {"status_code": None, "error": "ID chip không tồn tại"}
