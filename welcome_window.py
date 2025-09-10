"""
Eye Touch 用户欢迎窗口
采用 Fluent Design 风格，支持3秒自动跳过或空格键快速跳过
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QKeyEvent
from qfluentwidgets import (TitleLabel, SubtitleLabel, BodyLabel, FluentIcon, InfoBar, 
                          InfoBarPosition, setTheme, Theme, PrimaryPushButton, setStyleSheet)
from qfluentwidgets.components.widgets.frameless_window import FramelessWindow
from qframelesswindow import TitleBar

class WelcomeWindow(FramelessWindow):
    """欢迎窗口类"""
    
    # 信号：窗口关闭时发出
    window_closed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.apply_acrylic_effect()  # 先应用亚克力效果
        self.init_ui()
        self.init_timer()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Eye Touch - 眼动追踪系统")
        
        # 设置 Fluent Design 主题
        setTheme(Theme.AUTO)
        
        # 居中显示
        self.center_on_screen()
        
        # 创建主布局 - 参考登录窗口的布局方式
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 40, 50, 40)
        
        # 创建标题区域
        self.create_header_area(main_layout)
        
        # 创建进度区域
        self.create_progress_area(main_layout)
        
        # 创建操作提示区域
        self.create_hint_area(main_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
        
    def apply_acrylic_effect(self):
        """应用亚克力效果 - 参考成功系统的方式"""
        # 1. 设置自定义标题栏，这将自动启用无边框模式并接管窗口操作
        self.setTitleBar(TitleBar(self))
        self.titleBar.raise_()  # 将标题栏置于顶层

        # 2. 对窗口背景应用亚克力效果
        self.windowEffect.setAcrylicEffect(self.winId(), "F2F2F230")  # 30是透明度

        # 4. 固定窗口大小
        self.setFixedSize(550, 450)
        
        # 5. 确保窗口置顶和可见
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.raise_()
        self.activateWindow()
        
    def create_header_area(self, parent_layout):
        """创建标题区域 - 使用 Fluent Design 组件"""
        # 系统标题 - 使用 TitleLabel
        title_label = TitleLabel("Eye Touch")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 副标题 - 使用 SubtitleLabel
        subtitle_label = SubtitleLabel("眼动追踪和视线估计系统")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(title_label)
        parent_layout.addWidget(subtitle_label)
    
    def create_progress_area(self, parent_layout):
        """创建进度区域"""
        # 进度提示 - 使用 BodyLabel
        self.progress_label = BodyLabel("系统初始化中... 5秒后自动进入")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        parent_layout.addWidget(self.progress_label)
    
    def create_hint_area(self, parent_layout):
        """创建操作提示区域"""
        # 操作提示 - 使用较小的 BodyLabel
        action_hint = BodyLabel("按空格键快速跳过")
        action_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 设置较小的字体样式
        action_hint.setStyleSheet("""
            BodyLabel {
                font-size: 12px;
                color: #8a8a8a;
                font-style: italic;
            }
        """)
        
        parent_layout.addWidget(action_hint)
        
    def center_on_screen(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)
    
    def init_timer(self):
        """初始化定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
        # 设置倒计时 - 延长到5秒
        self.countdown = 5
        self.timer.start(1000)  # 每秒更新一次
        
    def update_countdown(self):
        """更新倒计时"""
        if self.countdown > 0:
            self.progress_label.setText(f"系统初始化中... {self.countdown}秒后自动进入")
            self.countdown -= 1
        else:
            self.timer.stop()
            self.close_window()
    
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Space:
            # 空格键快速跳过
            self.timer.stop()
            self.show_info_bar("快速跳过", "用户主动跳过欢迎界面")
            # 延迟一点时间显示提示信息
            QTimer.singleShot(500, self.close_window)
        else:
            super().keyPressEvent(event)
    
    def show_info_bar(self, title: str, content: str):
        """显示 InfoBar 提示"""
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=2000,
            parent=self
        )
    
    def close_window(self):
        """关闭窗口"""
        self.window_closed.emit()
        self.close()

def show_welcome_window():
    """显示欢迎窗口的便捷函数"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    welcome = WelcomeWindow()
    welcome.show()
    
    return welcome, app

if __name__ == "__main__":
    welcome, app = show_welcome_window()
    sys.exit(app.exec())
