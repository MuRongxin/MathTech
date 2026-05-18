"""随机抽人 — 分组抽取（真正抽取，而非全班 shuffle）"""
import math
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QListWidget, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
from core.random_engine import RandomEngine

GROUP_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22",
                "#9b59b6", "#1abc9c", "#f39c12", "#e91e63", "#00bcd4", "#ff5722"]


class GroupPanel(QFrame):
    """分组面板"""

    def __init__(self, gid: int, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("gpanel")
        self.setStyleSheet(f"""
            QFrame#gpanel {{
                background: white; border: 2px solid {color};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        header = QLabel(f"第 {gid + 1} 组")
        header.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        layout.addWidget(header)

        self.members_label = QLabel("")
        self.members_label.setFont(QFont("Microsoft YaHei", 11))
        self.members_label.setStyleSheet("color: #2c3e50; background: transparent; border: none;")
        self.members_label.setWordWrap(True)
        layout.addWidget(self.members_label)


class GroupTab(QWidget):
    """分组抽取 — 抽取 N 组 × M 人，真正使用 RandomEngine"""

    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(12)

        title = QLabel("📋 分组抽取")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; letter-spacing: 4px;")
        layout.addWidget(title)

        self.status_label = QLabel("设置分组参数，点击「抽取分组」")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("color: #95a5a6;")
        layout.addWidget(self.status_label)

        # 控制区
        ctrl = QHBoxLayout()
        ctrl.addStretch()

        ctrl.addWidget(QLabel("分为"))
        self.spin_groups = QSpinBox()
        self.spin_groups.setRange(2, 20)
        self.spin_groups.setValue(4)
        self.spin_groups.setFixedWidth(50)
        self.spin_groups.setStyleSheet("""
            QSpinBox { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px; font-size: 15px; font-weight: bold; color: #2c3e50; }
        """)
        ctrl.addWidget(self.spin_groups)
        ctrl.addWidget(QLabel("组"))

        ctrl.addSpacing(16)

        ctrl.addWidget(QLabel("每组"))
        self.spin_group_size = QSpinBox()
        self.spin_group_size.setRange(1, 15)
        self.spin_group_size.setValue(4)
        self.spin_group_size.setFixedWidth(50)
        self.spin_group_size.setStyleSheet("""
            QSpinBox { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px; font-size: 15px; font-weight: bold; color: #2c3e50; }
        """)
        ctrl.addWidget(self.spin_group_size)
        ctrl.addWidget(QLabel("人"))

        ctrl.addSpacing(8)

        self.chk_weight = QPushButton("⚖️ 权重优先")
        self.chk_weight.setCheckable(True)
        self.chk_weight.setChecked(True)
        self.chk_weight.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_weight.setStyleSheet("""
            QPushButton { background: white; border: 2px solid #dfe6e9;
                border-radius: 14px; padding: 4px 12px; font-size: 11px; color: #7f8c8d; }
            QPushButton:checked { background: #1abc9c; color: white; border-color: #1abc9c; }
        """)
        ctrl.addWidget(self.chk_weight)

        ctrl.addSpacing(12)

        self.btn_pick = QPushButton("🎯 抽取分组")
        self.btn_pick.setMinimumSize(140, 42)
        self.btn_pick.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.btn_pick.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_pick.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1abc9c, stop:1 #16a085);
                color: white; border: none; border-radius: 21px; }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1dd2af, stop:1 #1abc9c); }
        """)
        self.btn_pick.clicked.connect(self.pick_and_group)
        ctrl.addWidget(self.btn_pick)

        ctrl.addStretch()
        layout.addLayout(ctrl)

        # 分组展示区
        self.group_area = QFrame()
        self.group_area.setStyleSheet("background: transparent;")
        self.group_grid = QGridLayout(self.group_area)
        self.group_grid.setSpacing(14)
        self.group_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.group_area, 1)

        # 历史 / 提示区
        self.info_label = QLabel("")
        self.info_label.setFont(QFont("Microsoft YaHei", 10))
        self.info_label.setStyleSheet("color: #7f8c8d; padding: 4px 0;")
        layout.addWidget(self.info_label)

    def pick_and_group(self):
        students = self.dm.current_students
        if not students:
            self.status_label.setText("当前班级没有学生数据")
            return

        n_total = len(students)
        n_groups = self.spin_groups.value()
        n_per_group = self.spin_group_size.value()
        need = n_groups * n_per_group

        if need > n_total:
            QMessageBox.information(
                self, "提示",
                f"共 {n_total} 人，{n_groups}组×{n_per_group}人需要 {need} 人，\n"
                f"超出班级人数，自动调整为 {n_groups}组×{n_total // n_groups} 人"
            )
            n_per_group = n_total // n_groups
            need = n_groups * n_per_group
            if n_per_group < 1:
                n_per_group = 1
                n_groups = n_total
                need = n_total

        use_weight = self.chk_weight.isChecked()

        try:
            results = self.engine.pick(group_size=need, use_weight=use_weight)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"抽选失败: {e}")
            return

        if not results:
            return

        picked = results  # List[RandomResult]

        # 更新 callCount
        for r in picked:
            new_count = self.dm.update_call_count(self.dm.current_class, r.student.id)
            r.student.call_count = new_count

        # 打乱后分配到各组
        names = [r.student.name for r in picked]
        random.shuffle(names)

        groups = [[] for _ in range(n_groups)]
        for i, name in enumerate(names):
            groups[i % n_groups].append(name)

        # 清除旧面板
        for i in reversed(range(self.group_grid.count())):
            w = self.group_grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        cols = min(4, n_groups)
        for gid, members in enumerate(groups):
            panel = GroupPanel(gid, GROUP_COLORS[gid % len(GROUP_COLORS)])
            panel.members_label.setText("\n".join(f"  • {m}" for m in members))
            self.group_grid.addWidget(panel, gid // cols, gid % cols)

        sizes = [len(g) for g in groups]
        self.status_label.setText(
            f"🎉 共抽取 {len(picked)} 人，分为 {n_groups} 组"
        )
        self.info_label.setText(
            f"已抽 | 每组 {min(sizes)}~{max(sizes)} 人 | "
            f"{'⚖️权重优先' if use_weight else '🎲纯随机'} | "
            f"新周期: {'是' if any(r.is_new_cycle for r in picked) else '否'}"
        )

    def refresh(self):
        """初始化/切换回来时清空分组面板"""
        self.status_label.setText("设置分组参数，点击「抽取分组」")
        self.info_label.setText("")
        for i in reversed(range(self.group_grid.count())):
            w = self.group_grid.itemAt(i).widget()
            if w:
                w.deleteLater()
