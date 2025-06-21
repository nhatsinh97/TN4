from flask import Flask, render_template,request
from data_request import *
import os, cv2
import ast, json
import base64
import threading
import requests
api_cico = 'http://172.17.128.50:58185/api/MasterData/getitembycode'
api_timer_countdown = 'http://172.17.128.50:58185/api/Farm/getcountdownsecond'
url = 'http://172.17.128.50:58185/api/Farm/postbiohistory'

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin':
        return render_template("home.html")
    return 'failed'

@app.route('/api', methods = ['POST'])
def refresh_service():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = ast.literal_eval(request.data.decode())
        print(data)
        with open('./database/json/total_data.json', 'w', encoding='utf-8') as out_file:
            json.dump(data, out_file, ensure_ascii=False, indent = 4)
        id_farm = (data["ID"])
        ip_iot  = (data["IP"])
        reset = (data["reset"])
        check = (data["check"])
        cam_1 = (data["cam_1"])
        cam_2 = (data["cam_2"])
        status_uv1 = (data["phonguv1"]["status_uv1"])
        status_uv2 = (data["phonguv2"]["status_uv2"])
        cb_cua1 = (data["phonguv1"]["cb_cua1"])
        cb_cua2 = (data["phonguv2"]["cb_cua2"])
        if check == "True":
            with open("./database/json/"+ id_farm + ".json", "r", encoding='utf-8') as fin:
                check = json.load(fin)
            stt1 = (check[id_farm]["statusuv_1"])
            stt2 = (check[id_farm]["statusuv_2"])
            stt_cb1 = (check[id_farm]["cb_cua1"])
            stt_cb2 = (check[id_farm]["cb_cua2"])
            reset = (check[id_farm]["reset"])
            data_out = [{"reset":reset,"status_uv1":stt1,"status_uv2":stt2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}]
            print(data_out)
            return (data_out)
        with open("./database/json/"+ id_farm + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        stt1 = (check[id_farm]["statusuv_1"])
        stt2 = (check[id_farm]["statusuv_2"])
        stt_cb1 = (check[id_farm]["cb_cua1"])
        stt_cb2 = (check[id_farm]["cb_cua2"])
        reset = (check[id_farm]["reset"])
        # --- Nếu có tín hiệu reset từ server thì khởi động lại thiết bị ---
        if reset == "True":
            data_out = { 
                id_farm:
                { 
                 "reset":"False",
                 "IP": ip_iot ,
                 "statusuv_1":status_uv1,
                 "statusuv_2": status_uv2,
                 "cb_cua1":stt_cb1,
                 "cb_cua2":stt_cb2
                 }
                 }
            with open('./database/json/' + id_farm + '.json', 'w', encoding='utf-8') as out_file:
                json.dump(data_out, out_file, ensure_ascii=False, indent = 4)
            data_out = [{
                "reset":reset,
                "status_uv1":status_uv1,
                "status_uv2":status_uv2,
                "cb_cua1":cb_cua1,
                "cb_cua2":cb_cua2
                }]
            return (data_out)
    #------------------------- START XỬ LÝ DATA GỬI LÊN SERVER --------------------------#
    #------------------------- Nếu có tín hiệu bật phòng UV --------------------------#
        if status_uv1 == "1":
            if stt1 == "0":
                r = requests.post(api_cico, data =json.dumps({"item_code": id_farm,"item_type":"BIO_CAMERA", "ATT1":cam_1}), 
                   headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                data_uv1 = r.json()
                rtsp_1 = (data_uv1[0]["ATT2"])
                timer_uv1 = (data_uv1[0]["ATT3"])
                cap = cv2.VideoCapture(rtsp_1)
                retval, img = cap.read()
                if retval:
                    strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                if not retval:
                    with open('./database/json/abc.jpg', "rb") as f:
                        strImg64 = base64.b64encode(f.read()).decode()
                r = requests.post(url, data=json.dumps({
                    "mac_address": cam_1 ,
                    "action_name": "start",
                    "timer": timer_uv1,
                    "img": strImg64
                }), headers={
                    'Content-type': 'application/json', 'Accept': 'text/plain'})
                feedback = r.json()
                if feedback == 200:
                    status_uv1 = "1"
                    data_out = { 
                        id_farm:{ 
                            "reset":"False",
                            "IP": ip_iot ,
                            "statusuv_1":status_uv1,
                            "statusuv_2": status_uv2,
                            "cb_cua1":stt_cb1,
                            "cb_cua2":stt_cb2
                            }}
                    with open('./database/json/' + id_farm + '.json', 'w', encoding='utf-8') as out_file:
                        json.dump(data_out, out_file, ensure_ascii=False, indent = 4)
                    data_out = [{
                        "reset":reset,
                        "status_uv1":status_uv1,
                        "status_uv2":status_uv2,
                        "cb_cua1":cb_cua1,
                        "cb_cua2":cb_cua2
                        }]
                    return (data_out)
    #------------------------- Nếu có tín hiệu tắt phòng UV --------------------------#
        if status_uv1 == "0" :
            if stt1 == "1":
                r = requests.post(api_cico, data =json.dumps({"item_code": id_farm,"item_type":"BIO_CAMERA", "ATT1":cam_1}), 
                    headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                data_uv1 = r.json()
                rtsp_1 = (data_uv1[0]["ATT2"])
                timer_uv1 = (data_uv1[0]["ATT3"])
                cap = cv2.VideoCapture(rtsp_1)
                retval, img = cap.read()
                if retval:
                    strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                if not retval:
                    with open('./database/json/abc.jpg', "rb") as f:
                        strImg64 = base64.b64encode(f.read()).decode()
                r = requests.post(url, data=json.dumps({
                    "mac_address": cam_1 ,
                    "action_name": "end",
                    "timer": timer_uv1,
                    "img": strImg64
                }), headers={
                    'Content-type': 'application/json', 'Accept': 'text/plain'})
                feedback = r.json()
                if feedback == 200:
                    status_uv1 = "0"
                    data_out = { id_farm:{ 
                        "reset": reset,
                        "IP": ip_iot ,
                        "statusuv_1":status_uv1,
                        "statusuv_2": status_uv2,
                        "cb_cua1":stt_cb1,
                        "cb_cua2":stt_cb2
                        }}
                    with open('./database/json/' + id_farm + '.json', 'w', encoding='utf-8') as out_file:
                        json.dump(data_out, out_file, ensure_ascii=False, indent = 4)
                    data_out = [{
                        "reset":reset,
                        "status_uv1":status_uv1,
                        "status_uv2":status_uv2,
                        "cb_cua1":cb_cua1,
                        "cb_cua2":cb_cua2
                        }]
                    return (data_out)
        #---------------- Phong UV 2 --------------------------
        if status_uv2 == "1" :
            if stt2 == "0":
                r = requests.post(api_cico, data =json.dumps({"item_code": id_farm,"item_type":"BIO_CAMERA", "ATT1":cam_2}), 
                    headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                data_uv2 = r.json()
                rtsp_2 = (data_uv2[0]["ATT2"])
                timer_uv2 = (data_uv2[0]["ATT3"])
                cap = cv2.VideoCapture(rtsp_2)
                retval, img = cap.read()
                if retval:
                    strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                if not retval:
                    with open('./database/json/abc.jpg', "rb") as f:
                        strImg64 = base64.b64encode(f.read()).decode()
                r = requests.post(url, data=json.dumps({
                    "mac_address": cam_2 ,
                    "action_name": "start",
                    "timer": timer_uv2,
                    "img": strImg64
                }), headers={
                    'Content-type': 'application/json', 'Accept': 'text/plain'})
                feedback = r.json()
                if feedback == 200:
                    status_uv2 = "1"
                    data_out = { 
                        id_farm:{ 
                            "reset":"False",
                            "IP": ip_iot ,
                            "statusuv_1":status_uv1,
                            "statusuv_2": status_uv2,
                            "cb_cua1":stt_cb1,
                            "cb_cua2":stt_cb2
                            }}
                    with open('./database/json/' + id_farm + '.json', 'w', encoding='utf-8') as out_file:
                        json.dump(data_out, out_file, ensure_ascii=False, indent = 4)
                    data_out = [{
                        "reset":reset,
                        "status_uv1":status_uv1,
                        "status_uv2":status_uv2,
                        "cb_cua1":cb_cua1,
                        "cb_cua2":cb_cua2
                        }]
                    return (data_out)
        if status_uv2 == "0" :
            if stt2 == "1":
                r = requests.post(api_cico, data =json.dumps({"item_code": id_farm,"item_type":"BIO_CAMERA", "ATT1":cam_2}), 
                    headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                data_uv2 = r.json()
                rtsp_2 = (data_uv2[0]["ATT2"])
                timer_uv2 = (data_uv2[0]["ATT3"])
                cap = cv2.VideoCapture(rtsp_2)
                retval, img = cap.read()
                if retval:
                    strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                if not retval:
                    with open('./database/json/abc.jpg', "rb") as f:
                        strImg64 = base64.b64encode(f.read()).decode()
                r = requests.post(url, data=json.dumps({
                    "mac_address": cam_2 ,
                    "action_name": "end",
                    "timer": timer_uv2,
                    "img": strImg64
                }), headers={
                    'Content-type': 'application/json', 'Accept': 'text/plain'})
                feedback = r.json()
                if feedback == 200:
                    status_uv2 = "0"
                    data_out = { id_farm:{ 
                        "reset":"False",
                        "IP": ip_iot ,
                        "statusuv_1":status_uv1,
                        "statusuv_2": status_uv2,
                        "cb_cua1":stt_cb1,
                        "cb_cua2":stt_cb2
                        }}
                    with open('./database/json/' + id_farm + '.json', 'w', encoding='utf-8') as out_file:
                        json.dump(data_out, out_file, ensure_ascii=False, indent = 4)
                    data_out = [{
                        "reset":reset,
                        "status_uv1":status_uv1,
                        "status_uv2":status_uv2,
                        "cb_cua1":cb_cua1,
                        "cb_cua2":cb_cua2
                        }]
                    return (data_out)
        return
    return
                    


if __name__ == '__main__':
    app.run(host='172.17.128.24', port=58888, debug=False)