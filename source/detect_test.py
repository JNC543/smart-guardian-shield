import cv2
import numpy as np

# ===== 設定 =====
PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONF_THRESHOLD = 0.5   # 信心度門檻，越高越嚴格
PERSON_ID = 15         # 此模型中 person 的類別編號
LEFT_ZONE = 0.25       # 畫面左邊 25% 為監測區
RIGHT_ZONE = 0.75      # 畫面右邊 25% 為監測區
# ================

net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
cap = cv2.VideoCapture(0)

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame = cv2.flip(frame, 1)  # 左右翻轉，像照鏡子
    h, w = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    # 畫出監測區邊界
    lx, rx = int(w * LEFT_ZONE), int(w * RIGHT_ZONE)
    cv2.line(frame, (lx, 0), (lx, h), (255, 200, 0), 2)
    cv2.line(frame, (rx, 0), (rx, h), (255, 200, 0), 2)

    alert = False
    for i in range(detections.shape[2]):
        conf = detections[0, 0, i, 2]
        cls = int(detections[0, 0, i, 1])
        if cls == PERSON_ID and conf > CONF_THRESHOLD:
            x1, y1, x2, y2 = (detections[0, 0, i, 3:7] * np.array([w, h, w, h])).astype(int)
            cx = (x1 + x2) // 2
            in_zone = cx < lx or cx > rx
            color = (0, 0, 255) if in_zone else (0, 255, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"person {conf:.0%}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            if in_zone:
                alert = True

    if alert:
        cv2.putText(frame, "ALERT!", (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    cv2.imshow("Detect Test (press q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()