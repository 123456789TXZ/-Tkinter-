import tkinter as tk
import ctypes
from PIL import Image, ImageTk
from win32gui import ReleaseCapture, SendMessage, GetParent
from win32con import WM_SYSCOMMAND, SC_MOVE, HTCAPTION


class CustomTitleBar:
    """自定义标题栏类 - 支持嵌入任何 Tk/Toplevel 窗口"""

    # Windows API 常量
    GWL_STYLE = -16
    GWLP_HWNDPARENT = -8
    WS_CAPTION = 0x00C00000
    WS_THICKFRAME = 0x00040000

    def __init__(
            self,
            master,
            title="自定义窗口",
            icon_path=None,
            bg_image_path=None,
            width=1200,
            height=850,
            title_color="red",
            title_font=("KaiTi", 20),
            bar_height=120,
            bar_bg="green"
    ):
        """
        初始化自定义标题栏

        Args:
            master: Tk 或 Toplevel 实例
            title: 窗口标题
            icon_path: 窗口图标路径
            bg_image_path: 标题栏背景图片路径
            width: 窗口宽度
            height: 窗口高度
            title_color: 标题文字颜色
            title_font: 标题文字字体
            bar_height: 标题栏高度
            bar_bg: 标题栏背景色
        """
        self.master = master
        self.title = title
        self.icon_path = icon_path
        self.bg_image_path = bg_image_path
        self.width = width
        self.height = height
        self.title_color = title_color
        self.title_font = title_font
        self.bar_height = bar_height
        self.bar_bg = bar_bg

        # 窗口状态
        self.is_maximized = False

        # 构建UI
        self._setup_dpi()
        self._remove_titlebar()
        self._center_window()
        self._setup_icon()
        self._create_title_bar()
        self._create_main_frame()
        self._bind_drag()

    # ==================== 初始化方法 ====================

    def _setup_dpi(self):
        """设置 DPI 适配"""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            self.master.tk.call('tk', 'scaling', scale_factor / 75)
        except:
            pass  # 非 Windows 系统忽略

    def _remove_titlebar(self):
        """移除系统标题栏"""
        self.master.update_idletasks()
        hwnd = self._get_handle()
        style = ctypes.windll.user32.GetWindowLongPtrW(hwnd, self.GWL_STYLE)
        style &= ~(self.WS_CAPTION | self.WS_THICKFRAME)
        ctypes.windll.user32.SetWindowLongPtrW(hwnd, self.GWL_STYLE, style)

    def _get_handle(self):
        """获取窗口句柄"""
        GetWindowLongPtrW = ctypes.windll.user32.GetWindowLongPtrW
        return GetWindowLongPtrW(self.master.winfo_id(), self.GWLP_HWNDPARENT)

    def _center_window(self):
        """居中显示窗口"""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        self.master.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _setup_icon(self):
        """设置窗口图标"""
        if self.icon_path:
            try:
                icon_image = Image.open(self.icon_path)
                icon_image = icon_image.resize((80, 80), Image.Resampling.LANCZOS)
                large_icon = ImageTk.PhotoImage(icon_image)
                self.master.tk.call('wm', 'iconphoto', self.master._w, large_icon)
                self.master.icon_image = large_icon  # 防止垃圾回收
            except Exception as e:
                print(f"图标加载失败: {e}")

    # ==================== 标题栏构建 ====================

    def _create_title_bar(self):
        """创建自定义标题栏"""
        # 标题栏容器
        self.title_bar = tk.Frame(
            self.master,
            bg=self.bar_bg,
            height=self.bar_height,

            bd=0,
            highlightbackground='#202020',
            highlightthickness=0.5
        )
        self.title_bar.pack(fill='x')
        self.title_bar.pack_propagate(False)

        # 画布（用于绘制背景图片和元素）
        self.canvas = tk.Canvas(
            self.title_bar,
            highlightthickness=0,
            bg=self.bar_bg
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # 背景图片
        self._load_background()

        # 图标
        self._create_icon()

        # 标题文字
        self._create_title_text()

        # 窗口控制按钮
        self._create_control_buttons()

    def _load_background(self):
        """加载标题栏背景图片"""
        if self.bg_image_path:
            try:
                img = Image.open(self.bg_image_path)
                # 获取背景色用于提示框
                self.bg_color = img.getpixel((100, 100))
                self.bg_color_hex = f'#{self.bg_color[0]:02x}{self.bg_color[1]:02x}{self.bg_color[2]:02x}'

                print(self.width)

                # 调整图片大小
                img_resized = img.resize((self.width+100, self.bar_height), Image.Resampling.LANCZOS)
                self.bg_image = ImageTk.PhotoImage(img_resized)
                self.bg_item = self.canvas.create_image(
                    0, 0, anchor="nw", image=self.bg_image
                )
            except Exception as e:
                print(f"背景图片加载失败: {e}")

    def _create_icon(self):
        """创建窗口图标"""
        if self.icon_path:
            try:
                icon_img = Image.open(self.icon_path).resize((50, 50))
                self.icon_photo = ImageTk.PhotoImage(icon_img)
                self.icon_item = self.canvas.create_image(
                    10, (self.bar_height - 50) // 2, anchor="nw", image=self.icon_photo
                )
                # 图标提示
                self._add_tooltip(self.icon_item, "软件图标", tip_x=10, tip_y=-40)
            except Exception as e:
                print(f"图标加载失败: {e}")

    def _create_title_text(self):
        """创建标题文字"""
        self.title_item = self.canvas.create_text(
            75,
            self.bar_height // 2,
            text=self.title,
            fill=self.title_color,
            font=self.title_font,
            anchor="w"
        )

    def _create_control_buttons(self):
        """创建窗口控制按钮（最小化、最大化、关闭）"""
        btn_style = {
            'width': 5,
            'height': 2,
            'font': ('KaiTi', 12),
            'bg': '#F5F5F5',
            'fg': '#000000',
            'highlightthickness': 0,
            'bd': 0
        }

        # 关闭按钮
        self.close_btn = tk.Button(
            self.title_bar, text="✕", **btn_style,
            command=self.master.destroy
        )
        self.close_btn.pack(side='right', padx=(11, 11), pady=5)
        self._add_button_tooltip(
            self.close_btn, "关闭窗口", "关闭", "red", "✕", "#F5F5F5"
        )

        # 最大化/还原按钮
        self.max_btn = tk.Button(
            self.title_bar, text="□", **btn_style,
            command=self._toggle_maximize
        )
        self.max_btn.pack(side='right', padx=(11, 11), pady=5)
        self._add_button_tooltip(
            self.max_btn, "放大窗口", "放大", "yellow", "□", "#F5F5F5"
        )

        # 最小化按钮
        self.min_btn = tk.Button(
            self.title_bar, text="—", **btn_style,
            command=self._minimize
        )
        self.min_btn.pack(side='right', padx=(11, 11), pady=5)
        self._add_button_tooltip(
            self.min_btn, "缩小窗口", "缩小", "green", "—", "#F5F5F5"
        )

    # ==================== 窗口控制功能 ====================

    def _minimize(self):
        """最小化窗口"""
        self.master.wm_iconify()

    def _toggle_maximize(self):
        """切换最大化/还原"""
        if self.is_maximized:
            self._restore_window()
        else:
            self._maximize_window()

    def _maximize_window(self):
        """最大化窗口"""
        self.master.state("zoomed")
        self.is_maximized = True
        self.max_btn.config(text="❐", command=self._restore_window)
        self._update_tooltip_text(self.max_btn, "还原窗口", "还原")
        self._update_titlebar_layout(maximized=True)

    def _restore_window(self):
        """还原窗口"""
        self.master.state("normal")
        self.is_maximized = False
        self.max_btn.config(text="□", command=self._maximize_window)
        self._update_tooltip_text(self.max_btn, "放大窗口", "放大")
        self._update_titlebar_layout(maximized=False)

    def _update_titlebar_layout(self, maximized):
        """更新标题栏布局（最大化/还原时调整元素大小）"""
        # 可以在这里添加动态调整标题栏元素大小的逻辑
        # 目前只是示例，你可以根据需求自定义
        pass

    # ==================== 拖拽功能 ====================

    def _bind_drag(self):
        """绑定窗口拖拽"""
        def move(event):
            ReleaseCapture()
            SendMessage(
                GetParent(self.master.winfo_id()),
                WM_SYSCOMMAND,
                SC_MOVE + HTCAPTION,
                0
            )

        # 绑定到标题栏和画布
        for widget in [self.title_bar, self.canvas]:
            widget.bind("<B1-Motion>", move)

    # ==================== 主框架 ====================

    def _create_main_frame(self):
        """创建主内容框架"""
        self.main_frame = tk.Frame(
            self.master,
            highlightbackground='#202020',
            highlightthickness=0.5,
            bg='lightblue'
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))

    def get_main_frame(self):
        """获取主框架，用于放置内容"""
        return self.main_frame

    # ==================== 工具提示系统 ====================

    def _add_tooltip(self, canvas_item, text, tip_x=0, tip_y=0):
        """为画布元素添加提示"""
        tooltip = _CanvasToolTip(self.canvas, canvas_item, text, tip_x, tip_y)
        return tooltip

    def _add_button_tooltip(self, button, text, enter_text, enter_bg, leave_text, leave_bg):
        """为按钮添加提示"""
        tooltip = _ButtonToolTip(
            button, text, enter_text, enter_bg, leave_text, leave_bg
        )
        return tooltip

    def _update_tooltip_text(self, button, new_text, new_enter_text):
        """更新按钮提示文字（用于最大化/还原切换）"""
        # 这里需要遍历按钮的绑定事件，更新 tooltip 实例
        # 简化方案：直接重新创建 tooltip（实际项目中可优化）
        pass


