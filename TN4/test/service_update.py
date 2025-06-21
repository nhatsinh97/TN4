import cv2
import requests
import base64
import time
import os
import ast
import json
import sqlite3
import logging
from logging import Formatter, FileHandler, StreamHandler
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from threading import Thread
from flask import Flask, render_template, request
logger = logging.getLogger('cico_log')
logger.setLevel(logging.DEBUG)
formatter = Formatter('%(asctime)s - %(levelname)s - [in %(pathname)s:%(lineno)d] %(message)s')

# Stream handles
stream_handler = StreamHandler()
stream_handler.setLevel(logging.CRITICAL)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Split log at 0h everyday
file_handler = TimedRotatingFileHandler('./database/log/log_cico_everyday.log', when="midnight", interval=1)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# Khai báo các biến

api        = 'http://172.17.128.50:58185/api/MasterData/getitembycode'
apitimer   = 'http://172.17.128.50:58185/api/Farm/getcountdownsecond'
url        = 'http://172.17.128.50:58185/api/Farm/postbiohistory'

logger.info("Start: GF-CICO")

app = Flask(__name__)
# Trang chính web
@app.route("/")
def home():
    return render_template("index.html")
@app.route("/home", methods = ['POST'])
def admin():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'admin':
        return render_template("home.html")
    return 'failed'
@app.route("/iot")
def iot():
    return render_template("iot.html")
