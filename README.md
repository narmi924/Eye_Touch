 # Eye Touch - 眼动追踪和视线估计系统

一个用于验证眼动追踪算法的人机交互测试系统，采用现代化的 Fluent Design 界面风格。

## 🎯 项目概述

Eye Touch 是为算法团队的眼动追踪研究设计的测试系统，提供：

- **区域识别与判定**: 屏幕区域划分和视线区域判定
- **交互测试功能**: 多种测试场景验证算法准确性
- **实时视觉反馈**: 摄像头预览和视线轨迹显示
- **数据记录与分析**: 测试结果记录和统计分析

## 🏗️ 技术架构

- **开发语言**: Python 3.7+
- **UI框架**: PyQt6 + PyQt-Fluent-Widgets
- **图像处理**: OpenCV
- **数据处理**: NumPy, Pandas
- **配置管理**: ConfigParser

## 📁 项目结构

```
Eye_Touch/
├── app.py                      # 主程序入口
├── main_window.py              # 主窗口界面
├── welcome_window.py           # 欢迎窗口
├── algorithm_interface.py      # 算法接口模块
├── interaction_test.py         # 交互测试模块
├── config.ini                  # 配置文件
├── requirements.txt            # 依赖包列表
├── run.py                      # 快速启动脚本
├── 技术架构建议.md             # 技术文档
└── README.md                   # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 Python 3.7 或更高版本：

```bash
python --version
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv eye_touch_env

# 激活虚拟环境 (Windows)
eye_touch_env\\Scripts\\activate

# 激活虚拟环境 (macOS/Linux)
source eye_touch_env/bin/activate
```

### 3. 安装依赖

**方法一：全部一键安装（推荐）**
```bash
pip install -r requirements.txt
```

**方法二：部分手动安装（如果上述代码报错）**
```bash
pip install PyQt6>=6.4.0
pip install "PyQt6-Fluent-Widgets[full]>=1.3.0" -i https://pypi.org/simple/
pip install -r requirements.txt
```

**注意**：必须使用 `PyQt6-Fluent-Widgets[full]` 完整版本，它包含了所有必要的依赖组件（如 `PyQt6-Frameless-Window`）。

### 4. 运行程序

#### 方法一：使用快速启动脚本
```bash
python run.py
```

#### 方法二：直接运行主程序
```bash
python app.py
```

## 🎮 功能使用

### 界面特色

🌟 **现代化 Fluent Design 界面**
- 采用微软 Fluent Design 设计语言
- 无边框亚克力玻璃质感欢迎窗口
- 现代化导航界面和卡片式布局
- 完整的 Fluent Design 组件体系
- 优雅的 InfoBar 提示替代传统消息框

### 主要界面说明

1. **欢迎窗口** (550×450)
   - 🪟 **FramelessWindow** 无边框亚克力效果
   - 📊 **TitleLabel** 和 **SubtitleLabel** 标题组件
   - 🖱️ 自动支持窗口拖拽（通过 TitleBar）
   - ⏱️ 程序启动时自动显示，3秒后自动进入主界面
   - ⌨️ 按空格键快速跳过

2. **主界面** (全屏显示)
   - 🖥️ **FluentWindow** 全屏显示，固定窗口比例
   - 🔒 **窗口控制**: 只能最小化或关闭，无法调整大小
   - 🧭 **导航界面**: 主页 + 追踪测试页面
   - 📱 **左侧面板**: 摄像头预览 + 区域划分显示
   - 🎛️ **右侧面板**: 控制面板 + 状态信息
   - ⌨️ **Escape键**: 退出程序

3. **Fluent Design 组件**
   - **PrimaryPushButton**: 主要操作按钮（开始追踪、校准等）
   - **CardWidget**: 卡片式组件容器
   - **BodyLabel** 和 **CaptionLabel**: 标准文本标签
   - **InfoBar**: 优雅的通知提示框
   - **TitleBar**: 自定义标题栏，支持拖拽

### 区域测试功能

系统提供两种主要的交互测试：

#### 1. 区域停留测试
- 测试用户是否能准确注视指定区域
- 可设置停留时间要求
- 实时显示进度和反馈

#### 2. 目标选择测试
- 按顺序选择多个目标区域
- 测试选择准确性和速度
- 记录完整的选择轨迹

## ⚙️ 配置说明

编辑 `config.ini` 文件可调整系统参数：

```ini
[SYSTEM]
title = Eye Touch 眼动追踪系统
window_width = 1200        # 主窗口宽度
window_height = 800        # 主窗口高度
welcome_width = 550        # 欢迎窗口宽度
welcome_height = 450       # 欢迎窗口高度
acrylic_enabled = true     # 启用亚克力效果
acrylic_opacity = 48       # 亚克力透明度 (0-255)

