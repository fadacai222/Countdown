import tkinter as tk
from datetime import datetime, timedelta


class CountdownApp:
    def __init__(self, root):
        # 主GUI窗口
        self.root = root
        self.root.title("倒计时工具")
        self.root.geometry("350x300")  # 增加主窗口的高度，确保按钮不被遮挡
        self.root.config(bg="#f0f0f5")

        # 设置显示当前时间的标签
        self.current_time_label = tk.Label(
            root,
            text="当前时间: 00:00:00",
            font=("Segoe UI", 14),
            bg="#f0f0f5",
            fg="black",
        )
        self.current_time_label.pack(pady=10)

        # 设置显示倒计时的标签
        self.countdown_label = tk.Label(
            root,
            text="倒计时：00:00:00",
            font=("Segoe UI", 14),
            bg="#f0f0f5",
            fg="black",
        )
        self.countdown_label.pack(pady=10)

        # 输入目标时间选择
        self.time_input_label = tk.Label(
            root, text="选择下班时间：", bg="#f0f0f5", font=("Segoe UI", 12)
        )
        self.time_input_label.pack()

        # 创建时间选择框
        time_frame = tk.Frame(root, bg="#f0f0f5")
        time_frame.pack(pady=5)

        self.hour_var = tk.StringVar(value="10")  # 默认10点
        self.hour_dropdown = tk.OptionMenu(
            time_frame, self.hour_var, *[str(i).zfill(2) for i in range(1, 13)]
        )
        self.hour_dropdown.config(width=3, font=("Segoe UI", 12))
        self.hour_dropdown.grid(row=0, column=0, padx=5)

        self.minute_var = tk.StringVar(value="30")  # 默认30分钟
        self.minute_dropdown = tk.OptionMenu(
            time_frame, self.minute_var, *[str(i).zfill(2) for i in range(0, 60, 5)]
        )
        self.minute_dropdown.config(width=3, font=("Segoe UI", 12))
        self.minute_dropdown.grid(row=0, column=1, padx=5)

        self.am_pm_var = tk.StringVar(value="PM")  # 默认PM
        self.am_pm_dropdown = tk.OptionMenu(time_frame, self.am_pm_var, "AM", "PM")
        self.am_pm_dropdown.config(width=4, font=("Segoe UI", 12))
        self.am_pm_dropdown.grid(row=0, column=2, padx=5)

        # 启动倒计时按钮
        self.start_button = tk.Button(
            root,
            text="开始倒计时",
            font=("Segoe UI", 12),
            bg="#4CAF50",
            fg="white",
            command=self.start_countdown,
            relief="flat",
            width=15,
        )
        self.start_button.pack(pady=15)

        # 开关按钮，控制透明窗口的显示
        self.toggle_button = tk.Button(
            root,
            text="显示子GUI",
            font=("Segoe UI", 12),
            bg="#FF9800",
            fg="white",
            command=self.toggle_transp_window,
            relief="flat",
            width=15,
        )
        self.toggle_button.pack(pady=10)

        # 透明窗口
        self.create_transparent_window()

        # 更新当前时间
        self.update_current_time()

    def create_transparent_window(self):
        # 创建透明窗口来显示任务栏上的倒计时
        self.transp_root = tk.Toplevel(self.root)
        self.transp_root.geometry("350x80")
        self.transp_root.config(bg="black")
        self.transp_root.overrideredirect(True)  # 去除窗口的边框
        self.transp_root.attributes("-topmost", True)  # 确保窗口最上层
        self.transp_root.attributes("-transparentcolor", "black")  # 设置透明背景

        # 设置倒计时显示标签
        self.transp_countdown_label = tk.Label(
            self.transp_root,
            text="倒计时：00:00:00",
            font=("Microsoft YaHei", 12),
            bg="black",
            fg="#ffffff",
        )
        self.transp_countdown_label.pack(fill=tk.BOTH, expand=True)

        # 设置透明窗口的位置
        self.set_transp_position()

    def set_transp_position(self):
        # 获取屏幕大小
        screen_width = self.transp_root.winfo_screenwidth()
        screen_height = self.transp_root.winfo_screenheight()

        # 设置透明窗口位置在任务栏上方
        self.transp_root.geometry(
            f"250x50+{screen_width - 260}+{screen_height - 90}"
        )  # 定位窗口

    def update_current_time(self):
        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_time_label.config(text=f"当前时间: {current_time}")
        self.root.after(1000, self.update_current_time)  # 每秒更新当前时间

    def start_countdown(self):
        # 获取目标时间
        hour = int(self.hour_var.get())
        minute = int(self.minute_var.get())
        am_pm = self.am_pm_var.get()

        # 转换成24小时制
        if am_pm == "PM" and hour != 12:
            hour += 12
        if am_pm == "AM" and hour == 12:
            hour = 0

        # 计算目标时间
        target_time = datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        if target_time < datetime.now():
            target_time += timedelta(days=1)  # 如果目标时间已经过去，则推迟到第二天

        # 计算倒计时
        def update_timer():
            current_time = datetime.now()
            remaining_time = target_time - current_time

            if remaining_time.total_seconds() <= 0:
                self.countdown_label.config(text="目标时间已到！")
                self.transp_countdown_label.config(text="目标时间已到！")
            else:
                remaining_time_str = str(remaining_time).split(".")[0]  # 格式化倒计时
                self.countdown_label.config(text=f"倒计时: {remaining_time_str}")
                self.transp_countdown_label.config(text=f"倒计时: {remaining_time_str}")
                self.root.after(1000, update_timer)  # 每秒更新倒计时

        update_timer()

    def toggle_transp_window(self):
        # 切换透明窗口的显示状态
        if self.transp_root.winfo_viewable():
            self.transp_root.withdraw()  # 隐藏透明窗口
            self.toggle_button.config(text="显示子GUI")
        else:
            self.transp_root.deiconify()  # 显示透明窗口
            self.transp_root.lift()  # 手动提升窗口到最前
            self.toggle_button.config(text="隐藏子GUI")

    def on_minimize(self):
        # 最小化时让子GUI保持显示
        if self.transp_root.winfo_viewable():
            self.transp_root.lift()  # 将透明窗口置于最前
        else:
            self.transp_root.withdraw()


# 创建主窗口
root = tk.Tk()
app = CountdownApp(root)

root.protocol("WM_ICONIFY", app.on_minimize)
root.mainloop()
