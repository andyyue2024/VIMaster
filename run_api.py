"""
API 服务启动脚本
"""
import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import run_api_server, FLASK_AVAILABLE


def main():
    parser = argparse.ArgumentParser(description="VIMaster API 服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=5000, help="监听端口")
    parser.add_argument("--debug", action="store_true", help="调试模式")

    args = parser.parse_args()

    if not FLASK_AVAILABLE:
        print("错误: Flask 不可用")
        print("请安装: pip install flask flask-cors")
        sys.exit(1)

    run_api_server(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
