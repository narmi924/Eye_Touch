"""
Eye Touch 交互测试模块
提供各种交互测试场景来验证眼动追踪算法
"""
import time
import random
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QProgressBar, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QPainter, QPen, QBrush, QColor

from qfluentwidgets import (CardWidget, BodyLabel, CaptionLabel, 
                          PrimaryPushButton, PushButton, InfoBar, 
                          InfoBarPosition)

from algorithm_interface import GazePoint

class TestType(Enum):
    """测试类型枚举"""
    REGION_DWELL = "区域停留测试"
    TARGET_SELECTION = "目标选择测试"
    PATH_TRACKING = "路径追踪测试"
    SPEED_ACCURACY = "速度精度测试"

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_type: TestType
    success: bool
    duration: float
    accuracy: float
    target_region: Optional[Dict]
    actual_regions: List[Dict]
    timestamp: float

class RegionDwellTest(QWidget):
    """区域停留测试"""
    
    test_completed = pyqtSignal(TestResult)
    
    def __init__(self, target_region: Dict, dwell_time: float = 2.0):
        super().__init__()
        self.target_region = target_region
        self.dwell_time = dwell_time
        self.start_time = None
        self.dwell_start_time = None
        self.is_in_target = False
        self.test_active = False
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 测试说明
        self.instruction_label = BodyLabel(f"请注视 {self.target_region['name']} 区域 {self.dwell_time} 秒")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instruction_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(int(self.dwell_time * 100))
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = CaptionLabel("等待开始...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_progress)
        
    def start_test(self):
        """开始测试"""
        self.test_active = True
        self.start_time = time.time()
        self.status_label.setText("测试进行中...")
        self.update_timer.start(10)  # 10ms 更新一次
        
    def stop_test(self):
        """停止测试"""
        self.test_active = False
        self.update_timer.stop()
        
    def update_gaze_point(self, gaze_point: Optional[GazePoint], current_region: Optional[Dict]):
        """更新视线点信息"""
        if not self.test_active:
            return
            
        # 检查是否在目标区域内
        in_target = (current_region is not None and 
                    current_region['id'] == self.target_region['id'])
        
        if in_target and not self.is_in_target:
            # 进入目标区域
            self.is_in_target = True
            self.dwell_start_time = time.time()
            self.status_label.setText("✅ 进入目标区域，保持注视...")
            
        elif not in_target and self.is_in_target:
            # 离开目标区域
            self.is_in_target = False
            self.dwell_start_time = None
            self.status_label.setText("❌ 离开目标区域，请重新注视")
            self.progress_bar.setValue(0)
            
    def update_progress(self):
        """更新进度"""
        if not self.test_active:
            return
            
        if self.is_in_target and self.dwell_start_time:
            elapsed = time.time() - self.dwell_start_time
            progress = min(elapsed / self.dwell_time, 1.0)
            self.progress_bar.setValue(int(progress * self.progress_bar.maximum()))
            
            if progress >= 1.0:
                # 测试完成
                self.complete_test(True)
        
        # 检查超时
        if self.start_time and (time.time() - self.start_time) > 30:  # 30秒超时
            self.complete_test(False)
            
    def complete_test(self, success: bool):
        """完成测试"""
        self.stop_test()
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        accuracy = 1.0 if success else 0.0
        
        result = TestResult(
            test_type=TestType.REGION_DWELL,
            success=success,
            duration=total_duration,
            accuracy=accuracy,
            target_region=self.target_region,
            actual_regions=[self.target_region] if success else [],
            timestamp=time.time()
        )
        
        self.status_label.setText("✅ 测试完成！" if success else "❌ 测试失败")
        self.test_completed.emit(result)

class TargetSelectionTest(QWidget):
    """目标选择测试"""
    
    test_completed = pyqtSignal(TestResult)
    
    def __init__(self, regions: List[Dict], num_targets: int = 5):
        super().__init__()
        self.regions = regions
        self.num_targets = num_targets
        self.current_target_index = 0
        self.target_sequence = []
        self.selected_regions = []
        self.test_active = False
        self.start_time = None
        
        self.init_ui()
        self.generate_target_sequence()
        
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout()
        
        # 测试说明
        self.instruction_label = BodyLabel(f"按顺序选择 {self.num_targets} 个目标区域")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.instruction_label)
        
        # 当前目标显示
        self.current_target_label = BodyLabel("")
        self.current_target_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_target_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4;")
        layout.addWidget(self.current_target_label)
        
        # 进度显示
        self.progress_label = CaptionLabel("")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        self.setLayout(layout)
        
    def generate_target_sequence(self):
        """生成目标序列"""
        self.target_sequence = random.sample(self.regions, min(self.num_targets, len(self.regions)))
        
    def start_test(self):
        """开始测试"""
        self.test_active = True
        self.start_time = time.time()
        self.current_target_index = 0
        self.selected_regions.clear()
        self.update_display()
        
    def stop_test(self):
        """停止测试"""
        self.test_active = False
        
    def update_display(self):
        """更新显示"""
        if self.current_target_index < len(self.target_sequence):
            current_target = self.target_sequence[self.current_target_index]
            self.current_target_label.setText(f"目标: {current_target['name']}")
            self.progress_label.setText(f"进度: {self.current_target_index + 1} / {len(self.target_sequence)}")
        else:
            self.current_target_label.setText("测试完成！")
            
    def update_gaze_point(self, gaze_point: Optional[GazePoint], current_region: Optional[Dict]):
        """更新视线点信息"""
        if not self.test_active or self.current_target_index >= len(self.target_sequence):
            return
            
        if current_region:
            target_region = self.target_sequence[self.current_target_index]
            
            if current_region['id'] == target_region['id']:
                # 选择正确
                self.selected_regions.append(current_region)
                self.current_target_index += 1
                
                if self.current_target_index >= len(self.target_sequence):
                    # 所有目标完成
                    self.complete_test()
                else:
                    self.update_display()
                    
    def complete_test(self):
        """完成测试"""
        self.stop_test()
        
        total_duration = time.time() - self.start_time if self.start_time else 0
        accuracy = len(self.selected_regions) / len(self.target_sequence)
        success = accuracy == 1.0
        
        result = TestResult(
            test_type=TestType.TARGET_SELECTION,
            success=success,
            duration=total_duration,
            accuracy=accuracy,
            target_region=None,
            actual_regions=self.selected_regions,
            timestamp=time.time()
        )
        
        self.test_completed.emit(result)

