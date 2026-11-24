import cv2

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("無法開啟鏡頭")
    raise SystemExit

while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow("Camera Test (press q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
