"""概览页 - 带过渡动画的班级过滤 + 单班详情 + 柱状图

使用 QPropertyAnimation 实现卡片展开/收缩的平滑过渡
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QAbstractAnimation
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.data_manager import DataManager

CLASS_COLORS = ["#1565C0", "#C62828", "#2E7D32", "#F57C00", "#6A1B9A", "#00838F"]


def get_color(i: int) -> str:
    return CLASS_COLORS[i % len(CLASS_COLORS)]


class MetricCard(QFrame):
    def __init__(self, color: str, title: str, value: str, desc: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border-left: 5px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Microsoft YaHei", 10))
        lbl_title.setStyleSheet(f"color: {color}; font-weight: bold;")
        layout.addWidget(lbl_title)

        lbl_value = QLabel(value)
        lbl_value.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        lbl_value.setStyleSheet("color: #2c3e50;")
        layout.addWidget(lbl_value)

        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Microsoft YaHei", 9))
        lbl_desc.setStyleSheet("color: #95a5a6;")
        layout.addWidget(lbl_desc)


class ClassRow(QWidget):
    """一个班级的行，带可动画展开的卡片区域"""
    def __init__(self, class_idx: int, parent=None):
        super().__init__(parent)
        self.class_idx = class_idx
        self._expanded = True
        self._cached_height = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 标题
        self.header = QLabel()
        self.header.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.header.setStyleSheet("padding: 6px 4px;")
        layout.addWidget(self.header)

        # 卡片容器（可动画）
        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(10)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.cards_container)

        # 动画
        self._anim = QPropertyAnimation(self.cards_container, b"maximumHeight")
        self._anim.setDuration(250)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def set_expanded(self, expanded: bool, animate: bool = True, force: bool = False):
        if expanded == self._expanded and not force:
            return
        self._expanded = expanded

        if expanded:
            self.cards_container.setMaximumHeight(16777215)
            target = self.cards_container.sizeHint().height()
            if target > 0:
                self._cached_height = target
            elif self._cached_height > 0:
                target = self._cached_height
            else:
                target = 100
            if animate:
                # 先缩回 0，动画才能可见地展开
                self.cards_container.setMaximumHeight(0)
                current = 0
            else:
                current = target
        else:
            target = 0
            current = self.cards_container.maximumHeight()
            if current == 16777215:
                current = self._cached_height if self._cached_height > 0 else target

        if animate:
            self._anim.stop()
            self._anim.setStartValue(current)
            self._anim.setEndValue(target)
            self._anim.start()
        else:
            self.cards_container.setMaximumHeight(target)

    def update_data(self, name: str, metrics: dict, color: str):
        self.header.setText(
            f"<span style='color:{color};'>📚 {name}</span>  "
            f"<span style='color:#7f8c8d; font-weight:normal;'>({metrics['count']}人, 最近一次)  "
            f"高分{metrics['high']} | 及格{metrics['pass_pct']}% | 低分{metrics['low']} | 均分{metrics['avg']:.1f}</span>"
        )

        # 清空旧卡片
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        data = [
            ("🌟 高分", f"{metrics['high']}人", f"得分率≥80%  ({metrics['high_pct']}%)", color),
            ("✅ 及格", f"{metrics['pass_pct']}%", f"得分率≥60%  ({metrics['pass']}人)", "#27ae60"),
            ("⚠️ 低分", f"{metrics['low']}人", f"得分率<40%  ({metrics['low_pct']}%)", "#e74c3c"),
            ("📐 离散度", f"σ={metrics['std']}", "标准差", "#9b59b6"),
            ("📊 平均分", f"{metrics['avg']:.1f}分", f"最高{metrics.get('max_score', '-')}分", "#34495e"),
        ]
        for title, value, desc, c in data:
            self.cards_layout.addWidget(MetricCard(c, title, value, desc))


class OverviewTab(QWidget):
    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._filter_idx = -1
        self._hover_annot = None
        self._hover_lines = []
        self._hover_dates = []
        self._setup_ui()
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 标题
        title = QLabel("📊 数据概览")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # 过滤按钮
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        self.filter_buttons: list[QPushButton] = []

        btn_all = QPushButton("📋 全部班级")
        btn_all.setCheckable(True)
        btn_all.setChecked(True)
        btn_all.setMinimumHeight(36)
        btn_all.clicked.connect(lambda: self.set_filter(-1))
        filter_layout.addWidget(btn_all)
        self.filter_buttons.append(btn_all)

        for i in range(self.dm.class_count):
            name = self.dm.class_names[i] if i < len(self.dm.class_names) else f"班级{i+1}"
            color = get_color(i)
            btn = QPushButton(f"  {name}")
            btn.setCheckable(True)
            btn.setMinimumHeight(36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {color};
                    color: {color};
                    border-radius: 6px;
                    padding: 6px 16px;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: white;
                }}
            """)
            btn.clicked.connect(lambda checked, idx=i: self.set_filter(idx))
            filter_layout.addWidget(btn)
            self.filter_buttons.append(btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # 班级行容器
        self.rows_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(12)
        layout.addWidget(self.rows_widget)

        self.rows: list[ClassRow] = []
        for i in range(self.dm.class_count):
            row = ClassRow(i)
            self.rows_layout.addWidget(row)
            self.rows.append(row)

        # 柱状图
        chart_title = QLabel("📊 各次考试班级平均分趋势")
        chart_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        chart_title.setStyleSheet("color: #2c3e50; margin-top: 8px;")
        layout.addWidget(chart_title)

        self.fig = Figure(figsize=(10, 4), dpi=100)
        self.fig.patch.set_facecolor("#fafafa")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.refresh()

    def set_filter(self, idx: int):
        self._filter_idx = idx
        for i, btn in enumerate(self.filter_buttons):
            btn.setChecked(i == idx + 1)

        # 动画展开/收缩
        for i, row in enumerate(self.rows):
            row.set_expanded(idx == -1 or idx == i, animate=True)

        self._draw_chart()

    def _calc_metrics(self, students):
        """计算最近一次考试的班级指标，得分率 = 实际分 / 理论满分"""
        latest_dt = self.dm.dates[-1] if self.dm.dates else None
        if not latest_dt:
            return {"high": 0, "high_pct": 0, "pass": 0, "pass_pct": 0,
                    "low": 0, "low_pct": 0, "std": 0, "avg": 0, "count": 0, "max_score": "--"}

        scores = []
        for s in students:
            score_map = {d: float(v) for d, v in (s.scores_full or s.scores or [])}
            if latest_dt in score_map:
                scores.append(score_map[latest_dt])
        if not scores:
            return {"high": 0, "high_pct": 0, "pass": 0, "pass_pct": 0,
                    "low": 0, "low_pct": 0, "std": 0, "avg": 0, "count": 0, "max_score": "--"}

        # 理论满分：逐题 max_score 加总
        meta = self.dm.get_exam_meta(latest_dt)
        if meta.questions:
            theoretical_max = sum(q.max_score for q in meta.questions)
        else:
            theoretical_max = max(scores) if scores else 100.0

        import statistics
        if theoretical_max > 0:
            rates = [sc / theoretical_max for sc in scores]
        else:
            rates = [0.0] * len(scores)

        high = sum(1 for r in rates if r >= 0.80)
        passed = sum(1 for r in rates if r >= 0.60)
        low = sum(1 for r in rates if r < 0.40)
        avg = statistics.mean(scores)
        std = statistics.stdev(scores) if len(scores) > 1 else 0
        return {
            "high": high, "high_pct": round(high / len(scores) * 100, 1),
            "pass": passed, "pass_pct": round(passed / len(scores) * 100, 1),
            "low": low, "low_pct": round(low / len(scores) * 100, 1),
            "std": round(std, 2), "avg": round(avg, 1),
            "count": len(scores), "max_score": round(theoretical_max, 1)
        }

    def refresh(self):
        all_metrics = []
        for ci in range(self.dm.class_count):
            students = self.dm.students[ci][1]  # 固定用满分卷
            all_metrics.append(self._calc_metrics(students))

        needs_finalize = False
        for i, row in enumerate(self.rows):
            name = self.dm.class_names[i] if i < len(self.dm.class_names) else f"班级{i+1}"
            row.update_data(name, all_metrics[i], get_color(i))
            should_expand = self._filter_idx == -1 or self._filter_idx == i
            if should_expand:
                # 先放开限制让卡片可见，延迟再修正高度
                row.cards_container.setMaximumHeight(16777215)
                row._expanded = True
                needs_finalize = True
            else:
                row.set_expanded(False, animate=False, force=True)

        # 延迟修正展开行的高度（确保布局已完成）
        if needs_finalize:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._finalize_expanded_rows)

        # 折线图
        self._draw_chart()

    def _draw_chart(self):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor("#fafafa")

        dates = self.dm.dates
        x = list(range(len(dates)))
        markers = ["o", "s", "D", "^", "v", "p"]
        filter_on = self._filter_idx >= 0

        for ci in range(self.dm.class_count):
            students = self.dm.students[ci][1]
            avgs = []
            for dt in dates:
                vals = []
                for s in students:
                    # date-keyed lookup 避免缺考错位
                    score_map = {d: float(v) for d, v in (s.scores_full or s.scores or [])}
                    if dt in score_map:
                        vals.append(score_map[dt])
                avgs.append(round(sum(vals) / len(vals), 1) if vals else 0.0)

            name = self.dm.class_names[ci] if ci < len(self.dm.class_names) else f"班级{ci+1}"
            color = get_color(ci)
            marker = markers[ci % len(markers)]
            if filter_on and ci != self._filter_idx:
                # 淡化非选中班级
                ax.plot(x, avgs, label=name, color=color, linewidth=1.0, alpha=0.15,
                        marker=marker, markersize=2, markerfacecolor="white", markeredgewidth=1)
            else:
                ax.plot(x, avgs, label=name, color=color, linewidth=2.5,
                        marker=marker, markersize=4, markerfacecolor="white", markeredgewidth=2)

        ax.set_ylabel("平均分", fontsize=12, color="#555")
        ax.set_title("各次考试班级平均分趋势", fontsize=14, fontweight="bold", color="#2c3e50", pad=15)
        ax.legend(loc="upper right", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.3, color="#999")
        ax.set_xticks([])
        ax.tick_params(colors="#666")
        ax.set_xlim(-0.5, len(dates) - 0.5)
        for spine in ax.spines.values():
            spine.set_color("#ddd")

        self._hover_dates = dates
        self._hover_lines = ax.lines
        self._hover_annot = None
        self.fig.tight_layout()
        self.canvas.draw()

    def _finalize_expanded_rows(self):
        """延迟修正展开行的高度（布局就绪后 sizeHint 才准确）"""
        for row in self.rows:
            if row._expanded:
                row.set_expanded(True, animate=False, force=True)

    def _on_hover(self, event):
        if not event.inaxes or not self._hover_lines or not self._hover_dates:
            if self._hover_annot:
                self._hover_annot.set_visible(False)
                self.canvas.draw_idle()
            return

        ax = event.inaxes
        best_dist = float("inf")
        best_idx = -1
        best_line = None

        for line in self._hover_lines:
            xdata, ydata = line.get_data()
            if len(xdata) == 0:
                continue
            # 转换为像素坐标计算实际距离
            pts = ax.transData.transform(list(zip(xdata, ydata)))
            for i, (px, py) in enumerate(pts):
                dist = ((px - event.x) ** 2 + (py - event.y) ** 2) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    best_idx = i
                    best_line = line

        if best_dist > 12 or best_idx < 0 or best_line is None:
            if self._hover_annot:
                self._hover_annot.set_visible(False)
                self.canvas.draw_idle()
            return

        xdata, ydata = best_line.get_data()
        date_str = self._hover_dates[best_idx]
        score = ydata[best_idx]
        xy = (xdata[best_idx], score)

        if self._hover_annot is None:
            self._hover_annot = ax.annotate(
                "", xy=xy, xytext=(12, 12),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#2c3e50", edgecolor="none", alpha=0.92),
                color="white", fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.5),
            )
        else:
            self._hover_annot.xy = xy

        self._hover_annot.set_text(f"{date_str}\n平均分 {score:.1f}")
        self._hover_annot.set_visible(True)
        self.canvas.draw_idle()
