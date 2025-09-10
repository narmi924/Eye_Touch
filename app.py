"""
Eye Touch 主程序入口
整合欢迎窗口和主窗口，处理程序启动流程
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from qfluentwidgets import setTheme, Theme

from welcome_window import WelcomeWindow
from main_window import MainWindow

class EyeTouchApp:
    """Eye Touch 应用程序主类"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome_window = None
        self.main_window = None
        
        # 设置应用程序属性
        self.app.setApplicationName("Eye Touch")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("UESTC")
        
        # 设置主题
        setTheme(Theme.AUTO)
        
    def run(self):
        """运行应用程序"""
        # 显示欢迎窗口
        self.show_welcome_window()
        
        # 启动事件循环
        return self.app.exec()
    
    def show_welcome_window(self):
        """显示欢迎窗口"""
        print("🚀 正在显示欢迎窗口...")
        self.welcome_window = WelcomeWindow()
        self.welcome_window.window_closed.connect(self.on_welcome_closed)
        self.welcome_window.show()
        print(f"👁️ 欢迎窗口已显示 (大小: {self.welcome_window.size().width()}x{self.welcome_window.size().height()})")
        print("💡 请在屏幕上查找欢迎窗口，或按空格键快速跳过")
    
    def on_welcome_closed(self):
        """欢迎窗口关闭后的处理"""
        if self.welcome_window:
            self.welcome_window.deleteLater()
            self.welcome_window = None
        
        # 显示主窗口
        self.show_main_window()
    
    def show_main_window(self):
        """显示主窗口"""
        print("🖥️ 正在显示主窗口...")
        self.main_window = MainWindow()
        self.main_window.show()
        print(f"✅ 主窗口已显示 (大小: {self.main_window.size().width()}x{self.main_window.size().height()})")
        print("💡 主窗口使用 FluentWindow 框架，包含导航界面")

def main():
    """主函数"""
    # 确保在正确的工作目录
    if os.path.exists('config.ini'):
        app = EyeTouchApp()
        return app.run()
    else:
        print("❌ 未找到配置文件 config.ini，请确保在正确的目录中运行程序")
        return 1

if __name__ == "__main__":
    sys.exit(main())
