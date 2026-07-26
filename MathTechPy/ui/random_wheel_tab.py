"""随机抽人 — 转盘风格"""
import math
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QFrame, QListWidget, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath

from core.data_manager import DataManager
from core.random_engine import RandomEngine

WHEEL_COLORS = [
    "#e74c3c", "#e67e22", "#f39c12", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#e91e63", "#00bcd4", "#ff5722",
    "#16a085", "#c0392b", "#8e44ad", "#2980b9", "#d35400",
    "#27ae60", "#f1c40f", "#1abc9c",
]


class WheelWidget(QWidget):
    """转盘绘制"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._students = []
        self._angle = 0.0
        # 抽中学生的 id 集合（按 id 高亮，重名不误标）
        self._highlights: set[int] = set()
        self._draw_text = True
        self.setMinimumSize(400, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        radius = min(cx, cy) - 30

        n = len(self._students)
        if n == 0:
            painter.setPen(QColor("#95a5a6"))
            painter.setFont(QFont("Microsoft YaHei", 14))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "无学生数据")
            return

        aps = 360.0 / n
        rect = QRectF(cx - radius, cy - radius, 2 * radius, 2 * radius)

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(n):
            color = QColor(WHEEL_COLORS[i % len(WHEEL_COLORS)])
            if self._students[i].id in self._highlights:
                color = color.lighter(130)
            painter.setBrush(QBrush(color))

            # 累计角度 round 取整，相邻扇区共享取整后的边界，消除 int() 截断缝隙
            qt_start = round((90 - (self._angle + i * aps)) * 16)
            qt_end = round((90 - (self._angle + (i + 1) * aps)) * 16)
            painter.drawPie(rect, qt_start, qt_end - qt_start)

        # 扇形分隔线
        painter.setPen(QPen(QColor("#ffffff"), 1.5))
        for i in range(n):
            seg_angle = math.radians(self._angle + i * aps - 90)
            ex = cx + math.cos(seg_angle) * radius
            ey = cy + math.sin(seg_angle) * radius
            painter.drawLine(cx, cy, round(ex), round(ey))

        # 文字
        if self._draw_text:
            for i in range(n):
                mid_deg = self._angle + i * aps + aps / 2
                mid_rad = math.radians(mid_deg - 90)

                text = self._students[i].name
                painter.save()
                painter.translate(cx, cy)

                angle_norm = mid_deg % 360
                if 90 < angle_norm < 270:
                    rot = mid_deg - 90 + 180
                    align = Qt.AlignmentFlag.AlignRight
                    tx = radius * 0.85
                else:
                    rot = mid_deg - 90
                    align = Qt.AlignmentFlag.AlignLeft
                    tx = radius * 0.18

                painter.rotate(rot)

                font_size = max(8, min(12, int(radius * 2 * 3.14 / n * 0.45)))
                painter.setFont(QFont("Microsoft YaHei", font_size))
                painter.setPen(QColor("#ffffff"))

                text_width = radius * 0.65
                painter.drawText(
                    int(tx), -7, int(text_width), 16,
                    align | Qt.AlignmentFlag.AlignVCenter, text
                )
                painter.restore()

        # 中心 hub
        hub_r = radius * 0.13
        painter.setBrush(QBrush(QColor("#2c3e50")))
        painter.setPen(QPen(QColor("#ecf0f1"), 2.5))
        painter.drawEllipse(QPointF(cx, cy), hub_r, hub_r)

        # 指针
        ptr_h = 18
        ptr_w = 14
        ptr_path = QPainterPath()
        ptr_path.moveTo(cx, cy - radius - ptr_h // 2)
        ptr_path.lineTo(cx - ptr_w, cy - radius + ptr_h)
        ptr_path.lineTo(cx + ptr_w, cy - radius + ptr_h)
        ptr_path.closeSubpath()
        painter.setBrush(QBrush(QColor("#e74c3c")))
        painter.setPen(QPen(QColor("#c0392b"), 2))
        painter.drawPath(ptr_path)

        # 外环
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#bdc3c7"), 3))
        painter.drawEllipse(QPointF(cx, cy), radius + 2, radius + 2)


class RandomWheelTab(QWidget):
    """转盘随机抽人"""

    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine
        self._is_rolling = False
        self._speed = 0.0
        self._angle = 0.0

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------- 左侧：转盘区域 ----------
        left = QFrame()
        left.setStyleSheet("background: #f5f6fa;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(30, 18, 30, 18)
        left_layout.setSpacing(8)

        title = QLabel("🎡 转 盘 抽 人")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; letter-spacing: 4px; background: transparent;")
        left_layout.addWidget(title)

        self.status_label = QLabel("✨ 点击「开始转动」")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("color: #95a5a6; background: transparent;")
        left_layout.addWidget(self.status_label)

        self.wheel = WheelWidget()
        left_layout.addWidget(self.wheel, 1)

        self.winner_label = QLabel("")
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        self.winner_label.setStyleSheet("color: #2c3e50; background: transparent; padding: 6px;")
        left_layout.addWidget(self.winner_label)

        # 按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_roll = QPushButton("🚀  开 始 转 动")
        self.btn_roll.setMinimumSize(180, 52)
        self.btn_roll.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.btn_roll.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_roll_btn_start()
        self.btn_roll.clicked.connect(self.toggle_roll)
        btn_row.addWidget(self.btn_roll)

        btn_row.addSpacing(16)

        self.btn_reset = QPushButton("🔄 重置")
        self.btn_reset.setMinimumSize(100, 42)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background: white; color: #7f8c8d;
                border: 2px solid #dfe6e9; border-radius: 21px; font-size: 13px;
            }
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
            QSpinBox {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px; font-size: 15px; font-weight: bold; color: #2c3e50;
            }
        """)
        settings.addWidget(self.spin_group)
        settings.addWidget(QLabel("人"))
        settings.addSpacing(16)

        self.chk_weight = QPushButton("⚖️ 权重优先")
        self.chk_weight.setCheckable(True)
        self.chk_weight.setChecked(True)
        self.chk_weight.setCursor(Qt.CursorShape.PointingHandCursor)
        self.chk_weight.setStyleSheet("""
            QPushButton {
                background: white; border: 2px solid #dfe6e9;
                border-radius: 14px; padding: 4px 12px; font-size: 11px; color: #7f8c8d;
            }
            QPushButton:checked {
                background: #1abc9c; color: white; border-color: #1abc9c;
            }
        """)
        settings.addWidget(self.chk_weight)
        settings.addStretch()
        left_layout.addLayout(settings)

        layout.addWidget(left, 3)

        # ---------- 右侧：历史记录 ----------
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
            QListWidget {
                background: #fafafa; border: none; border-radius: 10px; padding: 6px;
            }
            QListWidget::item {
                background: white; border: 1px solid #ecf0f1;
                border-radius: 8px; padding: 10px 12px; margin: 2px 0;
                color: #2c3e50; font-size: 13px;
            }
            QListWidget::item:hover { background: #f0faf7; border-color: #1abc9c; }
        """)
        right_layout.addWidget(self.history_list)
        layout.addWidget(right)

        # ---------- 动画定时器 ----------
        self.roll_timer = QTimer(self)
        self.roll_timer.timeout.connect(self._roll_tick)

    def _set_roll_btn_start(self):
        self.btn_roll.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1abc9c, stop:1 #16a085);
                color: white; border: none; border-radius: 26px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1dd2af, stop:1 #1abc9c);
            }
        """)

    def _set_roll_btn_stop(self):
        self.btn_roll.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white; border: none; border-radius: 26px;
            }
        """)

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
        self.wheel._students = students
        self.wheel._highlights = set()
        self._speed = 8 + random.uniform(2, 8)
        self.winner_label.setText("")
        n = len(students)
        self.wheel._draw_text = n <= 30

        self.btn_roll.setText("⏹  停  止")
        self._set_roll_btn_stop()
        self.status_label.setText("🎰 转动中...")
        self.roll_timer.start(28)

    def _stop_roll(self):
        self._is_rolling = False
        self.status_label.setText("🎯 即将揭晓...")

    def _roll_tick(self):
        if self._is_rolling:
            self._angle = (self._angle + self._speed) % 360
            self.wheel._angle = self._angle
            self.wheel.update()
        else:
            if self._speed > 0.05:
                self._speed *= 0.97
                self._angle = (self._angle + self._speed) % 360
                self.wheel._angle = self._angle
                self.wheel.update()
            else:
                self._speed = 0
                self.roll_timer.stop()
                self._do_pick()

    # ------------------------------------------------------------------
    # 抽取
    # ------------------------------------------------------------------
    def _restore_idle(self):
        """恢复开始按钮与初始状态提示"""
        self.btn_roll.setText("🚀  开 始 转 动")
        self._set_roll_btn_start()
        self.status_label.setText("✨ 点击「开始转动」")

    def _do_pick(self):
        students = self.dm.current_students
        if not students:
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

        # 按 id 高亮所有抽中者（重名不误标；不在名单内则不高亮）
        student_ids = {s.id for s in students}
        self.wheel._highlights = {r.student.id for r in results} & student_ids
        # 大班（>30 人）不绘制全部名字，与 _start_roll 的阈值逻辑一致
        self.wheel._draw_text = len(students) <= 30
        winner_name = results[0].student.name
        self.winner_label.setText(f"🎉 {winner_name}")
        self.status_label.setText("✨ 点击「开始转动」")
        self.btn_roll.setText("🚀  开 始 转 动")
        self._set_roll_btn_start()
        self.wheel.update()

        for r in reversed(results):
            prefix = "🔄 " if r.is_new_cycle else ""
            text = f"{prefix}{r.student.name}  ·  第{r.student.call_count}次"
            self.history_list.insertItem(0, text)
        # 历史保留最近 100 条，超出删最旧
        while self.history_list.count() > 100:
            self.history_list.takeItem(self.history_list.count() - 1)
        self.hist_count.setText(str(self.history_list.count()))

    def reset_history(self):
        self.engine.reset_history(self.dm.current_class)
        self.history_list.clear()
        self.hist_count.setText("0")
        self._angle = 0
        self.wheel._angle = 0
        self.wheel._highlights = set()
        self.winner_label.setText("")
        self.status_label.setText("✨ 点击「开始转动」")
        self.wheel.update()

    def stop_rolling(self):
        """强制停止转动并恢复按钮状态（切换模式/页签/班级时调用）"""
        if not self._is_rolling and not self.roll_timer.isActive():
            return
        self.roll_timer.stop()
        self._is_rolling = False
        self._speed = 0.0
        self._restore_idle()

    def refresh(self):
        self.wheel._students = self.dm.current_students
        self._angle = 0
        self.wheel._angle = 0
        self.wheel._highlights = set()
        self.winner_label.setText("")
        self.status_label.setText("✨ 点击「开始转动」")
        self.wheel.update()
        # 清空右侧历史（引擎历史按班级隔离，由 reset_history 负责）
        self.history_list.clear()
        self.hist_count.setText("0")
