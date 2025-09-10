"""
Eye Touch 主程序窗口
包含区域划分、眼动追踪显示、交互测试等功能
"""
import sys
import configparser
from typing import Optional
import numpy as np
import cv2

from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                           QFrame, QSplitter, QTextEdit, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QPixmap, QImage, QPainter, QPen, QBrush, QColor, QKeyEvent

from qfluentwidgets import (FluentWindow, FluentIcon, InfoBar, InfoBarPosition, setTheme, Theme,
                          PrimaryPushButton, PushButton, ToggleButton, CardWidget,
                          BodyLabel, CaptionLabel, setStyleSheet, TitleLabel)

from algorithm_interface import EyeTrackingInterface, RegionManager, GazePoint

class CameraWidget(QLabel):
    """摄像头显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        self.setText("摄像头未启动")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
    def update_frame(self, frame: np.ndarray, gaze_point: Optional[GazePoint] = None):
        """更新显示帧"""
        if frame is None:
            return
            
        # 转换为 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_frame.shape
        bytes_per_line = 3 * width
        
        # 创建 QImage
        q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        
        # 在图像上绘制视线点
        if gaze_point:
            painter = QPainter(q_image)
            pen = QPen(QColor(255, 0, 0), 3)
            painter.setPen(pen)
            painter.drawEllipse(int(gaze_point.screen_x - 10), 
                              int(gaze_point.screen_y - 10), 20, 20)
            painter.end()
        
        # 缩放到组件大小
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, 
                                    Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

class RegionGridWidget(QWidget):
    """区域网格显示组件"""
    
    region_entered = pyqtSignal(dict)  # 进入区域信号
    region_exited = pyqtSignal(dict)   # 退出区域信号
    
    def __init__(self, region_manager: RegionManager):
        super().__init__()
        self.region_manager = region_manager
        self.current_gaze_point = None
        self.setFixedSize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet("""
            RegionGridWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
    def update_gaze_point(self, gaze_point: Optional[GazePoint]):
        """更新视线点"""
        if gaze_point != self.current_gaze_point:
            self.current_gaze_point = gaze_point
            
            if gaze_point:
                # 更新当前区域
                old_region = self.region_manager.get_current_region()
                self.region_manager.update_current_region(gaze_point.screen_x, gaze_point.screen_y)
                new_region = self.region_manager.get_current_region()
                
                # 发出区域变化信号
                if old_region != new_region:
                    if old_region:
                        self.region_exited.emit(old_region)
                    if new_region:
                        self.region_entered.emit(new_region)
            
            self.update()
    
    def paintEvent(self, event):
        """绘制区域网格"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制区域网格
        regions = self.region_manager.get_regions()
        current_region = self.region_manager.get_current_region()
        
        for region in regions:
            # 缩放坐标到组件大小
            scale_x = self.width() / self.region_manager.screen_width
            scale_y = self.height() / self.region_manager.screen_height
            
            x = region['x'] * scale_x
            y = region['y'] * scale_y
            width = region['width'] * scale_x
            height = region['height'] * scale_y
            
            # 设置颜色
            if current_region and region['id'] == current_region['id']:
                # 当前区域高亮
                brush = QBrush(QColor(0, 123, 255, 100))
                pen = QPen(QColor(0, 123, 255), 3)
            else:
                # 普通区域
                brush = QBrush(QColor(240, 240, 240, 50))
                pen = QPen(QColor(200, 200, 200), 1)
            
            painter.setBrush(brush)
            painter.setPen(pen)
            painter.drawRect(int(x), int(y), int(width), int(height))
            
            # 绘制区域标签
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.drawText(int(x + width/2 - 30), int(y + height/2), region['name'])
        
        # 绘制视线点
        if self.current_gaze_point:
            scale_x = self.width() / self.region_manager.screen_width
            scale_y = self.height() / self.region_manager.screen_height
            
            gaze_x = self.current_gaze_point.screen_x * scale_x
            gaze_y = self.current_gaze_point.screen_y * scale_y
            
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawEllipse(int(gaze_x - 8), int(gaze_y - 8), 16, 16)

class StatusWidget(CardWidget):
    """状态信息显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(200)
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 标题
        title = BodyLabel("系统状态")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # 状态信息
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(150)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #f8f9fa;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
        
    def add_status_message(self, message: str):
        """添加状态消息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.status_text.append(formatted_message)
        
        # 保持最新消息可见
        from PyQt6.QtGui import QTextCursor
        self.status_text.moveCursor(QTextCursor.MoveOperation.End)
        
        # 限制消息数量（保留最后100行）
        document = self.status_text.document()
        if document.blockCount() > 100:
            cursor = self.status_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor, 10)
            cursor.removeSelectedText()

class ControlPanelWidget(CardWidget):
    """控制面板组件"""
    
    start_tracking = pyqtSignal()
    stop_tracking = pyqtSignal()
    start_calibration = pyqtSignal()
    clear_calibration = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(150)
        self.is_tracking = False
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 标题
        title = BodyLabel("控制面板")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 追踪控制按钮
        self.track_button = PrimaryPushButton("开始追踪")
        self.track_button.clicked.connect(self.toggle_tracking)
        button_layout.addWidget(self.track_button)
        
        # 校准按钮
        self.calibrate_button = PushButton("开始校准")
        self.calibrate_button.clicked.connect(self.start_calibration.emit)
        button_layout.addWidget(self.calibrate_button)
        
        # 清除校准按钮
        self.clear_button = PushButton("清除校准")
        self.clear_button.clicked.connect(self.clear_calibration.emit)
        button_layout.addWidget(self.clear_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def toggle_tracking(self):
        """切换追踪状态"""
        if self.is_tracking:
            self.stop_tracking.emit()
            self.track_button.setText("开始追踪")
            self.is_tracking = False
        else:
            self.start_tracking.emit()
            self.track_button.setText("停止追踪")
            self.is_tracking = True

class MainWindow(FluentWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.eye_tracker = EyeTrackingInterface()
        
        # 获取屏幕尺寸作为区域管理器的基础尺寸
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_size = screen.geometry()
        self.region_manager = RegionManager(screen_size.width(), screen_size.height(), 3, 3)  # 全屏尺寸和3x3网格
        
        self.init_ui()
        self.init_connections()
        self.setup_update_timer()
        
    def load_config(self) -> configparser.ConfigParser:
        """加载配置文件"""
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        return config
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle(self.config.get('SYSTEM', 'title', fallback='Eye Touch 眼动追踪系统'))
        
        # 设置主题
        setTheme(Theme.AUTO)
        
        # 添加标题
        self.create_title_area()
        
        # 创建主内容
        self.create_main_content()
        
        # 设置全屏且固定窗口比例（在所有组件创建后）
        self.setup_fullscreen_window()
    
    def setup_fullscreen_window(self):
        """设置全屏且固定窗口比例"""
        # 获取屏幕尺寸
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # 设置窗口为屏幕尺寸且不可调整
        self.setFixedSize(screen_geometry.size())
        self.move(0, 0)  # 移动到屏幕左上角
        
        # 禁用窗口的最大化按钮和调整大小功能
        # FluentWindow 的标题栏设置
        if hasattr(self.titleBar, 'maxBtn'):
            self.titleBar.maxBtn.setEnabled(False)
            self.titleBar.maxBtn.setVisible(False)
        
        # 禁用窗口调整大小
        self.setFixedSize(screen_geometry.size())
    
    def create_title_area(self):
        """创建标题区域"""
        # 在 FluentWindow 中添加标题
        title_widget = QWidget()
        title_widget.setObjectName("title_page")  # 设置对象名称
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(30, 20, 30, 10)
        
        # 主标题
        main_title = TitleLabel("Eye Touch 眼动追踪测试系统")
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(main_title)
        
        # 副标题
        sub_title = BodyLabel("为算法团队提供人机交互测试平台")
        sub_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_title.setStyleSheet("color: #8a8a8a; font-size: 14px;")
        title_layout.addWidget(sub_title)
        
        # 将标题区域添加到主窗口
        self.addSubInterface(title_widget, FluentIcon.HOME, "主页")
    
    def create_main_content(self):
        """创建主要内容区域"""
        # 创建主内容组件
        content_widget = QWidget()
        content_widget.setObjectName("tracking_page")  # 设置对象名称
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧面板
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # 右侧面板
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # 添加到窗口
        self.addSubInterface(content_widget, FluentIcon.CAMERA, "追踪测试")
        
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 摄像头显示
        camera_group = QGroupBox("摄像头预览")
        camera_layout = QVBoxLayout()
        self.camera_widget = CameraWidget()
        camera_layout.addWidget(self.camera_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)
        
        # 区域网格显示
        region_group = QGroupBox("区域划分显示")
        region_layout = QVBoxLayout()
        self.region_widget = RegionGridWidget(self.region_manager)
        region_layout.addWidget(self.region_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        return panel
        
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # 控制面板
        self.control_panel = ControlPanelWidget()
        layout.addWidget(self.control_panel)
        
        # 状态显示
        self.status_widget = StatusWidget()
        layout.addWidget(self.status_widget)
        
        layout.addStretch()
        return panel
    
    def init_connections(self):
        """初始化信号连接"""
        # 控制面板信号
        self.control_panel.start_tracking.connect(self.start_tracking)
        self.control_panel.stop_tracking.connect(self.stop_tracking)
        self.control_panel.start_calibration.connect(self.start_calibration)
        self.control_panel.clear_calibration.connect(self.clear_calibration)
        
        # 区域变化信号
        self.region_widget.region_entered.connect(self.on_region_entered)
        self.region_widget.region_exited.connect(self.on_region_exited)
        
    def setup_update_timer(self):
        """设置更新定时器"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(33)  # 30 FPS
        
    @pyqtSlot()
    def start_tracking(self):
        """开始眼动追踪"""
        if self.eye_tracker.initialize_camera():
            self.eye_tracker.start_tracking()
            self.status_widget.add_status_message("✅ 眼动追踪已启动")
        else:
            self.status_widget.add_status_message("❌ 摄像头初始化失败")
            InfoBar.error("错误", "无法初始化摄像头", duration=3000, parent=self)
    
    @pyqtSlot()
    def stop_tracking(self):
        """停止眼动追踪"""
        self.eye_tracker.stop_tracking()
        self.status_widget.add_status_message("⏹️ 眼动追踪已停止")
        
    @pyqtSlot()
    def start_calibration(self):
        """开始校准"""
        self.status_widget.add_status_message("🎯 开始校准流程")
        # TODO: 实现校准界面
        
    @pyqtSlot()
    def clear_calibration(self):
        """清除校准数据"""
        self.eye_tracker.clear_calibration()
        self.status_widget.add_status_message("🗑️ 校准数据已清除")
        
    @pyqtSlot(dict)
    def on_region_entered(self, region: dict):
        """处理进入区域事件"""
        self.status_widget.add_status_message(f"👁️ 进入 {region['name']}")
        
    @pyqtSlot(dict)
    def on_region_exited(self, region: dict):
        """处理退出区域事件"""
        self.status_widget.add_status_message(f"👋 离开 {region['name']}")
        
    def update_display(self):
        """更新显示"""
        # 更新摄像头画面
        current_frame = self.eye_tracker.get_current_frame()
        current_gaze = self.eye_tracker.get_current_gaze_point()
        
        if current_frame is not None:
            self.camera_widget.update_frame(current_frame, current_gaze)
        
        # 更新区域显示
        self.region_widget.update_gaze_point(current_gaze)
        
    def keyPressEvent(self, event: QKeyEvent):
        """键盘事件处理"""
        if event.key() == Qt.Key.Key_Escape:
            # Escape 键退出程序
            self.close()
        else:
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.eye_tracker.stop_tracking()
        event.accept()
