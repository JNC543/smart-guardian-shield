import threading
import time
import tkinter as tk

import cv2
import numpy as np

from dashboard import draw_dashboard

# ===== 設定 =====
PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONF_THRESHOLD = 0.5   # 辨識信心度門檻
PERSON_ID = 15         # person 的類別編號
LEFT_ZONE = 0.25       # 左側監測區（畫面左 25%）
RIGHT_ZONE = 0.75      # 右側監測區（畫面右 25%）
HITS_NEEDED = 3        # 連續幾個畫面都偵測到才觸發
COOLDOWN_SEC = 3       # 關閉假畫面後的冷卻秒數
FONT = "Microsoft JhengHei"
# ================


class GuardianApp:
    def __init__(self, root):
        self.root = root
        root.title("Smart Guardian Shield")
        root.minsize(320, 270)  # 不固定大小，讓視窗依內容自動調整（高 DPI 螢幕才不會被切掉）
        root.resizable(False, False)

        self.stop_event = threading.Event()
        self.running = False
        self.paused = False
        self.alert = False
        self.error = None
        self.cooldown_until = 0
        self.decoy = None
        self.thread = None

        self.status = tk.StringVar(value="狀態：已停止")
        tk.Label(root, text="Smart Guardian Shield",
                 font=(FONT, 14, "bold")).pack(pady=12)
        tk.Label(root, textvariable=self.status, font=(FONT, 11)).pack(pady=4)

        self.btn_start = tk.Button(root, text="啟動防護", width=18,
                                   font=(FONT, 11), command=self.start)
        self.btn_start.pack(pady=4)
        self.btn_pause = tk.Button(root, text="暫停", width=18,
                                   font=(FONT, 11), command=self.toggle_pause)
        self.btn_pause.pack(pady=4)
        self.btn_stop = tk.Button(root, text="停止防護", width=18,
                                  font=(FONT, 11), command=self.stop)
        self.btn_stop.pack(pady=4)
        tk.Label(root, text="偵測到人時，按 Esc 可回到原本畫面",
                 font=(FONT, 9), fg="gray").pack(pady=8)

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        root.after(100, self.poll)

    # ---------- 控制按鈕 ----------
    def start(self):
        if self.running:
            return
        self.stop_event.clear()
        self.paused = False
        self.running = True
        self.btn_pause.config(text="暫停")
        self.status.set("狀態：防護中")
        self.thread = threading.Thread(target=self.detect_loop, daemon=True)
        self.thread.start()

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        if self.paused:
            self.btn_pause.config(text="繼續")
            self.status.set("狀態：已暫停")
        else:
            self.btn_pause.config(text="暫停")
            self.status.set("狀態：防護中")

    def stop(self):
        if not self.running:
            return
        self.stop_event.set()
        self.running = False
        self.paused = False
        self.btn_pause.config(text="暫停")
        self.status.set("狀態：已停止")
        self.close_decoy()

    def on_close(self):
        self.stop_event.set()
        self.root.destroy()

    # ---------- 偵測（背景執行緒） ----------
    def detect_loop(self):
        try:
            net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
        except Exception as e:
            self.error = f"模型載入失敗：{e}"
            return
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.error = "無法開啟鏡頭"
            return

        hits = 0
        while not self.stop_event.is_set():
            if self.paused:
                time.sleep(0.2)
                continue
            ok, frame = cap.read()
            if not ok:
                self.error = "讀取鏡頭失敗"
                break
            frame = cv2.flip(frame, 1)
            in_zone = self.person_in_zone(net, frame)
            hits = hits + 1 if in_zone else 0
            if (hits >= HITS_NEEDED and self.decoy is None
                    and time.time() > self.cooldown_until):
                self.alert = True
                hits = 0
        cap.release()

    def person_in_zone(self, net, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                     0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()
        lx, rx = w * LEFT_ZONE, w * RIGHT_ZONE
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            cls = int(detections[0, 0, i, 1])
            if cls == PERSON_ID and conf > CONF_THRESHOLD:
                x1, y1, x2, y2 = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                cx = (x1 + x2) / 2
                if cx < lx or cx > rx:
                    return True
        return False

    # ---------- 主執行緒定期檢查 ----------
    def poll(self):
        if self.error:
            self.status.set(f"錯誤：{self.error}")
            self.running = False
            self.error = None
        if self.alert:
            self.alert = False
            if self.decoy is None:
                self.show_decoy()
        self.root.after(100, self.poll)

    # ---------- 假的工作畫面（Power BI 風格儀表板） ----------
    def show_decoy(self):
        win = tk.Toplevel(self.root)
        self.decoy = win
        win.title("Sales Performance - Dashboard")
        win.attributes("-fullscreen", True)
        win.attributes("-topmost", True)
        win.configure(bg="#F3F2F1")
        win.bind("<Escape>", lambda e: self.close_decoy())

        W = win.winfo_screenwidth()
        H = win.winfo_screenheight()
        canvas = tk.Canvas(win, width=W, height=H, bg="#F3F2F1",
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        draw_dashboard(canvas, W, H)
        win.focus_force()

    def close_decoy(self):
        if self.decoy is not None:
            self.decoy.destroy()
            self.decoy = None
            self.cooldown_until = time.time() + COOLDOWN_SEC


if __name__ == "__main__":
    root = tk.Tk()
    GuardianApp(root)
    root.mainloop()