@app.route("/login", methods = ['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'admin':
        return render_template("home.html")
    return 'failed'
# Xử lý tín hiệu phòng UV1
def config_uv1():
    # print('hàm uv1')
    with open('./database/json/total_data.json', "r", encoding='utf-8') as fin:
        data = json.load(fin)
    ID = (data["ID"])
    reset = (data["reset"])
    check = (data["check"])
    cam_1 = (data["cam_1"])
    cam_2 = (data["cam_2"])
    status_uv1 = (data["phonguv1"]["status_uv1"])
    status_uv2 = (data["phonguv2"]["status_uv2"])
    cb_cua1 = (data["phonguv1"]["cb_cua1"])
    cb_cua2 = (data["phonguv2"]["cb_cua2"])
    # print('dữ liệu ID = {}'. format(ID))
    r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_1}), 
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
    code = r.status_code
    file = r.json()
    if code == 200:
        status_uv1 = "1" 
        with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        stt1 = (check[ID]["statusuv_1"])
        stt2 = (check[ID]["statusuv_2"])
        stt_cb1 = (check[ID]["cb_cua1"])
        stt_cb2 = (check[ID]["cb_cua2"])
        reset = (check[ID]["reset"])
        dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
        with open('./database/json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
            json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
        out = {"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}
        return (out)
# Xử lý tín hiệu phòng UV2
def config_uv2():
    # print("uv2 ok")
    with open('./database/json/total_data.json', "r", encoding='utf-8') as fin:
        data = json.load(fin)
    ID = (data["ID"])
    reset = (data["reset"])
    check = (data["check"])
    cam_1 = (data["cam_1"])
    cam_2 = (data["cam_2"])
    status_uv1 = (data["phonguv1"]["status_uv1"])
    status_uv2 = (data["phonguv2"]["status_uv2"])
    cb_cua1 = (data["phonguv1"]["cb_cua1"])
    cb_cua2 = (data["phonguv2"]["cb_cua2"])
    # print('dữ liệu ID = {}'. format(ID))
    r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_2}), 
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
    code = r.status_code
    file = r.json()
    if code == 200:
        status_uv2 = "1" 
        with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        stt1 = (check[ID]["statusuv_1"])
        stt2 = (check[ID]["statusuv_2"])
        stt_cb1 = (check[ID]["cb_cua1"])
        stt_cb2 = (check[ID]["cb_cua2"])
        reset = (check[ID]["reset"])
        dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
        with open('./database/json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
            json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
        out = {"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}
        return (out)
# Gửi thông báo khi cửa phòng UV1 được mở
def phong_1():
    with open('./database/json/total_data.json', "r", encoding='utf-8') as fin:
        data = json.load(fin)
    ID = (data["ID"])
    reset = (data["reset"])
    check = (data["check"])
    cam_1 = (data["cam_1"])
    cam_2 = (data["cam_2"])
    status_uv1 = (data["phonguv1"]["status_uv1"])
    status_uv2 = (data["phonguv2"]["status_uv2"])
    cb_cua1 = (data["phonguv1"]["cb_cua1"])
    cb_cua2 = (data["phonguv2"]["cb_cua2"])
    r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_1}), 
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    data_uv1 = r.json()
    rtsp_1 = (data_uv1[0]["ATT2"])
    cap = cv2.VideoCapture(rtsp_1)
    retval, img = cap.read()
    if retval:
        strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    if not retval:
        with open('./database/json/abc.jpg', "rb") as f:
            strImg64 = base64.b64encode(f.read()).decode()
    r = requests.post(url, data=json.dumps({
        "mac_address": cam_1 ,
        "action_name": "RECEIVE",
        "timer": "",
        "img": strImg64
    }), headers={
        'Content-type': 'application/json', 'Accept': 'text/plain'})
    code = r.status_code
    file = r.json()
    if code == 200:
        stt_cb1 = "0"
        with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        stt1 = (check[ID]["statusuv_1"])
        stt2 = (check[ID]["statusuv_2"])
        stt_cb1 = (check[ID]["cb_cua1"])
        stt_cb2 = (check[ID]["cb_cua2"])
        reset = (check[ID]["reset"])
        dataa = { ID:{ "reset": reset,"statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
        with open('./database/json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
            json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
        out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
        return (out)
# Gửi thông báo khi cửa phòng UV2 được mở
def phong_2():
    with open('./database/json/total_data.json', "r", encoding='utf-8') as fin:
        data = json.load(fin)
    ID = (data["ID"])
    reset = (data["reset"])
    check = (data["check"])
    cam_1 = (data["cam_1"])
    cam_2 = (data["cam_2"])
    status_uv1 = (data["phonguv1"]["status_uv1"])
    status_uv2 = (data["phonguv2"]["status_uv2"])
    cb_cua1 = (data["phonguv1"]["cb_cua1"])
    cb_cua2 = (data["phonguv2"]["cb_cua2"])
    r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_2}), 
        headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
    data_uv2 = r.json()
    rtsp_2 = (data_uv2[0]["ATT2"])
    cap = cv2.VideoCapture(rtsp_2)
    retval, img = cap.read()
    if retval:
        strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    if not retval:
        with open('./database/json/abc.jpg', "rb") as f:
            strImg64 = base64.b64encode(f.read()).decode()
    r = requests.post(url, data=json.dumps({
        "mac_address": cam_2 ,
        "action_name": "RECEIVE",
        "timer": "",
        "img": strImg64
    }), headers={
        'Content-type': 'application/json', 'Accept': 'text/plain'})
    code = r.status_code
    file = r.json()
    if code == 200:
        stt_cb2 = "0"
        with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        stt1 = (check[ID]["statusuv_1"])
        stt2 = (check[ID]["statusuv_2"])
        stt_cb1 = (check[ID]["cb_cua1"])
        stt_cb2 = (check[ID]["cb_cua2"])
        reset = (check[ID]["reset"])
        dataa = { ID:{ "reset": reset,"statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
        with open('./database/json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
            json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
        out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
        return (out)
    
# API xử lý request từ thiết bị IOT

@app.route('/api', methods = ['POST'])
def iot_request():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = ast.literal_eval(request.data.decode())
        logger.critical(data)
        with open('./database/json/total_data.json', 'w', encoding='utf-8') as out_file:
            json.dump(data, out_file, ensure_ascii=False, indent = 4)
        ID = (data["ID"])
        reset = (data["reset"])
        check = (data["check"])
        cam_1 = (data["cam_1"])
        cam_2 = (data["cam_2"])
        status_uv1 = (data["phonguv1"]["status_uv1"])
        status_uv2 = (data["phonguv2"]["status_uv2"])
        cb_cua1 = (data["phonguv1"]["cb_cua1"])
        cb_cua2 = (data["phonguv2"]["cb_cua2"])
        if check == "True":
            with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
                check = json.load(fin)
            stt1 = (check[ID]["statusuv_1"])
            stt2 = (check[ID]["statusuv_2"])
            stt_cb1 = (check[ID]["cb_cua1"])
            stt_cb2 = (check[ID]["cb_cua2"])
            reset = (check[ID]["reset"])
            out = {"reset":reset,"status_uv1":stt1,"status_uv2":stt2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}
            return out
        # Mở file json theo ID trại và kiểm tra trạng thái
        with open("./database/json/"+ ID + ".json", "r", encoding='utf-8') as fin:
            check = json.load(fin)
        # print("tới 223")
        stt1 = (check[ID]["statusuv_1"])
        stt2 = (check[ID]["statusuv_2"])
        stt_cb1 = (check[ID]["cb_cua1"])
        stt_cb2 = (check[ID]["cb_cua2"])
        reset = (check[ID]["reset"])
        if reset == "True":
            data = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
            with open('./database/json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                json.dump(data, out_file, ensure_ascii=False, indent = 4)
            out = {"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}
            return out
        if status_uv1 == "1" :
            if stt1 == "0":
                thread = Thread(target=config_uv1)
                thread.start()
        if status_uv2 == "1" :
            if stt2 == "0":
                thread = Thread(target=config_uv2)
                thread.start()
        if cb_cua1 == "1" :
            if stt_cb1 == "0":
                thread = Thread(target=phong_1)
                thread.start()
        if cb_cua2 == "1" :
            if stt_cb2 == "0":
                thread = Thread(target=phong_2)
                thread.start()
        out = {"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}
        print(out)
        return out
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=58888 ,debug=True)