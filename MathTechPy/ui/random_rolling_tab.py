"""随机抽人 — 滚动轮盘（轮盘旋转揭晓）"""
import math

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QPolygonF

from core.data_manager import DataManager
from core.random_engine import RandomEngine

WHEEL_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#e67e22",
                "#9b59b6", "#1abc9c", "#f39c12", "#e91e63"]


class RollingWheelWidget(QWidget):
    """滚动轮盘绘制组件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.names = []
        self.angle = 0.0
        self._highlights: set[int] = set()
        self.setMinimumSize(200, 200)

    def set_names(self, names):
        self.names = names
        self._highlights = set()
        self.update()

    def set_angle(self, angle):
        self.angle = angle % 360
        self.update()

    def set_highlights(self, indices):
        """按索引集合高亮（空集合即清除高亮）"""
        self._highlights = set(indices)
        self.update()

    def paintEvent(self, event):
        if not self.names:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        outer_r = min(cx, cy) - 16
        n = len(self.names)

        # 外圈（轮盘主体）
        painter.setPen(QPen(QColor("#34495e"), 4))
        painter.setBrush(QColor("#f5f6fa"))
        painter.drawEllipse(QPointF(cx, cy), outer_r, outer_r)

        # 内圈装饰
        inner_r = outer_r * 0.55
        painter.setPen(QPen(QColor("#bdc3c7"), 2))
        painter.setBrush(QColor("#ecf0f1"))
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

        # 名字所在半径
        name_r = (outer_r + inner_r) / 2

        # 根据人数自适应尺寸
        if n > 35:
            bw, bh, fs = 48, 22, 11
        elif n > 20:
            bw, bh, fs = 72, 26, 12
        else:
            bw, bh, fs = 96, 32, 14

        for i in range(n):
            angle_deg = i * 360 / n + self.angle
            qt_angle = math.radians(90 - angle_deg)
            px = cx + name_r * math.cos(qt_angle)
            py = cy - name_r * math.sin(qt_angle)

            is_win = (i in self._highlights)
            rect = QRectF(px - bw / 2, py - bh / 2, bw, bh)

            if is_win:
                painter.setPen(QPen(QColor("#f1c40f"), 3))
                painter.setBrush(QColor("#fffde7"))
            else:
                color = WHEEL_COLORS[i % len(WHEEL_COLORS)]
                painter.setPen(QPen(QColor(color), 1.5))
                painter.setBrush(Qt.GlobalColor.white)

            painter.drawRoundedRect(rect, 6, 6)

            # 名字缩略
            if n > 35:
                short = self.names[i][0]
            elif n > 20:
                short = self.names[i] if len(self.names[i]) <= 3 else self.names[i][:2] + "."
            else:
                short = self.names[i] if len(self.names[i]) <= 4 else self.names[i][:3] + "."
            painter.setPen(QColor("#2c3e50"))
            font = QFont("Microsoft YaHei", fs)
            font.setBold(is_win)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, short)

        # 右侧红色三角指针
        painter.setPen(QPen(QColor("#e74c3c"), 2))
        painter.setBrush(QColor("#e74c3c"))
        ptr = QPolygonF([
            QPointF(cx + outer_r - 10, cy),
            QPointF(cx + outer_r + 14, cy - 12),
            QPointF(cx + outer_r + 14, cy + 12),
        ])
        painter.drawPolygon(ptr)

        # 中心装饰圆
        painter.setPen(QPen(QColor("#2c3e50"), 2))
        painter.setBrush(QColor("#34495e"))
        painter.drawEllipse(QPointF(cx, cy), 16, 16)
        painter.setBrush(QColor("#1abc9c"))
        painter.drawEllipse(QPointF(cx, cy), 6, 6)


class RollingWheelTab(QWidget):
    """滚动轮盘抽人"""

    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine
        self._is_rolling = False
        self._speed = 0.0
        # 与 wheel.names 平行的学生 id 列表，用于按 id 定位高亮
        self._student_ids: list[int] = []

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------- 左侧：主区域 ----------
        left = QFrame()
        left.setStyleSheet("background: #f5f6fa;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(30, 18, 30, 18)
        left_layout.setSpacing(10)

        title = QLabel("🎰 滚动轮盘")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; letter-spacing: 4px; background: transparent;")
        left_layout.addWidget(title)

        self.status_label = QLabel("✨ 点「开始转动」")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("color: #95a5a6; background: transparent;")
        left_layout.addWidget(self.status_label)

        # 轮盘居中，自适应大小
        wheel_box = QHBoxLayout()
        wheel_box.addStretch()
        self.wheel = RollingWheelWidget()
        wheel_box.addWidget(self.wheel, 1)
        wheel_box.addStretch()
        left_layout.addLayout(wheel_box, 1)

        self.winner_label = QLabel("")
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.winner_label.setStyleSheet("color: #2c3e50; background: transparent; padding: 6px;")
        left_layout.addWidget(self.winner_label)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_roll = QPushButton("🚀  开 始 转 动")
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

        # ---------- 右侧：历史 ----------
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

        # ---------- 定时器 ----------
        self.roll_timer = QTimer(self)
        self.roll_timer.timeout.connect(self._roll_tick)

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

    def _set_wheel_students(self):
        """同步轮盘名字与平行的 id 列表"""
        students = self.dm.current_students
        self._student_ids = [s.id for s in students] if students else []
        self.wheel.set_names([s.name for s in students] if students else [])

    def _restore_idle(self):
        """恢复开始按钮与初始状态提示"""
        self.btn_roll.setText("🚀  开 始 转 动")
        self._set_start_style()
        self.status_label.setText("✨ 点「开始转动」")

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

        names = [s.name for s in students]
        self._student_ids = [s.id for s in students]
        self.wheel.set_names(names)
        self._is_rolling = True
        self._speed = 12.0
        self.winner_label.setText("")
        self.btn_roll.setText("⏹  停  止")
        self._set_stop_style()
        self.status_label.setText("🌀 转动中...")
        self.roll_timer.start(30)

    def _stop_roll(self):
        self._is_rolling = False
        self.status_label.setText("🎯 即将揭晓...")

    def _roll_tick(self):
        if not self.wheel.names:
            return

        if self._is_rolling:
            self.wheel.set_angle(self.wheel.angle + self._speed)
        else:
            # 减速
            self._speed *= 0.97
            self.wheel.set_angle(self.wheel.angle + self._speed)

            if self._speed < 0.15:
                self.roll_timer.stop()
                self._do_pick()

    def _do_pick(self):
        students = self.dm.current_students
        if not students or not self.wheel.names:
            self._restore_idle()
            return

        group_size = self.spin_group.value()
        use_weight = self.chk_weight.isChecked()
        try:
            results = self.engine.pick(group_size=group_size, use_weight=use_weight)
            if results:
                # 批量更新 call_count（内存同步 + 一次性写回 XML）
                self.dm.update_call_counts(
                    self.dm.current_class, [r.student.id for r in results]
                )
        except Exception as e:
            self._restore_idle()
            QMessageBox.critical(self, "错误", f"抽选失败: {e}")
            return

        if not results:
            self._restore_idle()
            return

        # 按 id 定位高亮（重名不误标；找不到则不高亮）
        highlight_idx = []
        for r in results:
            try:
                highlight_idx.append(self._student_ids.index(r.student.id))
            except ValueError:
                pass
        self.wheel.set_highlights(highlight_idx)

        winner_name = results[0].student.name
        self.winner_label.setText(f"🎉 {winner_name}")
        self.status_label.setText(f"🎉 {winner_name}  ·  第{results[0].student.call_count}次被抽中")
        self.btn_roll.setText("🚀  开 始 转 动")
        self._set_start_style()

        for r in reversed(results):
            prefix = "🔄 " if r.is_new_cycle else ""
            self.history_list.insertItem(0, f"{prefix}{r.student.name}  ·  第{r.student.call_count}次")
        # 历史保留最近 100 条，超出删最旧
        while self.history_list.count() > 100:
            self.history_list.takeItem(self.history_list.count() - 1)
        self.hist_count.setText(str(self.history_list.count()))

    def reset_history(self):
        self.engine.reset_history(self.dm.current_class)
        self.history_list.clear()
        self.hist_count.setText("0")
        self.winner_label.setText("")
        self._set_wheel_students()
        self.wheel.angle = 0.0
        self.wheel.update()
        self.status_label.setText("✨ 点「开始转动」")

    def stop_rolling(self):
        """强制停止转动并恢复按钮状态（切换模式/页签/班级时调用）"""
        if not self._is_rolling and not self.roll_timer.isActive():
            return
        self.roll_timer.stop()
        self._is_rolling = False
        self._speed = 0.0
        self._restore_idle()

    def refresh(self):
        self._set_wheel_students()
        self.wheel.angle = 0.0
        self.wheel.set_highlights([])
        self.wheel.update()
        self.winner_label.setText("")
        self.status_label.setText("✨ 点「开始转动」")
        # 清空右侧历史（引擎历史按班级隔离，由 reset_history 负责）
        self.history_list.clear()
        self.hist_count.setText("0")
