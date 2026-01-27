"""
PC 客户端启动脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.desktop import run_desktop_app, PYQT_AVAILABLE


def main():
    if not PYQT_AVAILABLE:
        print("=" * 60)
        print("错误: PyQt6 不可用")
        print("=" * 60)
        print("\n请安装 PyQt6:")
        print("  pip install PyQt6")
        print("\n或者使用 Web 版:")
        print("  python run_web.py")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("🎯 VIMaster PC 客户端")
    print("=" * 60)
    print("正在启动...")

    run_desktop_app()


if __name__ == "__main__":
    main()
