"""随机抽人 — 翻牌（卡片网格，翻牌揭晓）"""
import math
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QListWidget, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QResizeEvent

from core.data_manager import DataManager
from core.random_engine import RandomEngine

CARD_BACK = "#2c3e50"
CARD_FRONT = "#ffffff"
CARD_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22",
               "#9b59b6", "#1abc9c", "#f39c12", "#e91e63"]


class CardWidget(QFrame):
    """单张卡片（显示名字的 QLabel 在中央）"""

    def __init__(self, name: str, color: str, parent=None):
        super().__init__(parent)
        self.name = name
        self.color = color
        self._face_up = False
        self.setObjectName("card")
        self.setMinimumSize(50, 36)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        self.label = QLabel("?")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Microsoft YaHei", 9, QFont.Weight.Bold))
        layout.addWidget(self.label)

        self._update_style()

    def set_card_size(self, w: int, h: int):
        self.setFixedSize(w, h)
        # 字号自适应
        fs = max(7, min(14, w // 8))
        self.label.setFont(QFont("Microsoft YaHei", fs, QFont.Weight.Bold))

    def _update_style(self):
        if self._face_up:
            self.label.setText(self.name)
            self.label.setStyleSheet("color: #2c3e50; background: transparent;")
            self.setStyleSheet(f"""
                QFrame#card {{
                    background: white; border: 3px solid {self.color};
                    border-radius: 10px;
                }}
            """)
        else:
            self.label.setText("?")
            self.label.setStyleSheet("color: white; background: transparent;")
            self.setStyleSheet(f"""
                QFrame#card {{
                    background: {self.color}; border: 2px solid #ecf0f1;
                    border-radius: 10px;
                }}
            """)

    def flip(self, revealed: bool):
        self._face_up = revealed
        self._update_style()

    def highlight(self, on: bool):
        if on:
            self.label.setStyleSheet("color: #f1c40f; font-weight: bold; background: transparent;")
            self.setStyleSheet(f"""
                QFrame#card {{
                    background: white; border: 4px solid #f1c40f;
                    border-radius: 10px;
                }}
            """)
        else:
            self._update_style()


class CardTab(QWidget):
    """翻牌随机抽人"""

    CARD_SPACING = 8

    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine
        self._is_rolling = False
        self._cards: list[CardWidget] = []
        self._highlight_idx = 0
        self._decel_step = 0
        self._card_w = 90
        self._card_h = 58
        self._cols = 8

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        left = QFrame()
        left.setStyleSheet("background: #f5f6fa;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(30, 18, 30, 18)
        left_layout.setSpacing(10)

        title = QLabel("🃏 翻 牌")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; letter-spacing: 4px; background: transparent;")
        left_layout.addWidget(title)

        self.status_label = QLabel("✨ 点「开始翻牌」抽取")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("color: #95a5a6; background: transparent;")
        left_layout.addWidget(self.status_label)

        # 卡片网格
        self.card_area = QFrame()
        self.card_area.setStyleSheet("background: transparent;")
        self.card_grid = QGridLayout(self.card_area)
        self.card_grid.setSpacing(self.CARD_SPACING)
        self.card_grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.card_area, 1)

        self.winner_label = QLabel("")
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.winner_label.setStyleSheet("color: #2c3e50; background: transparent; padding: 6px;")
        left_layout.addWidget(self.winner_label)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_roll = QPushButton("🚀  开 始 翻 牌")
        self.btn_roll.setMinimumSize(200, 52)
        self.btn_roll.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.btn_roll.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_start_style()
        self.btn_roll.clicked.connect(self.toggle_roll)
        btn_row.addWidget(self.btn_roll)
        btn_row.addSpacing(16)
        self.btn_reset = QPushButton("🔄 重置")
        self.btn_reset.setMinimumSize(100, 42)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton { background: white; color: #7f8c8d;
                border: 2px solid #dfe6e9; border-radius: 21px; font-size: 13px; }
            QPushButton:hover { border-color: #bdc3c7; color: #2c3e50; }
        """)
        self.btn_reset.clicked.connect(self.reset_history)
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch()
        left_layout.addLayout(btn_row)

        # 设置
        settings = QHBoxLayout()
        settings.addStretch()
        settings.addWidget(QLabel("每组"))
        self.spin_group = QSpinBox()
        self.spin_group.setRange(1, 10)
        self.spin_group.setValue(1)
        self.spin_group.setFixedWidth(50)
        self.spin_group.setStyleSheet("""
            QSpinBox { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px; font-size: 15px; font-weight: bold; color: #2c3e50; }
        """)
        settings.addWidget(self.spin_group)
        settings.addWidget(QLabel("人"))
        settings.addSpacing(16)
        self.chk_weight = QPushButton("⚖️ 权重优先")
        self.chk_weight.setCheckable(True)
        self.chk_weight.setChecked(True)
        self.chk_weight.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_weight.setStyleSheet("""
            QPushButton { background: white; border: 2px solid #dfe6e9;
                border-radius: 14px; padding: 4px 12px; font-size: 11px; color: #7f8c8d; }
            QPushButton:checked { background: #1abc9c; color: white; border-color: #1abc9c; }
        """)
        settings.addWidget(self.chk_weight)
        settings.addStretch()
        left_layout.addLayout(settings)

        layout.addWidget(left, 3)

        # 右侧：历史
        right = QFrame()
        right.setFixedWidth(260)
        right.setStyleSheet("background: white; border-left: 1px solid #ecf0f1;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(16, 20, 16, 20)
        right_layout.setSpacing(12)
        hist_header = QHBoxLayout()
        hist_title = QLabel("📋 抽选历史")
        hist_title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        hist_title.setStyleSheet("color: #2c3e50;")
        hist_header.addWidget(hist_title)
        hist_header.addStretch()
        self.hist_count = QLabel("0")
        self.hist_count.setFont(QFont("Microsoft YaHei", 11))
        self.hist_count.setStyleSheet("color: #95a5a6;")
        hist_header.addWidget(self.hist_count)
        right_layout.addLayout(hist_header)
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget { background: #fafafa; border: none; border-radius: 10px; padding: 6px; }
            QListWidget::item { background: white; border: 1px solid #ecf0f1;
                border-radius: 8px; padding: 10px 12px; margin: 2px 0;
                color: #2c3e50; font-size: 13px; }
            QListWidget::item:hover { background: #f0faf7; border-color: #1abc9c; }
        """)
        right_layout.addWidget(self.history_list)
        layout.addWidget(right)

        self.roll_timer = QTimer(self)
        self.roll_timer.timeout.connect(self._roll_tick)

    def _calc_card_size(self) -> tuple[int, int, int]:
        """根据可用宽度计算卡片尺寸和列数"""
        avail = self.card_area.width() - 20  # 留边距
        if avail < 200:
            cols = 4
        else:
            # 每张卡约 95px 宽，算列数
            cols = max(4, (avail + self.CARD_SPACING) // (95 + self.CARD_SPACING))
        card_w = (avail - self.CARD_SPACING * (cols - 1)) // cols
        card_w = max(50, min(card_w, 130))
        card_h = int(card_w * 0.64)
        card_h = max(36, card_h)
        return card_w, card_h, cols

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        # 窗口大小变化时重建卡片网格
        if self._cards:
            self._apply_card_layout()

    def _apply_card_layout(self):
        """根据当前窗口宽度重新布局卡片"""
        card_w, card_h, cols = self._calc_card_size()

        if cols == self._cols and card_w == self._card_w and card_h == self._card_h:
            return  # 没变化

        self._card_w, self._card_h, self._cols = card_w, card_h, cols

        # 清空网格并重新添加
        for i in reversed(range(self.card_grid.count())):
            self.card_grid.takeAt(0)

        for idx, card in enumerate(self._cards):
            card.set_card_size(card_w, card_h)
            self.card_grid.addWidget(card, idx // cols, idx % cols)

    def _rebuild_cards(self):
        """重建所有卡片"""
        while self.card_grid.count():
            item = self.card_grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
        self._cards = []

        students = self.dm.current_students
        if not students:
            return

        card_w, card_h, cols = self._calc_card_size()
        self._card_w, self._card_h, self._cols = card_w, card_h, cols

        for i, s in enumerate(students):
            card = CardWidget(s.name, CARD_COLORS[i % len(CARD_COLORS)])
            card.set_card_size(card_w, card_h)
            card.flip(False)
            self._cards.append(card)
            self.card_grid.addWidget(card, i // cols, i % cols)

    def _set_start_style(self):
        self.btn_roll.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1abc9c, stop:1 #16a085);
                color: white; border: none; border-radius: 26px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1dd2af, stop:1 #1abc9c); }
        """)

    def _set_stop_style(self):
        self.btn_roll.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #e74c3c, stop:1 #c0392b);
                color: white; border: none; border-radius: 26px; }
        """)

    def toggle_roll(self):
        if not self._is_rolling:
            self._start_roll()
        else:
            self._stop_roll()

    def _start_roll(self):
        students = self.dm.current_students
        if not students:
            QMessageBox.warning(self, "错误", "当前班级没有学生数据")
            return
        self._rebuild_cards()
        if not self._cards:
            QMessageBox.warning(self, "错误", "没有可用的卡片")
            return

        self._is_rolling = True
        self._highlight_idx = 0
        self._decel_step = 0
        self.winner_label.setText("")
        self.btn_roll.setText("⏹  停  止")
        self._set_stop_style()
        self.status_label.setText("🎰 翻牌中...")
        self.roll_timer.start(60)

    def _stop_roll(self):
        self._is_rolling = False
        self.status_label.setText("🎯 即将揭晓...")

    def _roll_tick(self):
        students = self.dm.current_students
        if not students:
            return
        if not self._cards:
            self.roll_timer.stop()
            return

        if self._is_rolling:
            # 快速轮转高亮
            prev = self._highlight_idx
            self._highlight_idx = (self._highlight_idx + 1) % len(self._cards)
            if prev < len(self._cards):
                self._cards[prev].highlight(False)
            if self._highlight_idx < len(self._cards):
                self._cards[self._highlight_idx].highlight(True)
        else:
            # 减速阶段
            self._decel_step += 1
            interval = 2 + self._decel_step // 4
            if self._decel_step % interval == 0:
                prev = self._highlight_idx
                self._highlight_idx = (self._highlight_idx + 1) % len(self._cards)
                if prev < len(self._cards):
                    self._cards[prev].highlight(False)
                if self._highlight_idx < len(self._cards):
                    self._cards[self._highlight_idx].highlight(True)

            if self._decel_step >= 24:
                self.roll_timer.stop()
                for c in self._cards:
                    c.highlight(False)
                self._do_pick(students)

    def _do_pick(self, students):
        if not students or not self._cards:
            return

        # 高亮停的位置就是中奖者
        winner_idx = self._highlight_idx
        if winner_idx >= len(self._cards):
            return
        winner_card = self._cards[winner_idx]
        winner_name = winner_card.name

        # 找到对应的 StudentData
        winner_stu = None
        for s in students:
            if s.name == winner_name:
                winner_stu = s
                break
        if winner_stu is None:
            return

        # 更新 callCount
        new_count = self.dm.update_call_count(self.dm.current_class, winner_stu.id)
        winner_stu.call_count = new_count

        # 同步引擎历史
        engine_history = self.engine._get_history()
        engine_history.append(winner_stu.id)

        # 只翻开中奖者的卡片
        for c in self._cards:
            c.flip(c.name == winner_name)

        self.winner_label.setText(f"🎉 {winner_name}")
        self.status_label.setText(f"🎉 {winner_name}  ·  第{winner_stu.call_count}次被抽中")
        self.btn_roll.setText("🚀  开 始 翻 牌")
        self._set_start_style()

        self.history_list.insertItem(0, f"{winner_name}  ·  第{winner_stu.call_count}次")
        self.hist_count.setText(str(self.history_list.count()))

    def reset_history(self):
        self.engine.reset_history()
        self.history_list.clear()
        self.hist_count.setText("0")
        self.winner_label.setText("")
        self.status_label.setText("✨ 点「开始翻牌」抽取")
        for c in self._cards:
            c.flip(False)
            c.highlight(False)

    def refresh(self):
        self._rebuild_cards()
        self.winner_label.setText("")
        self.status_label.setText("✨ 点「开始翻牌」抽取")