class InteractionTestManager:
    """交互测试管理器"""
    
    def __init__(self, regions: List[Dict]):
        self.regions = regions
        self.test_results = []
        self.current_test = None
        
    def create_region_dwell_test(self, target_region: Dict, dwell_time: float = 2.0) -> RegionDwellTest:
        """创建区域停留测试"""
        test = RegionDwellTest(target_region, dwell_time)
        test.test_completed.connect(self.on_test_completed)
        return test
        
    def create_target_selection_test(self, num_targets: int = 5) -> TargetSelectionTest:
        """创建目标选择测试"""
        test = TargetSelectionTest(self.regions, num_targets)
        test.test_completed.connect(self.on_test_completed)
        return test
        
    def on_test_completed(self, result: TestResult):
        """测试完成处理"""
        self.test_results.append(result)
        print(f"测试完成: {result.test_type.value}")
        print(f"成功: {result.success}, 准确率: {result.accuracy:.2%}, 耗时: {result.duration:.2f}秒")
        
    def get_test_statistics(self) -> Dict:
        """获取测试统计信息"""
        if not self.test_results:
            return {}
            
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.success)
        avg_accuracy = sum(r.accuracy for r in self.test_results) / total_tests
        avg_duration = sum(r.duration for r in self.test_results) / total_tests
        
        return {
            'total_tests': total_tests,
            'success_rate': successful_tests / total_tests,
            'average_accuracy': avg_accuracy,
            'average_duration': avg_duration,
            'results': self.test_results
        }
        
    def export_results(self, filename: str = "test_results.csv"):
        """导出测试结果到CSV文件"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['test_type', 'success', 'duration', 'accuracy', 'timestamp']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in self.test_results:
                writer.writerow({
                    'test_type': result.test_type.value,
                    'success': result.success,
                    'duration': result.duration,
                    'accuracy': result.accuracy,
                    'timestamp': result.timestamp
                })
        
        print(f"测试结果已导出到: {filename}")