[CAMERA]
device_id = 0          # 摄像头设备ID
fps = 30              # 帧率
resolution_width = 640 # 分辨率宽度
resolution_height = 480 # 分辨率高度

[REGIONS]
grid_rows = 3         # 区域网格行数
grid_cols = 3         # 区域网格列数
calibration_points = 9 # 校准点数量
```

## 🔌 算法接口说明

为算法团队预留的主要接口：

### EyeTrackingInterface 类

```python
class EyeTrackingInterface:
    def initialize_camera() -> bool:
        # 初始化摄像头
    
    def _preprocess_frame(frame) -> np.ndarray:
        # TODO: 算法团队实现视频预处理
    
    def _detect_pupil(frame) -> PupilData:
        # TODO: 算法团队实现瞳孔检测
    
    def _estimate_gaze(pupil_data) -> GazePoint:
        # TODO: 算法团队实现视线估计
```

### 数据结构

```python
@dataclass
class PupilData:
    center_x: float    # 瞳孔中心X坐标
    center_y: float    # 瞳孔中心Y坐标
    radius: float      # 瞳孔半径
    confidence: float  # 检测置信度
    timestamp: float   # 时间戳

@dataclass
class GazePoint:
    screen_x: float    # 屏幕坐标X
    screen_y: float    # 屏幕坐标Y
    confidence: float  # 估计置信度
    timestamp: float   # 时间戳
```

## 📊 测试数据导出

系统支持将测试结果导出为CSV格式：

```python
test_manager.export_results("test_results.csv")
```

导出的数据包括：
- 测试类型
- 成功率
- 准确率
- 耗时统计
- 时间戳

## 🔧 开发说明

### 为算法团队集成新功能

1. **修改 `algorithm_interface.py`**：
   - 实现 `_preprocess_frame()` 方法
   - 实现 `_detect_pupil()` 方法
   - 实现 `_estimate_gaze()` 方法

2. **添加新的测试场景**：
   - 在 `interaction_test.py` 中创建新的测试类
   - 继承基础测试接口
   - 实现特定的测试逻辑

3. **调整界面布局**：
   - 修改 `main_window.py` 中的界面组件
   - 添加新的控制按钮或显示组件

### 扩展功能建议

- [ ] 添加眼动轨迹记录和回放
- [ ] 实现更多测试场景（路径追踪、速度测试等）
- [ ] 添加数据可视化图表
- [ ] 支持多用户测试数据管理
- [ ] 集成机器学习模型评估工具

## ❗ 常见问题

### Q: 虚拟环境中程序无窗口显示
A: 这是最常见的问题，解决方案：
1. **使用正确的 Fluent Widgets 版本**：
   ```bash
   pip install "PyQt6-Fluent-Widgets[full]>=1.3.0" -i https://pypi.org/simple/
   ```
2. **或运行修复脚本**：
   ```bash
   install_correct.bat
   ```
3. **确认安装了 PyQt6-Frameless-Window**：这是关键依赖组件

### Q: 程序启动失败
A: 请检查：
1. Python 版本是否为 3.7+
2. 是否在虚拟环境中运行
3. 依赖包是否正确安装（特别是完整版 Fluent Widgets）

### Q: 摄像头无法初始化
A: 请确认：
1. 摄像头是否被其他程序占用
2. 检查 config.ini 中的 device_id 设置
3. 确认摄像头权限已开启

### Q: 界面显示异常
A: 尝试：
1. 更新显卡驱动
2. 检查屏幕缩放设置
3. 重新安装 PyQt6 和 Fluent Widgets

## 👥 贡献指南

1. Fork 本项目
2. 创建功能分支
3. 提交代码更改
4. 发起 Pull Request

## 📄 许可证

本项目仅供学术研究使用，请勿用于商业用途。

---

**联系方式**: Imranjan Mamtimin
**版本**: v1.0
**最后更新**: 2025年9月10日
