"""MathTech - Python Edition

纯桌面 PyQt6 版本，替代原有的 C# Avalonia + ASP.NET Core 架构。

用法:
    source ../.venv/bin/activate
    python main.py
"""
import sys
from pathlib import Path

# 确保能导入 core 和 ui
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
# 设置中文字体
plt.rcParams["font.sans-serif"] = ["Noto Serif CJK SC", "WenQuanYi Micro Hei", "AR PL UMing CN", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题

from ui import MainWindow


def main():
    # 启用高分屏支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    # 全局样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f6fa;
        }
        QWidget {
            font-family: "Microsoft YaHei", "PingFang SC", sans-serif;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
