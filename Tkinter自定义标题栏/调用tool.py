import tkinter as tk
from tool  import CustomTitleBar


# 主窗口
root = tk.Tk()

# 创建自定义标题栏
title_bar = CustomTitleBar(
    master=root,
    title="自定义标题栏【发挥你的想象，让tkinter变得更好】",
    icon_path="图标2.png",
    bg_image_path="标题栏背景2.jpg",
    width=1200,
    height=850,
    title_color="red",
    title_font=("KaiTi", 20),
    bar_height=120
)

# 获取主框架，添加你的内容
main_frame = title_bar.get_main_frame()

# ===== 在这里添加你的业务逻辑 =====
label = tk.Label(main_frame, text="欢迎使用！", font=("微软雅黑", 24), bg='lightblue')
label.pack(expand=True)

root.mainloop()