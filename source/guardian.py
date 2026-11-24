import threading
import time
import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np

# ===== 設定 =====
PROTOTXT = "models/MobileNetSSD_deploy.prototxt"
MODEL = "models/MobileNetSSD_deploy.caffemodel"
CONF_THRESHOLD = 0.5   # 辨識信心度門檻
PERSON_ID = 15         # person 的類別編號
LEFT_ZONE = 0.35
RIGHT_ZONE = 0.65
HITS_NEEDED = 2
COOLDOWN_SEC = 3       # 關閉假畫面後的冷卻秒數
FONT = "Microsoft JhengHei"
# ================


class GuardianApp:
    def __init__(self, root):
        self.root = root
        root.title("Smart Guardian Shield")
        root.geometry("320x270")
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

    # ---------- 假的「設定程式」畫面 ----------
    def show_decoy(self):
        win = tk.Toplevel(self.root)
        self.decoy = win
        win.title("System Configuration Utility")
        win.attributes("-fullscreen", True)
        win.attributes("-topmost", True)
        win.configure(bg="white")
        win.bind("<Escape>", lambda e: self.close_decoy())

        tk.Label(win, text="System Configuration Utility  v2.3",
                 font=(FONT, 20, "bold"), bg="#1f3a5f", fg="white",
                 anchor="w", padx=20).pack(fill="x", ipady=14)

        body = tk.Frame(win, bg="white")
        body.pack(fill="both", expand=True, padx=40, pady=20)

        tk.Label(body, text="Network Parameters", font=(FONT, 14, "bold"),
                 bg="white").grid(row=0, column=0, sticky="w", pady=6)
        form = [("Server Address", "192.168.10.25"),
                ("Port", "8080"),
                ("Timeout (sec)", "30"),
                ("Retry Count", "3")]
        for r, (name, val) in enumerate(form, start=1):
            tk.Label(body, text=name, font=(FONT, 11), bg="white").grid(
                row=r, column=0, sticky="w", pady=4)
            e = ttk.Entry(body, width=30)
            e.insert(0, val)
            e.grid(row=r, column=1, sticky="w", padx=20)

        tk.Label(body, text="Parameter Table", font=(FONT, 14, "bold"),
                 bg="white").grid(row=6, column=0, sticky="w", pady=(24, 6))
        tree = ttk.Treeview(body, columns=("p", "v", "s"),
                            show="headings", height=8)
        for col, title in (("p", "Parameter"), ("v", "Value"), ("s", "Status")):
            tree.heading(col, text=title)
            tree.column(col, width=220)
        rows = [("max_connections", "128", "OK"), ("buffer_size", "4096", "OK"),
                ("log_level", "INFO", "OK"), ("cache_ttl", "600", "OK"),
                ("compression", "enabled", "OK"), ("auto_update", "disabled", "OK")]
        for row in rows:
            tree.insert("", "end", values=row)
        tree.grid(row=7, column=0, columnspan=3, sticky="w")

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