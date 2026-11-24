import tkinter as tk
from dashboard import draw_dashboard

root = tk.Tk()
root.attributes("-fullscreen", True)
W = root.winfo_screenwidth()
H = root.winfo_screenheight()

canvas = tk.Canvas(root, width=W, height=H, bg="#F3F2F1", highlightthickness=0)
canvas.pack(fill="both", expand=True)
draw_dashboard(canvas, W, H)

root.bind("<Escape>", lambda e: root.destroy())
root.mainloop()