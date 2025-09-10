#!/usr/bin/env python3
"""
Eye Touch 快速启动脚本
"""
import sys
import subprocess
import os

def check_venv():
    """检查是否在虚拟环境中运行"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    if not check_venv():
        print("⚠️  建议在虚拟环境中运行此程序")
        print("创建虚拟环境: python -m venv eye_touch_env")
        print("激活虚拟环境: eye_touch_env\\Scripts\\activate")
        print("安装依赖: pip install -r requirements.txt")
        
    try:
        # 尝试导入必要的依赖
        import PyQt6
        from qfluentwidgets import FluentIcon
        print("✅ 依赖检查通过，启动 Eye Touch...")
        
        # 运行主程序
        from app import main as run_app
        run_app()
        
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

