"""Power BI 風格的假儀表板：全部用 Tkinter Canvas 畫出來，不需額外套件。"""
import ctypes
import tkinter as tk

# 讓 Windows 不要把視窗「放大」成模糊的低解析度畫面（高 DPI 螢幕必備）
# 注意：必須在建立任何 Tk 視窗之前執行，所以放在模組載入時
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# Power BI 常見配色
BG = "#F3F2F1"
CARD = "#FFFFFF"
BORDER = "#E1DFDD"
GRID = "#EDEBE9"
TEXT = "#252423"
SUB = "#605E5C"
TEAL = "#01B8AA"
DARK = "#374649"
RED = "#FD625E"
YELLOW = "#F2C811"
SKY = "#8AD4EB"
PALETTE = [TEAL, DARK, RED, YELLOW, SKY]
FONT = "Segoe UI"


def draw_dashboard(c, W, H):
    """在 Canvas c 上畫出 W x H 的儀表板。"""
    base = max(9, H // 90)  # 依螢幕高度決定基準字體大小
    s = H / 1080            # 以 1080p 為基準的縮放比例（線條粗細等用）

    def font(delta=0, bold=False):
        # 負數代表「像素」大小，不受 Windows 縮放設定影響，畫面才會清晰
        size = -int((base + delta) * 1.33)
        return (FONT, size, "bold") if bold else (FONT, size)

    def px(n):
        return max(1, int(round(n * s)))

    top_h = int(H * 0.045)
    nav_w = int(W * 0.03)
    pad = int(W * 0.012)

    # ---------- 頂部標題列 ----------
    c.create_rectangle(0, 0, W, top_h, fill=TEXT, outline="")
    c.create_rectangle(pad, top_h * 0.25, pad + top_h * 0.5, top_h * 0.75,
                       fill=YELLOW, outline="")
    c.create_text(pad + top_h * 0.8, top_h / 2, text="Sales Performance Dashboard",
                  anchor="w", fill="white", font=font(1))
    c.create_text(W - pad, top_h / 2, text="Last refresh: Today 09:15",
                  anchor="e", fill="#C8C6C4", font=font(-1))

    # ---------- 左側導覽列 ----------
    c.create_rectangle(0, top_h, nav_w, H, fill=CARD, outline=BORDER)
    icon = nav_w * 0.36
    for i in range(4):
        cy = top_h + pad * 2 + i * pad * 2.6
        color = YELLOW if i == 0 else "#C8C6C4"
        c.create_rectangle(nav_w / 2 - icon / 2, cy, nav_w / 2 + icon / 2,
                           cy + icon, fill=color, outline="")

    x0 = nav_w + pad
    x1 = W - pad
    cw = x1 - x0
    gap = pad

    # ---------- 標題與篩選器 ----------
    y = top_h + pad
    c.create_text(x0, y, text="Sales Overview", anchor="nw", fill=TEXT,
                  font=font(7, True))
    sx = x1
    for label in ("All Regions  \u25be", "FY2026  \u25be"):
        w = base * 11
        c.create_rectangle(sx - w, y, sx, y + base * 2.6, fill=CARD, outline=BORDER)
        c.create_text(sx - w / 2, y + base * 1.3, text=label, fill=SUB, font=font(-1))
        sx -= w + gap * 0.6

    # ---------- KPI 卡片 ----------
    ky0 = y + base * 4.6
    kh = H * 0.12
    kw = (cw - 3 * gap) / 4
    kpis = [
        ("Total Revenue", "$4.82M", "\u25b2 8.4% vs LY", TEAL),
        ("Orders", "12,486", "\u25b2 5.1% vs LY", TEAL),
        ("Avg Order Value", "$386", "\u25b2 3.2% vs LY", TEAL),
        ("Return Rate", "2.1%", "\u25bc 0.4% vs LY", RED),
    ]
    for i, (label, value, delta, color) in enumerate(kpis):
        kx = x0 + i * (kw + gap)
        c.create_rectangle(kx, ky0, kx + kw, ky0 + kh, fill=CARD, outline=BORDER)
        c.create_rectangle(kx, ky0, kx + px(4), ky0 + kh, fill=color, outline="")
        c.create_text(kx + pad, ky0 + kh * 0.22, text=label, anchor="w",
                      fill=SUB, font=font(-1))
        c.create_text(kx + pad, ky0 + kh * 0.55, text=value, anchor="w",
                      fill=TEXT, font=font(9, True))
        c.create_text(kx + pad, ky0 + kh * 0.85, text=delta, anchor="w",
                      fill=color, font=font(-2))

    # ---------- 共用：卡片外框 ----------
    def card(cx0, cy0, cx1, cy1, title):
        c.create_rectangle(cx0, cy0, cx1, cy1, fill=CARD, outline=BORDER)
        c.create_text(cx0 + pad * 0.8, cy0 + base * 1.5, text=title, anchor="w",
                      fill=TEXT, font=font(1, True))

    # ---------- 圖表列 ----------
    cy0 = ky0 + kh + gap
    ch = H * 0.30
    cy1 = cy0 + ch
    w1 = cw * 0.37
    w2 = cw * 0.37
    w3 = cw - w1 - w2 - 2 * gap
    bx0 = x0
    lx0 = bx0 + w1 + gap
    dx0 = lx0 + w2 + gap

    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]

    # 長條圖：每月營收
    card(bx0, cy0, bx0 + w1, cy1, "Revenue by Month ($K)")
    ax0 = bx0 + pad * 2.6
    ax1 = bx0 + w1 - pad
    ay0 = cy0 + base * 3.6
    ay1 = cy1 - base * 2.6
    vmax = 600
    for v in (0, 200, 400, 600):
        gy = ay1 - v / vmax * (ay1 - ay0)
        c.create_line(ax0, gy, ax1, gy, fill=GRID)
        c.create_text(ax0 - px(6), gy, text=str(v), anchor="e", fill=SUB, font=font(-3))
    bars = [310, 335, 360, 342, 388, 410, 395, 430, 418, 452, 470, 512]
    slot = (ax1 - ax0) / len(bars)
    bw = slot * 0.6
    for i, v in enumerate(bars):
        bx = ax0 + i * slot + (slot - bw) / 2
        by = ay1 - v / vmax * (ay1 - ay0)
        c.create_rectangle(bx, by, bx + bw, ay1,
                           fill=DARK if i == len(bars) - 1 else TEAL, outline="")
        c.create_text(bx + bw / 2, ay1 + base * 1.1, text=months[i],
                      fill=SUB, font=font(-3))

    # 折線圖：訂單趨勢
    card(lx0, cy0, lx0 + w2, cy1, "Orders Trend")
    ax0 = lx0 + pad * 2.8
    ax1 = lx0 + w2 - pad
    vmax = 1500
    for v in (0, 500, 1000, 1500):
        gy = ay1 - v / vmax * (ay1 - ay0)
        c.create_line(ax0, gy, ax1, gy, fill=GRID)
        c.create_text(ax0 - px(6), gy, text=f"{v:,}", anchor="e", fill=SUB, font=font(-3))
    step = (ax1 - ax0) / (len(months) - 1)
    series = [
        ([760, 790, 830, 820, 870, 900, 910, 940, 950, 980, 1010, 1060], SKY),
        ([820, 860, 910, 880, 950, 1010, 990, 1060, 1040, 1120, 1150, 1230], TEAL),
    ]
    for data, color in series:
        pts = []
        for i, v in enumerate(data):
            pts += [ax0 + i * step, ay1 - v / vmax * (ay1 - ay0)]
        c.create_line(*pts, fill=color, width=px(3))
        c.create_oval(pts[-2] - px(4), pts[-1] - px(4), pts[-2] + px(4), pts[-1] + px(4),
                      fill=color, outline="")
    for i, m in enumerate(months):
        c.create_text(ax0 + i * step, ay1 + base * 1.1, text=m, fill=SUB, font=font(-3))
    lgx = lx0 + w2 - pad * 5
    for j, (name, color) in enumerate((("2026", TEAL), ("2025", SKY))):
        c.create_rectangle(lgx + j * pad * 2.4, cy0 + base * 1.2,
                           lgx + j * pad * 2.4 + px(8), cy0 + base * 1.2 + px(8),
                           fill=color, outline="")
        c.create_text(lgx + j * pad * 2.4 + px(12), cy0 + base * 1.5, text=name,
                      anchor="w", fill=SUB, font=font(-2))

    # 甜甜圈圖：類別占比
    card(dx0, cy0, dx0 + w3, cy1, "Sales by Category")
    r = min(w3 * 0.22, (ch - base * 4) / 2)
    cx = dx0 + pad + r
    cy = (cy0 + base * 3 + cy1) / 2
    cats = [("Hardware", 38), ("Software", 27), ("Services", 21), ("Other", 14)]
    start = 90
    for i, (name, pct) in enumerate(cats):
        extent = -pct / 100 * 360
        c.create_arc(cx - r, cy - r, cx + r, cy + r, start=start, extent=extent,
                     fill=PALETTE[i], outline="white", width=px(2), style=tk.PIESLICE)
        start += extent
    hole = r * 0.55
    c.create_oval(cx - hole, cy - hole, cx + hole, cy + hole, fill=CARD, outline="")
    c.create_text(cx, cy, text="$4.82M", fill=TEXT, font=font(0, True))
    lx = cx + r + pad * 1.2
    for i, (name, pct) in enumerate(cats):
        ly = cy - r * 0.7 + i * base * 2.4
        c.create_rectangle(lx, ly - px(5), lx + px(10), ly + px(5), fill=PALETTE[i], outline="")
        c.create_text(lx + px(16), ly, text=f"{name}  {pct}%", anchor="w",
                      fill=SUB, font=font(-1))

    # ---------- 表格 ----------
    ty0 = cy1 + gap
    ty1 = H - pad
    card(x0, ty0, x1, ty1, "Top Products by Revenue")
    cols = [("Product", 0.02), ("Category", 0.32), ("Units", 0.52),
            ("Revenue", 0.70), ("Margin", 0.86)]
    hy = ty0 + base * 3.4
    rh = base * 2.4
    c.create_rectangle(x0 + 1, hy - rh / 2, x1 - 1, hy + rh / 2, fill=BG, outline="")
    for name, frac in cols:
        c.create_text(x0 + cw * frac, hy, text=name, anchor="w", fill=TEXT,
                      font=font(-1, True))
    rows = [
        ("Edge Gateway X200", "Hardware", "1,842", "$712,400", "32.1%"),
        ("Analytics Suite Pro", "Software", "1,206", "$598,300", "61.4%"),
        ("Sensor Pack S5", "Hardware", "3,410", "$455,900", "28.7%"),
        ("Cloud Monitoring", "Services", "2,975", "$401,200", "54.0%"),
        ("Camera Module C3", "Hardware", "2,230", "$368,700", "30.5%"),
        ("Support Plan Plus", "Services", "1,540", "$297,100", "58.2%"),
    ]
    ry = hy + rh
    for row in rows:
        if ry + rh / 2 > ty1 - 2:
            break
        c.create_line(x0 + 1, ry - rh / 2, x1 - 1, ry - rh / 2, fill=GRID)
        for (name, frac), value in zip(cols, row):
            c.create_text(x0 + cw * frac, ry, text=value, anchor="w",
                          fill=TEXT, font=font(-1))
        ry += rh
