import cv2
import os

RTSP_URL = 'rtsp://admin:Admin123@192.168.32.205/cam/realmonitor?channel=1&subtype=00&authbasic=YWRtaW46QWRtaW4xMjM='

os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

if not cap.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)

while True:
    _, frame = cap.read()
    cv2.imwrite('opencv.png', frame)
    # cv2.imshow('RTSP stream', frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()