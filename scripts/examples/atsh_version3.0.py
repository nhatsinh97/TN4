# encoding: utf-8
# cd /home/erpfarm/workspace/GF_IOT
# python3 service.py
import json
import sqlite3
import logging
# from systemd.journal import JournalHandler
import cv2
import requests
import base64
import time
import os
from flask import Flask, request
import ast

# connecting to the database  
connection = sqlite3.connect("./SQL/atsh.db")
# cursor  
crsr = connection.cursor() 
# SQL command to create a table in the database 
sql_command = """CREATE TABLE emp (  
staff_number INTEGER PRIMARY KEY,  
ID_timer DATE,
ID_name VARCHAR(30),  
ID_status VARCHAR(30),  
total_timer VARCHAR(20));"""
# execute the statement 
crsr.execute(sql_command) 
# SQL command to insert the data in the table 
sql_command = """INSERT INTO emp VALUES (23, "2022-10-06", "GF_BT", "GF_BT_CAMERA01", "64");"""
crsr.execute(sql_command) 
# another SQL command to insert the data in the table 
sql_command = """INSERT INTO emp VALUES (1, "2022-10-06", "GF_LV2", "GF_LV2_CAMERA01", "94");"""
crsr.execute(sql_command) 
# To save the changes in the files. Never skip this.  
# If we skip this, nothing will be saved in the database. 
connection.commit() 
# close the connection 
connection.close() 
api = 'http://172.17.128.50:58185/api/MasterData/getitembycode'
apitimer = 'http://172.17.128.50:58185/api/Farm/getcountdownsecond'
url = 'http://172.17.128.50:58185/api/Farm/postbiohistory'
try:
    app = Flask(__name__)
    @app.route('/api', methods = ['POST'])
    def refresh_service():
        content_type = request.headers.get('Content-Type')
        try:
            sqliteConnection = sqlite3.connect('gf_iot.db')
            cursor = sqliteConnection.cursor()

            if (content_type == 'application/json'):
                data = ast.literal_eval(request.data.decode())
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
                    with open("./json/"+ ID + ".json", "r", encoding='utf-8') as fin:
                        check = json.load(fin)
                    stt1 = (check[ID]["statusuv_1"])
                    stt2 = (check[ID]["statusuv_2"])
                    stt_cb1 = (check[ID]["cb_cua1"])
                    stt_cb2 = (check[ID]["cb_cua2"])
                    reset = (check[ID]["reset"])
                    out = [{"reset":reset,"status_uv1":stt1,"status_uv2":stt2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}]
                    return (out)
                with open("./json/"+ ID + ".json", "r", encoding='utf-8') as fin:
                    check = json.load(fin)
                stt1 = (check[ID]["statusuv_1"])
                stt2 = (check[ID]["statusuv_2"])
                stt_cb1 = (check[ID]["cb_cua1"])
                stt_cb2 = (check[ID]["cb_cua2"])
                reset = (check[ID]["reset"])
                if reset == "True":
                    dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                    with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                        json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                    out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                    return (out)
    #-------------------------- START XỬ LÝ DATA GỬI LÊN SERVER --------------------------#
                if status_uv1 == "1" :
                    if stt1 == "0":
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
                            with open('./json/abc.jpg', "rb") as f:
                                strImg64 = base64.b64encode(f.read()).decode()
                        r = requests.post(url, data=json.dumps({
                            "mac_address": cam_1 ,
                            "action_name": "start",
                            "timer": timer_uv1,
                            "img": strImg64
                        }), headers={
                            'Content-type': 'application/json', 'Accept': 'text/plain'})
                        file = r.json()
                        if file == 200:
                            status_uv1 = "1" # cho nay ghi nhan lich su vao file json
                            dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                            with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                            out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                            sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                            cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                            sqliteConnection.commit()
                            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                            cursor.close()
                            return (out)
                if status_uv1 == "0" :
                    if stt1 == "1":
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
                            with open('./json/abc.jpg', "rb") as f:
                                strImg64 = base64.b64encode(f.read()).decode()
                        r = requests.post(url, data=json.dumps({
                            "mac_address": cam_1 ,
                            "action_name": "end",
                            "timer": timer_uv1,
                            "img": strImg64
                        }), headers={
                            'Content-type': 'application/json', 'Accept': 'text/plain'})
                        file = r.json()
                        if file == 200:
                            status_uv1 = "0"
                            dataa = { ID:{ "reset": reset,"statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                            with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                            out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                            sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                            cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                            sqliteConnection.commit()
                            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                            cursor.close()
                            return (out)
                if cb_cua1 == "3":
                    if stt_cb1 == "0":
                        r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_1}), 
                            headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                        data_uv1 = r.json()
                        rtsp_1 = (data_uv1[0]["ATT2"])
                        cap = cv2.VideoCapture(rtsp_1)
                        retval, img = cap.read()
                        if retval:
                            strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                        if not retval:
                            with open('./json/abc.jpg', "rb") as f:
                                strImg64 = base64.b64encode(f.read()).decode()
                        r = requests.post(url, data=json.dumps({
                            "mac_address": cam_1 ,
                            "action_name": "RECEIVE",
                            "timer": "",
                            "img": strImg64
                        }), headers={
                            'Content-type': 'application/json', 'Accept': 'text/plain'})
                        file = r.json()
                        if file == 200:
                            stt_cb1 = "1"
                            dataa = { ID:{ "reset": reset,"statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                            with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                            out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                            sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                            cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                            sqliteConnection.commit()
                            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                            cursor.close()
                            return (out)
                # if cb_cua1 = 0:

                #----------------- Phong UV 2 --------------------------
                if status_uv2 == "1" :
                    if stt2 == "0":
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
                            with open('./json/abc.jpg', "rb") as f:
                                strImg64 = base64.b64encode(f.read()).decode()
                        r = requests.post(url, data=json.dumps({
                            "mac_address": cam_2 ,
                            "action_name": "start",
                            "timer": timer_uv2,
                            "img": strImg64
                        }), headers={
                            'Content-type': 'application/json', 'Accept': 'text/plain'})
                        file = r.json()
                        if file == 200:
                            status_uv2 = "1"
                            dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                            with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                            out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                            sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                            cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                            sqliteConnection.commit()
                            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                            cursor.close()
                            return (out)
                if status_uv2 == "0" :
                        if stt2 == "1":
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
                                with open('./json/abc.jpg', "rb") as f:
                                    strImg64 = base64.b64encode(f.read()).decode()
                            r = requests.post(url, data=json.dumps({
                                "mac_address": cam_2 ,
                                "action_name": "end",
                                "timer": timer_uv2,
                                "img": strImg64
                            }), headers={
                                'Content-type': 'application/json', 'Accept': 'text/plain'})
                            file = r.json()
                            if file == 200:
                                status_uv2 = "0"
                                dataa = { ID:{ "reset":"False","statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                                with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                    json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                                out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                                
                                sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                                cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                                sqliteConnection.commit()
                                print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                                cursor.close()
                                return (out)
                if cb_cua2 == "3":
                    if stt_cb2 == "0":
                        r = requests.post(api, data =json.dumps({"item_code": ID,"item_type":"BIO_CAMERA", "ATT1":cam_2}), 
                            headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
                        data_uv2 = r.json()
                        rtsp_2 = (data_uv2[0]["ATT2"])
                        cap = cv2.VideoCapture(rtsp_2)
                        retval, img = cap.read()
                        if retval:
                            strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
                        if not retval:
                            with open('./json/abc.jpg', "rb") as f:
                                strImg64 = base64.b64encode(f.read()).decode()
                        r = requests.post(url, data=json.dumps({
                            "mac_address": cam_2 ,
                            "action_name": "RECEIVE",
                            "timer": "",
                            "img": strImg64
                        }), headers={
                            'Content-type': 'application/json', 'Accept': 'text/plain'})
                        file = r.json()
                        if file == 200:
                            stt_cb2 = "0"
                            dataa = { ID:{ "reset": reset,"statusuv_1":status_uv1,"statusuv_2": status_uv2,"cb_cua1":stt_cb1,"cb_cua2":stt_cb2}}
                            with open('./json/' + ID + '.json', 'w', encoding='utf-8') as out_file:
                                json.dump(dataa, out_file, ensure_ascii=False, indent = 4)
                            out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                            sqlite_update_query = ''' UPDATE uv
                                    SET iot_signal = ? ,
                                        reset = ? ,
                                        statusuv_1 = ?,
                                        statusuv_2 = ?,
                                        cb_cua1 = ?,
                                        cb_cua2 = ?
                                    WHERE farm_name = ?'''
                            cursor.execute(sqlite_update_query, (1, reset, status_uv1, status_uv2, cb_cua1, cb_cua2, ID))
                            sqliteConnection.commit()
                            print("Record inserted successfully into SqliteDb_developers table ", cursor.rowcount)
                            cursor.close()
                            return (out)
                out = [{"reset":reset,"status_uv1":status_uv1,"status_uv2":status_uv2,"cb_cua1":cb_cua1,"cb_cua2":cb_cua2}]
                return (out)
        except sqlite3.Error as error:
            print("Failed to insert data into sqlite table", error)
        finally:
            if sqliteConnection:
                sqliteConnection.close()
                print("The SQLite connection is closed")
    app.run(host='0.0.0.0', port=58889)  
except:
    pass