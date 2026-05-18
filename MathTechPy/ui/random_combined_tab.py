"""随机抽人 — 六种模式合一"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QStackedWidget,
    QFrame, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
from core.random_engine import RandomEngine
from .random_tab import RandomTab
from .random_wheel_tab import RandomWheelTab
from .random_rolling_tab import RollingWheelTab
from .random_card_tab import CardTab
from .random_group_tab import GroupTab


class RandomCombinedTab(QWidget):
    """六种随机抽人模式整合在一个页面"""

    MODE_NAMES = [
        "🎲 弹跳",
        "🎡 转盘",
        "🎰 滚动轮盘",
        "🃏 翻牌",
        "📋 分组",
    ]

    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------- 模式切换栏 ----------
        bar = QFrame()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: #34495e;")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(14, 0, 14, 0)
        bar_layout.setSpacing(10)

        lbl = QLabel("🎯 抽人模式:")
        lbl.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: white; background: transparent;")
        bar_layout.addWidget(lbl)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(self.MODE_NAMES)
        self.combo_mode.setFont(QFont("Microsoft YaHei", 11))
        self.combo_mode.setMinimumWidth(160)
        self.combo_mode.setStyleSheet("""
            QComboBox {
                background: white; color: #2c3e50; border: none;
                border-radius: 8px; padding: 4px 12px;
            }
            QComboBox::drop-down {
                border: none; width: 24px;
            }
            QComboBox::down-arrow {
                image: none; border: none;
            }
            QComboBox QAbstractItemView {
                background: white; selection-background-color: #1abc9c;
                selection-color: white; border: none; padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px; border-radius: 6px;
            }
        """)
        self.combo_mode.currentIndexChanged.connect(self._switch_mode)
        bar_layout.addWidget(self.combo_mode)

        bar_layout.addStretch()

        self._mode_label = QLabel("")
        self._mode_label.setFont(QFont("Microsoft YaHei", 10))
        self._mode_label.setStyleSheet("color: #bdc3c7; background: transparent;")
        bar_layout.addWidget(self._mode_label)

        layout.addWidget(bar)

        # ---------- 内容区 ----------
        self._mode_index = 0
        self._modes = [
            RandomTab(dm, engine),
            RandomWheelTab(dm, engine),
            RollingWheelTab(dm, engine),
            CardTab(dm, engine),
            GroupTab(dm, engine),
        ]

        self.stack = QStackedWidget()
        for m in self._modes:
            self.stack.addWidget(m)
        layout.addWidget(self.stack, 1)

        self._update_label()

    def _switch_mode(self, idx: int):
        if idx == self._mode_index:
            return
        self._mode_index = idx
        self.stack.setCurrentIndex(idx)
        self._update_label()
        self._modes[idx].refresh()

    def _update_label(self):
        hints = [
            "名字在屏幕中碰撞弹跳",
            "彩色转盘旋转揭晓",
            "滚动轮盘旋转揭晓",
            "卡片翻牌揭晓结果",
            "全班随机分组展示",
        ]
        self._mode_label.setText(hints[self._mode_index])

    def refresh(self):
        self._modes[self._mode_index].refresh()
