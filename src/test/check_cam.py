import cv2
import base64
tn4 = cv2.VideoCapture('rtsp://admin:Passw0rd@10.16.41.206/profile2/media.smp')
uv1 = cv2.VideoCapture('rtsp://admin:L283A86A@192.168.41.60/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
bt = cv2.VideoCapture('rtsp://admin:Admin123@192.168.37.202/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
uv2 = cv2.VideoCapture('rtsp://admin:L2122A61@192.168.41.216/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
dnb2 = cv2.VideoCapture('rtsp://admin:Admin123@192.168.36.210/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
cj = cv2.VideoCapture('rtsp://admin:Admin123@192.168.30.9/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
lv22 = cv2.VideoCapture('rtsp://admin:Passw0rd@192.168.41.203/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')
# cj = 9,16,15,10,
# while True:
ret, img = cj.read()
if ret:
    print("ok")
    cv2.imwrite('opencv.png', img)
    strImg64 = base64.b64encode(cv2.imencode('.jpg', img)[1]).decode()
    with open('base64.txt', "w") as wf:
        wf.writelines(strImg64)
        print("Đã lưu File base64")
if not ret:
    print("không kết nối")

# from flask import Flask, render_template, Response
# # import cv2

# app = Flask(__name__)

# camera = cv2.VideoCapture(0)   
# ('rtsp://admin:Passw0rd@10.16.41.206/profile2/media.smp')  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

# def gen_frames():  # generate frame by frame from camera
#     while True:
#         # Capture frame-by-frame
#         success, frame = camera.read('rtsp://admin:Admin123@192.168.30.9/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM=')  # read the camera frame
#         if not success:
#             break
#         else:
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


# @app.route('/video_feed')
# def video_feed():
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=58887 ,debug=False)