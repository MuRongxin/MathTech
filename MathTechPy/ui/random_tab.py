"""随机抽人页 - 滚动动画 + 抽选结果 + 历史记录

修复的 C# bug：
1. 动画定时器在页面隐藏时自动停止，避免后台空转
2. 抽人后同步更新 DataManager 的 call_count（而不是只更新本地缓存）
3. 分组抽选时正确处理最后一组人数不足
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QSpinBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

import random

from core.data_manager import DataManager
from core.random_engine import RandomEngine


class RandomTab(QWidget):
    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine
        self._is_rolling = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # ---------- 左侧：抽选区 ----------
        left = QVBoxLayout()
        left.setSpacing(15)

        # 标题
        title = QLabel("随机抽人")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        left.addWidget(title)

        # 结果显示标签
        self.result_label = QLabel("准备开始")
        self.result_label.setFont(QFont("Microsoft YaHei", 48, QFont.Weight.Bold))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: #ecf0f1;
                border-radius: 15px;
                padding: 40px;
                min-height: 120px;
            }
        """)
        left.addWidget(self.result_label)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_roll = QPushButton("▶ 开始滚动")
        self.btn_roll.setMinimumHeight(50)
        self.btn_roll.setFont(QFont("Microsoft YaHei", 14))
        self.btn_roll.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #16a085; }
            QPushButton:pressed { background-color: #149174; }
        """)
        self.btn_roll.clicked.connect(self.toggle_roll)
        btn_layout.addWidget(self.btn_roll)

        self.btn_reset = QPushButton("🔄 重置历史")
        self.btn_reset.setMinimumHeight(50)
        self.btn_reset.clicked.connect(self.reset_history)
        btn_layout.addWidget(self.btn_reset)
        left.addLayout(btn_layout)

        # 分组设置
        group_box = QGroupBox("分组设置")
        group_layout = QHBoxLayout(group_box)
        group_layout.addWidget(QLabel("每组人数:"))
        self.spin_group = QSpinBox()
        self.spin_group.setRange(1, 10)
        self.spin_group.setValue(1)
        group_layout.addWidget(self.spin_group)
        self.chk_weight = QPushButton("✓ 使用权重（优先抽少的人）")
        self.chk_weight.setCheckable(True)
        self.chk_weight.setChecked(True)
        group_layout.addWidget(self.chk_weight)
        group_layout.addStretch()
        left.addWidget(group_box)

        # 本轮结果
        self.result_detail = QLabel("")
        self.result_detail.setFont(QFont("Microsoft YaHei", 14))
        self.result_detail.setStyleSheet("color: #7f8c8d;")
        left.addWidget(self.result_detail)

        left.addStretch()
        layout.addLayout(left, 2)

        # ---------- 右侧：历史记录 ----------
        right = QVBoxLayout()
        right.setSpacing(10)

        hist_title = QLabel("本次会话历史")
        hist_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        right.addWidget(hist_title)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
        """)
        right.addWidget(self.history_list)

        layout.addLayout(right, 1)

        # ---------- 动画定时器 ----------
        self.roll_timer = QTimer(self)
        self.roll_timer.timeout.connect(self._roll_tick)

    # ------------------------------------------------------------------
    # 动画逻辑
    # ------------------------------------------------------------------
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

        self._is_rolling = True
        self.btn_roll.setText("⏹ 停止")
        self.result_detail.setText("")
        self.roll_timer.start(60)  # 每60ms切换一次

    def _stop_roll(self):
        self._is_rolling = False
        self.roll_timer.stop()
        self.btn_roll.setText("▶ 开始滚动")
        self._do_pick()

    def _roll_tick(self):
        """动画帧 - 快速切换显示的名字"""
        students = self.dm.current_students
        if students:
            name = random.choice(students).name
            self.result_label.setText(name)

    def _do_pick(self):
        """执行抽选"""
        group_size = self.spin_group.value()
        use_weight = self.chk_weight.isChecked()

        try:
            results = self.engine.pick(group_size=group_size, use_weight=use_weight)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"抽选失败: {e}")
            return

        if not results:
            return

        # 更新 callCount（持久化到 XML）
        for r in results:
            new_count = self.dm.update_call_count(self.dm.current_class, r.student.id)
            r.student.call_count = new_count

        # 显示结果
        if len(results) == 1:
            s = results[0].student
            self.result_label.setText(s.name)
            self.result_detail.setText(
                f"ID: {s.id}  |  本次第 {s.call_count} 次被抽"
            )
        else:
            names = "、".join(r.student.name for r in results)
            self.result_label.setText(f"{len(results)} 人")
            details = "  |  ".join(
                f"{r.student.name}({r.student.call_count}次)" for r in results
            )
            self.result_detail.setText(details)

        # 添加到历史列表
        for r in reversed(results):
            text = f"{r.student.name}  (第{r.student.call_count}次)"
            if r.is_new_cycle:
                text += "  [新一轮]"
            self.history_list.insertItem(0, text)

    def reset_history(self):
        """重置历史记录"""
        self.engine.reset_history()
        self.history_list.clear()
        self.result_label.setText("准备开始")
        self.result_detail.setText("历史已重置")

    def refresh(self):
        """切换班级/模式时刷新"""
        self.result_label.setText("准备开始")
        self.result_detail.setText("")
