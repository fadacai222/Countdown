import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
import threading
import ctypes
import sys
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

# DPI适配
ctypes.windll.shcore.SetProcessDpiAwareness(1)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_TIME = "22:30"  # 默认阶段一时间
DEFAULT_DAY = 7  # 默认阶段二日期


def get_next_time(target_time_str):
    now = datetime.now()
    target = datetime.strptime(target_time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day
    )
    if now >= target:
        target += timedelta(days=1)
    return target


def get_next_day(day):
    now = datetime.now()
    if now.day > day:
        month = now.month + 1 if now.month < 12 else 1
        year = now.year + 1 if month == 1 else now.year
    else:
        month = now.month
        year = now.year
    return datetime(year=year, month=month, day=day)


def calculate_month_progress(start_day):
    now = datetime.now()
    current = datetime(year=now.year, month=now.month, day=start_day)
    if now.day < start_day:
        prev_month = current - timedelta(days=30)
        current = datetime(year=prev_month.year, month=prev_month.month, day=start_day)
    next_point = get_next_day(start_day)
    total = (next_point - current).total_seconds()
    elapsed = (now - current).total_seconds()
    progress = max(0, min(1, elapsed / total))
    return round(progress * 100, 2)


class SubWindow(tk.Toplevel):
    def __init__(self, root, time_point, day_point):
        super().__init__(root)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.wm_attributes("-transparentcolor", "black")
        self.configure(bg="black")

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"220x120+{sw - 230}+{sh - 160}")

        self.label1 = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label1.pack(pady=5)

        self.label2 = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label2.pack(pady=5)

        self.label3 = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label3.pack(pady=5)

        self.time_point = time_point
        self.day_point = day_point
        self.update_labels()

    def update_labels(self):
        now = datetime.now()
        next_time = get_next_time(self.time_point)
        time_left = str(next_time - now).split(".")[0]

        next_day = get_next_day(self.day_point)
        days_left = (next_day.date() - now.date()).days

        progress = calculate_month_progress(self.day_point)

        self.label1.configure(text=f"🕒 阶段一剩余：{time_left}")
        self.label2.configure(text=f"💰 阶段二预计：{days_left} 天")
        self.label3.configure(text=f"📈 本阶段进度：{progress}%")
        self.after(1000, self.update_labels)


class CountdownApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("任务跟踪")
        self.geometry("400x360")
        self.protocol("WM_DELETE_WINDOW", self.hide_window)

        self.time_point = DEFAULT_TIME
        self.day_point = DEFAULT_DAY

        self.create_widgets()
        self.sub_gui = None
        self.spawn_sub()
        self.update_labels()

        self.icon = self.create_tray_icon()
        threading.Thread(target=self.icon.run, daemon=True).start()

    def create_widgets(self):
        self.label_time = ctk.CTkLabel(self, text="", font=("Arial", 15))
        self.label_time.pack(pady=8)

        self.label_cd = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label_cd.pack(pady=5)

        self.label_day = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label_day.pack(pady=5)

        self.label_progress = ctk.CTkLabel(self, text="", font=("Arial", 13))
        self.label_progress.pack(pady=5)

        ctk.CTkLabel(self, text="阶段一时间 (HH:MM)").pack(pady=4)
        self.entry_time = ctk.CTkEntry(self, placeholder_text=self.time_point)
        self.entry_time.pack()

        ctk.CTkLabel(self, text="阶段二日期 (1-31)").pack(pady=4)
        self.entry_day = ctk.CTkEntry(self, placeholder_text=str(self.day_point))
        self.entry_day.pack()

        ctk.CTkButton(self, text="保存设定", command=self.save_settings).pack(pady=12)

    def update_labels(self):
        now = datetime.now()
        self.label_time.configure(text="现在时间：" + now.strftime("%I:%M:%S %p"))

        next_time = get_next_time(self.time_point)
        self.label_cd.configure(
            text=f"阶段一剩余：{str(next_time - now).split('.')[0]}"
        )

        next_day = get_next_day(self.day_point)
        self.label_day.configure(
            text=f"阶段二预计：{(next_day.date() - now.date()).days} 天"
        )

        progress = calculate_month_progress(self.day_point)
        self.label_progress.configure(text=f"本阶段进度：{progress}%")

        self.after(1000, self.update_labels)

    def save_settings(self):
        time_input = self.entry_time.get().strip()
        day_input = self.entry_day.get().strip()

        if time_input:
            try:
                datetime.strptime(time_input, "%H:%M")
                self.time_point = time_input
            except ValueError:
                print("时间格式错误")

        if day_input.isdigit() and 1 <= int(day_input) <= 31:
            self.day_point = int(day_input)

        if self.sub_gui:
            self.sub_gui.destroy()
        self.spawn_sub()

    def spawn_sub(self):
        self.sub_gui = SubWindow(self, self.time_point, self.day_point)

    def hide_window(self):
        self.withdraw()

    def show_window(self, icon=None, item=None):
        self.deiconify()

    def quit_app(self, icon=None, item=None):
        self.icon.stop()
        self.destroy()
        sys.exit()

    def create_tray_icon(self):
        image = Image.new("RGB", (64, 64), color="black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill="blue")

        return Icon(
            "倒计时",
            image,
            menu=Menu(
                MenuItem("显示主界面", self.show_window),
                MenuItem("退出", self.quit_app),
            ),
        )


if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()