# ==================== 工具提示辅助类 ====================

class _CanvasToolTip:
    """画布元素工具提示"""
    def __init__(self, canvas, item, text, tip_x, tip_y):
        self.canvas = canvas
        self.item = item
        self.text = text
        self.tip_x = tip_x
        self.tip_y = tip_y
        self.tooltip_window = None

        self.canvas.tag_bind(self.item, '<Enter>', self.show)
        self.canvas.tag_bind(self.item, '<Leave>', self.hide)

    def show(self, event=None):
        if self.tooltip_window:
            return
        x = self.canvas.winfo_rootx() + self.tip_x
        y = self.canvas.winfo_rooty() + self.tip_y
        self.tooltip_window = tk.Toplevel(self.canvas)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f'+{x}+{y}')
        label = tk.Label(
            self.tooltip_window, text=self.text,
            background='lightyellow', borderwidth=1, relief='solid'
        )
        label.pack()

    def hide(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


class _ButtonToolTip:
    """按钮工具提示（支持悬停文字变化）"""
    def __init__(self, widget, text, enter_text, enter_bg, leave_text, leave_bg):
        self.widget = widget
        self.text = text
        self.enter_text = enter_text
        self.enter_bg = enter_bg
        self.leave_text = leave_text
        self.leave_bg = leave_bg
        self.tooltip_window = None

        self.widget.bind('<Enter>', self.on_enter)
        self.widget.bind('<Leave>', self.on_leave)

    def on_enter(self, event):
        self.widget.config(text=self.enter_text, bg=self.enter_bg)
        self._show_tooltip()

    def on_leave(self, event):
        self.widget.config(text=self.leave_text, bg=self.leave_bg)
        self._hide_tooltip()

    def _show_tooltip(self):
        if self.tooltip_window:
            return
        x = self.widget.winfo_rootx() + 5
        y = self.widget.winfo_rooty() - 35
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f'+{x}+{y}')
        label = tk.Label(
            self.tooltip_window, text=self.text,
            background='lightyellow', borderwidth=1, relief='solid'
        )
        label.pack()

    def _hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None