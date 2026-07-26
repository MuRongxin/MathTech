"""随机抽人页 — 全屏碰撞弹跳版

动画效果：
1. 名字在整个左侧区域内弹跳碰撞，碰到边缘换名+换色+反弹
2. 停止时名字飞向中央，放大揭示
3. 分组模式多人芯片依次排列
"""
import random

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QSpinBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
from core.random_engine import RandomEngine
# FlowLayout 已迁移至 ui.widgets；保留此 import 以兼容旧的
# `from ui.random_tab import FlowLayout` 引用
from ui.widgets import FlowLayout  # noqa: F401

# Qt 的 QWIDGETSIZE_MAX：setFixedWidth 传入此值即解除固定宽度限制
QWIDGETSIZE_MAX = 16777215

BOUNCE_COLORS = [
    "#e74c3c", "#e67e22", "#f39c12", "#2ecc71", "#1abc9c",
    "#3498db", "#9b59b6", "#e91e63", "#00bcd4", "#ff5722",
    "#16a085", "#c0392b", "#8e44ad", "#2980b9", "#d35400",
]


def _bouncer_style(color: str, size: int = 42) -> str:
    return (
        f"color: {color}; background: transparent; border: none; "
        f"font-size: {size}px; font-weight: bold;"
    )


class BouncingLabel(QLabel):
    """自由漂浮的名字标签"""

    def __init__(self, parent=None):
        super().__init__("准备开始", parent)
        self._color = "#2c3e50"
        self._font_size = 42
        self.setFont(QFont("Microsoft YaHei", 42, QFont.Weight.Bold))
        self.set_style(self._color, self._font_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.adjustSize()

    def set_style(self, color: str, size: int = 42):
        """记录当前颜色/字号并重设样式表（样式表会覆盖 setFont 的字号）"""
        self._color = color
        self._font_size = size
        self.setStyleSheet(_bouncer_style(color, size))

    def move_to(self, x: int, y: int):
        self.move(x, y)

    def fit_width(self, max_w: int):
        """限制最大宽度，长名字逐级缩字号（须改样式表，setFont 无效）"""
        if self.width() <= max_w:
            self.setFixedWidth(self.width())  # 用自身宽度
            return
        # 缩字号直到适配
        for size in range(self._font_size, 16, -4):
            self.set_style(self._color, size)
            self.adjustSize()
            if self.width() <= max_w:
                self.setFixedWidth(self.width())
                return
        self.setFixedWidth(max_w)


class ResultChip(QFrame):
    """被抽中人的芯片"""

    def __init__(self, name: str, count: int, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        colors = ["#1abc9c", "#3498db", "#9b59b6", "#e67e22", "#2ecc71", "#e74c3c"]
        c = random.choice(colors)
        self.setObjectName("result_chip")
        self.setStyleSheet(f"""
            QFrame#result_chip {{
                background-color: white;
                border: 2px solid {c};
                border-radius: 12px;
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(10)

        avatar = QLabel(name[:1] or "?")
        avatar.setFixedSize(34, 34)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        avatar.setObjectName("avatar_lbl")
        avatar.setStyleSheet(
            f"QLabel#avatar_lbl {{ background-color: {c}; color: white; border-radius: 17px; }}"
        )
        layout.addWidget(avatar)

        name_lbl = QLabel(name)
        name_lbl.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        name_lbl.setObjectName("chip_name")
        name_lbl.setStyleSheet("QLabel#chip_name { background-color: transparent; color: #2c3e50; }")
        layout.addWidget(name_lbl)
        layout.addStretch()

        count_lbl = QLabel(f"第 {count} 次")
        count_lbl.setFont(QFont("Microsoft YaHei", 9))
        count_lbl.setObjectName("chip_count")
        count_lbl.setStyleSheet("QLabel#chip_count { background-color: transparent; color: #95a5a6; }")
        layout.addWidget(count_lbl)


class RandomTab(QWidget):
    def __init__(self, dm: DataManager, engine: RandomEngine):
        super().__init__()
        self.dm = dm
        self.engine = engine
        self._is_rolling = False
        self._tick_count = 0

        # 弹跳物理
        self._bx = 0.0
        self._by = 0.0
        self._vx = 0.0
        self._vy = 0.0
        self._speed = 10.0

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------- 左侧：整个活动区域 ----------
        self.stage = QFrame()
        self.stage.setStyleSheet("background: #f5f6fa;")

        # 用 overlay 方式布局固定控件
        stage_layout = QVBoxLayout(self.stage)
        stage_layout.setContentsMargins(40, 24, 40, 24)
        stage_layout.setSpacing(12)
        stage_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标题
        title = QLabel("🎲 随 机 抽 人")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2c3e50; letter-spacing: 4px; background: transparent;")
        stage_layout.addWidget(title)

        # 操作状态指示
        self.status_label = QLabel("✨ 点「开始滚动」抽取")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Microsoft YaHei", 11))
        self.status_label.setStyleSheet("color: #95a5a6; background: transparent;")
        stage_layout.addWidget(self.status_label)

        stage_layout.addStretch()

        # 底部按钮区
        btn_wrapper = QHBoxLayout()
        btn_wrapper.addStretch()

        self.btn_roll = QPushButton("🚀  开 始 滚 动")
        self.btn_roll.setMinimumSize(180, 52)
        self.btn_roll.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        self.btn_roll.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_roll_btn_green()
        self.btn_roll.clicked.connect(self.toggle_roll)
        btn_wrapper.addWidget(self.btn_roll)

        btn_wrapper.addSpacing(16)

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
        btn_wrapper.addWidget(self.btn_reset)

        btn_wrapper.addStretch()
        stage_layout.addLayout(btn_wrapper)

        # 分组设置
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
        stage_layout.addLayout(settings)

        # 结果芯片面板（浮动在中央）
        self.chips_panel = QFrame(self.stage)
        self.chips_panel.setStyleSheet("""
            QFrame#chips_panel {
                background-color: transparent;
                border: none;
            }
        """)
        self.chips_panel.setObjectName("chips_panel")
        self.chips_panel.hide()
        self.chips_layout = FlowLayout(self.chips_panel, 10)
        self.chips_layout.setContentsMargins(16, 14, 16, 14)

        layout.addWidget(self.stage, 3)

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

        # ---------- 浮动名字标签 ----------
        self.bouncer = BouncingLabel(self.stage)
        self._center_bouncer()

        # ---------- 动画定时器 ----------
        self.roll_timer = QTimer(self)
        self.roll_timer.timeout.connect(self._roll_tick)

        # 监听 stage 尺寸变化
        self.stage.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.stage and event.type() == event.Type.Resize:
            if not self._is_rolling:
                self._center_bouncer()
        return False

    def _set_roll_btn_green(self):
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

    def _set_roll_btn_red(self):
        self.btn_roll.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white; border: none; border-radius: 26px;
            }
        """)

    def _center_bouncer(self):
        bw = self.bouncer.width()
        bh = self.bouncer.height()
        sw = self.stage.width()
        sh = self.stage.height()
        cx = (sw - bw) // 2 if sw > bw else 0
        cy = (sh - bh) // 2 if sh > bh else 0
        self._bx = cx
        self._by = cy
        self.bouncer.move_to(cx, cy)

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
        self._tick_count = 0
        self._clear_chips()

        self.btn_roll.setText("⏹  停  止")
        self._set_roll_btn_red()
        self.status_label.setText("🎰 滚动中...")

        # 随机起始位置和方向
        sw = self.stage.width()
        sh = self.stage.height()
        bw = self.bouncer.width()
        bh = self.bouncer.height()
        if sw <= bw or sh <= bh:
            sw, sh = 600, 400

        self._bx = random.uniform(0, max(sw - bw, 1))
        self._by = random.uniform(0, max(sh - bh, 1))

        self._vx = self._speed * 1.6 * random.choice([-1, 1])
        self._vy = self._speed * random.choice([-1, 1])

        # 初始颜色
        color = random.choice(BOUNCE_COLORS)
        self.bouncer.set_style(color)

        self.roll_timer.start(35)

    def _stop_roll(self):
        self._is_rolling = False
        self.roll_timer.stop()

        self.btn_roll.setText("🚀  开 始 滚 动")
        self._set_roll_btn_green()
        self.status_label.setText("✨ 点「开始滚动」抽取")
        self._do_pick()

    def _roll_tick(self):
        students = self.dm.current_students
        if not students:
            return

        sw = self.stage.width()
        sh = self.stage.height()
        bw = self.bouncer.width()
        bh = self.bouncer.height()

        if sw <= bw or sh <= bh:
            return

        # 先用旧位置检测按钮碰撞，再移动，避免穿模
        hit_button, bx, by, flip_vx, flip_vy = self._check_button_collision(
            self._bx, self._by, self._bx + self._vx, self._by + self._vy, bw, bh
        )
        if hit_button:
            self._bx = bx
            self._by = by
            if flip_vx:
                self._vx = -self._vx
            if flip_vy:
                self._vy = -self._vy
        else:
            self._bx += self._vx
            self._by += self._vy

        hit_wall = False

        if self._bx <= 0:
            self._bx = 0
            self._vx = abs(self._vx)
            hit_wall = True
        elif self._bx >= sw - bw:
            self._bx = sw - bw
            self._vx = -abs(self._vx)
            hit_wall = True

        if self._by <= 0:
            self._by = 0
            self._vy = abs(self._vy)
            hit_wall = True
        elif self._by >= sh - bh:
            self._by = sh - bh
            self._vy = -abs(self._vy)
            hit_wall = True

        self.bouncer.move_to(int(self._bx), int(self._by))

        self._tick_count += 1

        hit_any = hit_wall or hit_button

        # 每 3 帧换一次名字（约 100ms），碰到东西必换
        if hit_any or self._tick_count % 3 == 0:
            name = random.choice(students).name
            self.bouncer.setText(name)
            self.bouncer.setFixedWidth(QWIDGETSIZE_MAX)
            self.bouncer.adjustSize()
            if self.bouncer.width() > sw - 4:
                self.bouncer.fit_width(sw - 4)

        # 碰到东西换颜色
        if hit_any:
            color = random.choice(BOUNCE_COLORS)
            self.bouncer.set_style(color)

    def _button_rects(self):
        """返回按钮在 stage 坐标系中的矩形列表（含分组设置控件，避免穿越）"""
        rects = []
        for btn in (self.btn_roll, self.btn_reset, self.spin_group, self.chk_weight):
            r = btn.geometry()
            # geometry 是相对于直接父容器；控件在 stage_layout 内，坐标即 stage 坐标
            rects.append((r.x(), r.y(), r.width(), r.height()))
        return rects

    def _check_button_collision(self, x, y, next_x, next_y, bw, bh):
        """检测下一步是否撞到按钮，返回 (hit, new_x, new_y, flip_vx, flip_vy)"""
        for rx, ry, rw, rh in self._button_rects():
            bx, by2, bw2, bh2 = rx - 4, ry - 4, rw + 8, rh + 8
            nb_rect = (next_x, next_y, bw, bh)
            btn_rect = (bx, by2, bw2, bh2)
            if self._rects_overlap(nb_rect, btn_rect):
                # 判断主碰撞方向
                # 从上方撞入
                if y + bh <= by2 and next_y + bh > by2:
                    return True, next_x, by2 - bh, False, True
                # 从下方撞入
                if y >= by2 + bh2 and next_y < by2 + bh2:
                    return True, next_x, by2 + bh2, False, True
                # 从左撞入
                if x + bw <= bx and next_x + bw > bx:
                    return True, bx - bw, next_y, True, False
                # 从右撞入
                if x >= bx + bw2 and next_x < bx + bw2:
                    return True, bx + bw2, next_y, True, False
                # 角落/对角碰撞，两边都反弹
                return True, x, y, True, True
        return False, next_x, next_y, False, False

    @staticmethod
    def _rects_overlap(a, b):
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

    def _do_pick(self):
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
            QMessageBox.critical(self, "错误", f"抽选失败: {e}")
            return

        if not results:
            return

        if len(results) == 1:
            s = results[0].student
            self.bouncer.set_style("#2c3e50", 52)
            self.bouncer.setText(s.name)
            self.bouncer.setFixedWidth(QWIDGETSIZE_MAX)
            self.bouncer.adjustSize()
            self.bouncer.fit_width(self.stage.width() - 40)
            self._center_bouncer()
            self.status_label.setText(
                f"🎉 ID: {s.id}  |  第 {s.call_count} 次被抽中 ✨"
            )
        else:
            self.bouncer.hide()
            self.bouncer.setText(f"{len(results)} 人")
            self.status_label.setText("")
            for r in results:
                chip = ResultChip(r.student.name, r.student.call_count)
                self.chips_layout.addWidget(chip)
            max_w = int(self.stage.width() * 0.75)
            self.chips_panel.setFixedWidth(max_w)
            self.chips_panel.adjustSize()
            ph = self.chips_panel.sizeHint().height()
            self.chips_panel.setFixedHeight(ph)
            self.chips_panel.move(
                (self.stage.width() - max_w) // 2,
                (self.stage.height() - ph) // 2,
            )
            self.chips_panel.show()

        # 弹跳揭示（bouncer 隐藏时跳过）
        if not self.bouncer.isHidden():
            self._reveal_anim = QPropertyAnimation(self.bouncer, b"geometry")
            rect = self.bouncer.geometry()
            start_rect = rect.translated(0, -25)
            self._reveal_anim.setStartValue(start_rect)
            self._reveal_anim.setEndValue(rect)
            self._reveal_anim.setDuration(500)
            self._reveal_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
            self._reveal_anim.start()

        # 历史
        for r in reversed(results):
            prefix = "🔄 " if r.is_new_cycle else ""
            text = f"{prefix}{r.student.name}  ·  第{r.student.call_count}次"
            self.history_list.insertItem(0, text)
        # 历史保留最近 100 条，超出删最旧
        while self.history_list.count() > 100:
            self.history_list.takeItem(self.history_list.count() - 1)
        self.hist_count.setText(str(self.history_list.count()))

    def _clear_chips(self):
        while self.chips_layout.count():
            item = self.chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.chips_panel.hide()
        self.bouncer.show()

    def reset_history(self):
        self.engine.reset_history(self.dm.current_class)
        self.history_list.clear()
        self.hist_count.setText("0")
        self.bouncer.setText("准备开始")
        self.bouncer.setFixedWidth(QWIDGETSIZE_MAX)
        self.bouncer.adjustSize()
        self.bouncer.set_style("#2c3e50")
        self._center_bouncer()
        self.status_label.setText("✨ 点「开始滚动」抽取")
        self.stage.setStyleSheet("background: #f5f6fa;")
        self._clear_chips()

    def stop_rolling(self):
        """强制停止滚动动画并恢复按钮状态（切换模式/页签/班级时调用）"""
        if not self._is_rolling and not self.roll_timer.isActive():
            return
        self.roll_timer.stop()
        self._is_rolling = False
        self.btn_roll.setText("🚀  开 始 滚 动")
        self._set_roll_btn_green()
        self.status_label.setText("✨ 点「开始滚动」抽取")

    def refresh(self):
        self.bouncer.setText("准备开始")
        self.bouncer.setFixedWidth(QWIDGETSIZE_MAX)
        self.bouncer.adjustSize()
        self.bouncer.set_style("#2c3e50")
        self._center_bouncer()
        self.status_label.setText("✨ 点「开始滚动」抽取")
        self.stage.setStyleSheet("background: #f5f6fa;")
        self._clear_chips()
        # 清空右侧历史（引擎历史按班级隔离，由 reset_history 负责）
        self.history_list.clear()
        self.hist_count.setText("0")
